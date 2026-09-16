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
    def post(self, request, *args, **kwargs):
        try:
            data = request.data
            text = data.get('text', '').lower()

            if text == 'products':
                # Fetch product list from the commerce API
                # This assumes the backend is running on the default port 8000
                response = requests.get('http://localhost:8000/api/commerce/products/')
                if response.status_code == 200:
                    products = response.json()
                    product_list = "\n".join([f"{p['id']}: {p['name']} - KES {p['price']}" for p in products])
                    return Response({'fulfillmentText': f"Here are our products:\n{product_list}"})
                else:
                    return Response({'fulfillmentText': "Sorry, I couldn't fetch the products right now."})

            elif text.startswith('buy '):
                product_id = text.split(' ')[1]
                phone_number = data.get('session') # Assuming the session ID is the user's phone number

                # Initiate payment
                response = requests.post('http://localhost:8000/api/commerce/initiate-payment/', data={
                    'product_id': product_id,
                    'phone_number': phone_number
                })

                if response.status_code == 200:
                    return Response({'fulfillmentText': "Thank you! You will receive a prompt on your phone to complete the payment."})
                else:
                    return Response({'fulfillmentText': "Sorry, I couldn't process your order right now."})

            # If it's not a commerce command, proceed with Dialogflow
            session_id = data.get('session', 'default_session_id')
            project_id = os.environ.get('DIALOGFLOW_PROJECT_ID')
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
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )