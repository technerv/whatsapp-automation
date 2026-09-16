from django.conf import settings
from django.db import transaction
from django.http import JsonResponse
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from .models import Conversation, WhatsAppAccount, WhatsAppMessage, WebhookEvent
from .serializers import ConversationSerializer, WhatsAppMessageSerializer
from crm.models import Customer

class ConversationViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Conversation.objects.filter(business=self.request.user.business).select_related('customer').order_by('-last_message_at')

class WhatsAppMessageViewSet(viewsets.ModelViewSet):
    serializer_class = WhatsAppMessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        conversation_id = self.kwargs['conversation_pk']
        return WhatsAppMessage.objects.filter(conversation__id=conversation_id, conversation__business=self.request.user.business).order_by('timestamp')

    def perform_create(self, serializer):
        conversation_id = self.kwargs['conversation_pk']
        conversation = Conversation.objects.get(id=conversation_id, business=self.request.user.business)
        serializer.save(
            conversation=conversation,
            direction='outbound',
            whatsapp_message_id=f'local-{timezone.now().timestamp()}-{conversation.id}',
            timestamp=timezone.now(),
        )


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def whatsapp_webhook(request):
    if request.method == 'GET':
        mode = request.query_params.get('hub.mode')
        token = request.query_params.get('hub.verify_token')
        challenge = request.query_params.get('hub.challenge')
        if mode == 'subscribe' and token == getattr(settings, 'WHATSAPP_VERIFY_TOKEN', None):
            return Response(challenge, status=status.HTTP_200_OK)
        return Response({'detail': 'Invalid verification request.'}, status=status.HTTP_403_FORBIDDEN)

    payload = request.data
    message_ids = [
        message.get('id')
        for entry in payload.get('entry', [])
        for change in entry.get('changes', [])
        for message in change.get('value', {}).get('messages', [])
        if message.get('id')
    ]
    external_event_id = message_ids[0] if message_ids else payload.get('id')
    if not external_event_id:
        return Response({'detail': 'Webhook event has no message ID.'}, status=status.HTTP_400_BAD_REQUEST)
    event, created = WebhookEvent.objects.get_or_create(
        external_event_id=external_event_id,
        defaults={'payload': payload},
    )
    if not created and event.status == 'processed':
        return Response({'status': 'already_processed'})

    try:
        with transaction.atomic():
            for entry in payload.get('entry', []):
                for change in entry.get('changes', []):
                    value = change.get('value', {})
                    metadata = value.get('metadata', {})
                    account = WhatsAppAccount.objects.get(phone_number_id=metadata.get('phone_number_id'))
                    for message in value.get('messages', []):
                        message_id = message.get('id')
                        if not message_id or WhatsAppMessage.objects.filter(whatsapp_message_id=message_id).exists():
                            continue
                        wa_id = (value.get('contacts') or [{}])[0].get('wa_id') or message.get('from')
                        contact_name = ((value.get('contacts') or [{}])[0].get('profile') or {}).get('name', wa_id)
                        customer, _ = Customer.objects.get_or_create(
                            business=account.business,
                            phone_number=wa_id,
                            defaults={'name': contact_name},
                        )
                        conversation, _ = Conversation.objects.get_or_create(
                            business=account.business,
                            customer=customer,
                        )
                        text = (message.get('text') or {}).get('body', '')
                        WhatsAppMessage.objects.create(
                            conversation=conversation,
                            whatsapp_message_id=message_id,
                            direction='inbound',
                            content=text,
                            timestamp=timezone.now(),
                        )
                        conversation.save(update_fields=['last_message_at'])
            event.status = 'processed'
            event.processed_at = timezone.now()
            event.save(update_fields=['status', 'processed_at'])
    except Exception as exc:
        event.status = 'failed'
        event.error = str(exc)
        event.save(update_fields=['status', 'error'])
        return Response({'detail': 'Webhook processing failed.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return Response({'status': 'processed'}, status=status.HTTP_200_OK)