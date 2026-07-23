
from django.contrib import admin
from django.urls import path
from .views import *
from django.urls import path
from rest_framework_simplejwt.views import (
 TokenObtainPairView,
 TokenRefreshView,
)

urlpatterns = [
 path('register/',Register.as_view()),
 path('auth/token/generate/', LoginView.as_view(), name='token_obtain_pair'),
 path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
 path('auth/verify-email/<str:uidb64>/<str:token>/', VerifyEmailView.as_view(), name='verify_email'),
 path('auth/password-reset/', RequestPasswordResetView.as_view(), name='password_reset_request'),
 path('auth/reset-password-confirm/', ResetPasswordConfirmView.as_view(), name='password_reset_confirm'),

 path('auth/change-password/', ChangePasswordView.as_view(), name='change_password'),
]
