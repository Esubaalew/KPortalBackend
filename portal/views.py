from django.shortcuts import render
from .models import CustomUser
from .serializers import CustomUserSerializer
from rest_framework import viewsets


class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
