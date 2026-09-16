from rest_framework import serializers
from .models import Payment

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ('id', 'business', 'invoice', 'amount', 'phone_number', 'transaction_id',
                  'merchant_request_id', 'checkout_request_id', 'callback_payload',
                  'status', 'created_at', 'updated_at')
        read_only_fields = fields