from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.status import *
from rest_framework.generics import get_object_or_404
from .serializers import *
from .models import *

from .models import *
# Create your views here.


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import UserSerializer
from .models import Users


class Register(APIView):
    def get(self, request):
        return Response({"msg": "register endpoint ready"}, status=status.HTTP_200_OK)

    def post(self, request):
        email = request.data.get("email")

        # Check if user already exists using .exists()
        if Users.objects.filter(email=email).exists():
            return Response(
                {"msg": f"User with email: {email} already exists."},
                status=status.HTTP_409_CONFLICT
            )

        # Pass request payload to serializer
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"msg": "User created successfully", "data": serializer.data},
                status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)