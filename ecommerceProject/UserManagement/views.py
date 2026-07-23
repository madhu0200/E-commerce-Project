
from .tokens import account_activation_token
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import *
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated


from .models import Users
from .serializers import RequestPasswordResetSerializer, ResetPasswordConfirmSerializer


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





class LoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            # Handle invalid credentials / custom authentication exceptions
            return Response(
                {"error": str(e.detail) if hasattr(e, 'detail') else "Invalid email or password."},
                status=status.HTTP_401_UNAUTHORIZED
            )

        return Response(serializer.validated_data, status=status.HTTP_200_OK)



token_generator = PasswordResetTokenGenerator()


class RequestPasswordResetView(APIView):
    """Generates a password reset token and emails the link."""
    def post(self, request):
        serializer = RequestPasswordResetSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            user = Users.objects.get(email=email)

            # Generate token and base64-encoded User ID
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = token_generator.make_token(user)

            # Build reset link for Front-end or API client
            frontend_url = getattr(settings, 'FRONTEND_URL', 'http://127.0.0.1:8000')
            reset_link = f"{frontend_url}/users/auth/reset-password-confirm/{uid}/{token}/"

            # Send Email
            send_mail(
                subject="Password Reset Request",
                message=f"Hi {user.first_name or user.username},\n\nClick the link below to reset your password:\n\n{reset_link}\n\nIf you did not request this, please ignore this email.",
                from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@ecommerce.com'),
                recipient_list=[user.email],
                fail_silently=False,
            )

            return Response(
                {"msg": "Password reset link has been sent to your email."},
                status=status.HTTP_200_OK
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ResetPasswordConfirmView(APIView):
    """Validates token and sets a new password."""
    def post(self, request):
        serializer = ResetPasswordConfirmSerializer(data=request.data)
        if serializer.is_valid():
            uidb64 = serializer.validated_data['uidb64']
            token = serializer.validated_data['token']
            new_password = serializer.validated_data['new_password']

            try:
                uid = force_str(urlsafe_base64_decode(uidb64))
                user = Users.objects.get(pk=uid)
            except (TypeError, ValueError, OverflowError, Users.DoesNotExist):
                user = None

            if user is not None and token_generator.check_token(user, token):
                # Set hashed password & save
                user.set_password(new_password)
                user.save()
                return Response(
                    {"msg": "Password has been reset successfully. You can now log in with your new password."},
                    status=status.HTTP_200_OK
                )

            return Response(
                {"error": "Invalid or expired reset token."},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)





class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]  # Ensures user MUST be logged in

    def post(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data,
            context={'request': request}
        )
        if serializer.is_valid():
            user = request.user
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return Response(
                {"msg": "Password updated successfully!"},
                status=status.HTTP_200_OK
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

