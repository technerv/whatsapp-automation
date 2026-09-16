from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.db import transaction
from .models import Business, Membership

User = get_user_model()

class BusinessSerializer(serializers.ModelSerializer):
    class Meta:
        model = Business
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
    business_name = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = ('id', 'email', 'password', 'first_name', 'last_name', 'business_name')
        extra_kwargs = {'password': {'write_only': True}}

    @transaction.atomic
    def create(self, validated_data):
        business_name = validated_data.pop('business_name', None)
        user = User.objects.create_user(**validated_data)

        if business_name:
            business = Business.objects.create(name=business_name, email=user.email)
            user.business = business
            user.save(update_fields=['business'])
            Membership.objects.create(
                business=business,
                user=user,
                role=Membership.Role.OWNER,
            )

        return user

class CurrentUserSerializer(serializers.ModelSerializer):
    business = BusinessSerializer()

    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'business')