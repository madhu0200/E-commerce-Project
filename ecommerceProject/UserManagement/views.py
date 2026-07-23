from django.core.mail import send_mail
from django.shortcuts import render
from django.utils.encoding import force_bytes, force_str
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.status import *
from rest_framework.generics import get_object_or_404
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode

from .serializers import *
from .models import *

from .models import *
# Create your views here.


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import UserSerializer
from .models import Users
from .tokens import account_activation_token


class Register(APIView):
    def get(self, request):
        return Response({"msg": "register endpoint ready"}, status=status.HTTP_200_OK)

    def post(self, request):
        email = request.data.get("email")

        if Users.objects.filter(email=email).exists():
            return Response(
                {"error": f"User with email '{email}' already exists."},
                status=status.HTTP_409_CONFLICT
            )

        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()

            # Generate token and UID
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = account_activation_token.make_token(user)

            # Build verification URL
            verification_link = f"{settings.FRONTEND_URL}/users/auth/verify-email/{uid}/{token}/"

            # Send Email
            subject = "Verify Your Email Address"
            message = f"Hi {user.first_name or user.username},\n\nPlease click the link below to verify your account:\n\n{verification_link}\n\nThank you!"

            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL if hasattr(settings,
                                                                  'DEFAULT_FROM_EMAIL') else 'noreply@ecommerce.com',
                recipient_list=[user.email],
                fail_silently=False,
            )

            return Response(
                {"msg": "User registered successfully! Please check your email to verify your account."},
                status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyEmailView(APIView):
    def get(self, request, uidb64, token):
        try:
            # Decode the user ID
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = Users.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, Users.DoesNotExist):
            user = None

        if user is not None and account_activation_token.check_token(user, token):
            if user.is_verified:
                return Response(
                    {"msg": "Email is already verified."},
                    status=status.HTTP_200_OK
                )

            # Mark account as verified
            user.is_verified = True
            user.save()
            return Response(
                {"msg": "Email verified successfully! You can now log in."},
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {"error": "Verification link is invalid or has expired."},
                status=status.HTTP_400_BAD_REQUEST
            )