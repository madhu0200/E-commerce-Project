from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import *
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.exceptions import AuthenticationFailed

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
            'password',
            'role'
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





class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        # Authenticate email & password with base SimpleJWT method
        data = super().validate(attrs)

        # Security Check: Block login if user is not email-verified
        if not self.user.is_verified:
            raise AuthenticationFailed(
                {"error": "Your email is not verified. Please verify your email before logging in."}
            )

        # Security Check: Block login if user account is deactivated
        if not self.user.is_active:
            raise AuthenticationFailed(
                {"error": "Your account has been deactivated. Please contact support."}
            )

        # Add custom fields to the JSON response

        data['email'] = self.user.email
        data['username'] = self.user.username
        data['role'] = self.user.role


        return data



User = get_user_model()


class RequestPasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("No registered user found with this email address.")
        return value


class ResetPasswordConfirmSerializer(serializers.Serializer):
    uidb64 = serializers.CharField(write_only=True)
    token = serializers.CharField(write_only=True)
    new_password = serializers.CharField(min_length=8, write_only=True)

    def validate_new_password(self, value):
        # Add extra complexity checks if needed
        return value

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, min_length=8, write_only=True)

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Your current password was entered incorrectly.")
        return value