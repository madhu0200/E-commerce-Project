from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import *

User = get_user_model()


# 1. User Serializer
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'phone_number',
            'role',
            'is_active',
            'is_verified',
            'created_at',
            'updated_at',
            'password'
        ]
        read_only_fields = ['id', 'is_verified', 'created_at', 'updated_at']
        extra_kwargs = {
            'password': {'write_only': True}  # Protect password from GET requests
        }

    def create(self, validated_data):
        user = Users.objects.create_user(**validated_data)
        return user


# 2. Customer Address Serializer
class CustomerAddressSerializer(serializers.ModelSerializer):
    # Pass user automatically from request context or restrict choices
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = CustomerAddress
        fields = [
            'id',
            'user',
            'full_name',
            'phone_number',
            'door_no',
            'street',
            'landmark',
            'city',
            'state',
            'pincode',
            'country',
            'address_type',
            'is_default',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']


# 3. Seller Address Serializer
class SellerAddressSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = SellerAddress
        fields = [
            'id',
            'user',
            'company_name',
            'contact_person',
            'phone_number',
            'door_no',
            'street',
            'landmark',
            'city',
            'state',
            'pincode',
            'country',
            'purpose',
            'is_primary'
        ]
        read_only_fields = ['id']