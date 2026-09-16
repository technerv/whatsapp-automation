from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from google.cloud import dialogflow_v2 as dialogflow
import os
import logging
import requests
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated

from .models import Workflow
from .serializers import WorkflowSerializer
from .services import publish_event
from inventory.models import Product

logger = logging.getLogger(__name__)


class WorkflowViewSet(viewsets.ModelViewSet):
    serializer_class = WorkflowSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Workflow.objects.filter(business=self.request.user.business)

    def perform_create(self, serializer):
        if not self.request.user.business_id:
            raise PermissionDenied('Your account is not associated with a business.')
        serializer.save(business=self.request.user.business, created_by=self.request.user)

    @action(detail=True, methods=['post'])
    def publish(self, request, pk=None):
        workflow = self.get_object()
        workflow.status = 'active'
        workflow.version += 1
        workflow.save(update_fields=['status', 'version', 'updated_at'])
        return Response(self.get_serializer(workflow).data)

    @action(detail=True, methods=['post'])
    def pause(self, request, pk=None):
        workflow = self.get_object()
        workflow.status = 'paused'
        workflow.save(update_fields=['status', 'updated_at'])
        return Response(self.get_serializer(workflow).data)


class AutomationEventView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if not request.user.business_id:
            raise PermissionDenied('Your account is not associated with a business.')
        event_type = request.data.get('event_type', '')
        idempotency_key = request.headers.get('Idempotency-Key', request.data.get('idempotency_key', ''))
        if not event_type or not idempotency_key:
            return Response({'detail': 'event_type and Idempotency-Key are required.'}, status=400)
        event, created = publish_event(
            business=request.user.business,
            event_type=event_type,
            payload=request.data.get('payload', {}),
            idempotency_key=idempotency_key,
            aggregate_type=request.data.get('aggregate_type', ''),
            aggregate_id=request.data.get('aggregate_id', ''),
        )
        return Response({'id': event.id, 'status': event.status, 'created': created}, status=201 if created else 200)

class DialogflowWebhook(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
            data = request.data
            text = data.get('text', '').strip().lower()
            business = request.user.business

            if not business:
                raise PermissionDenied('Your account is not associated with a business.')

            if text == 'products':
                products = Product.objects.filter(business=business).order_by('name')[:20]
                if not products:
                    return Response({'fulfillmentText': 'Your catalogue is empty. Add products to get started.'})
                product_list = '\n'.join(
                    f'{product.name} - {product.price} {business.currency}'
                    for product in products
                )
                return Response({'fulfillmentText': f'Here are your products:\n{product_list}'})

            if text.startswith('buy '):
                return Response({'fulfillmentText': 'Order creation is available through the cart checkout flow. Tell me the product name and quantity to continue.'})

            session_id = data.get('session', 'default_session_id')
            project_id = os.environ.get('DIALOGFLOW_PROJECT_ID')
            ai_provider = os.environ.get('AI_PROVIDER', 'local').lower()
            if ai_provider != 'dialogflow' or not project_id:
                return Response({'fulfillmentText': 'I am ready to help with products, orders, and payments. Try typing "products".'})
            session_client = dialogflow.SessionsClient()
            session = session_client.session_path(project_id, session_id)
            text_input = dialogflow.types.TextInput(text=data.get('text'), language_code='en-US')
            query_input = dialogflow.types.QueryInput(text=text_input)
            response = session_client.detect_intent(session=session, query_input=query_input)

            return Response(
                {'fulfillmentText': response.query_result.fulfillment_text},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            logger.error(f"Error in Dialogflow webhook: {e}")
            return Response(
                {'detail': 'The AI assistant is temporarily unavailable.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )