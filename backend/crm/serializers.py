from rest_framework import serializers
from .models import Customer

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ('id', 'business', 'name', 'email', 'phone_number', 'created_at', 'updated_at')
        read_only_fields = ('id', 'business', 'created_at', 'updated_at')

    def validate_phone_number(self, phone_number):
        business = self.context['request'].user.business
        existing = Customer.objects.filter(
            business=business,
            phone_number=phone_number,
        )
        if self.instance:
            existing = existing.exclude(pk=self.instance.pk)
        if existing.exists():
            raise serializers.ValidationError('A customer with this phone number already exists.')
        return phone_number