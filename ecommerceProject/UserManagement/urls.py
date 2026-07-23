
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
 path('auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
 path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
