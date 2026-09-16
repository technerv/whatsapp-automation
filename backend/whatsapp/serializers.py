from rest_framework import serializers
from .models import Conversation, WhatsAppMessage
from crm.serializers import CustomerSerializer

class WhatsAppMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = WhatsAppMessage
        fields = ('id', 'conversation', 'whatsapp_message_id', 'direction', 'content', 'status', 'timestamp', 'created_at')
        read_only_fields = ('id', 'conversation', 'whatsapp_message_id', 'direction', 'status', 'created_at')

class ConversationSerializer(serializers.ModelSerializer):
    customer = CustomerSerializer()
    last_message = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = ('id', 'customer', 'assigned_to', 'status', 'unread_count', 'last_message_at', 'last_message')
        read_only_fields = ('id', 'customer', 'last_message_at', 'last_message')

    def get_last_message(self, obj):
        last_message = obj.messages.order_by('-timestamp').first()
        if last_message:
            return WhatsAppMessageSerializer(last_message).data
        return None