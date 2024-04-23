from django.shortcuts import render
from .models import CustomUser, LinkResource
from .serializers import CustomUserSerializer, LinkResourceSerializer, FileResourceSerializer
from rest_framework import viewsets


class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer


class LinkResourceViewSet(viewsets.ModelViewSet):
    queryset = LinkResource.objects.all()
    serializer_class = LinkResourceSerializer


class FileResourceViewSet(viewsets.ModelViewSet):
    queryset = LinkResource.objects.all()
    serializer_class = FileResourceSerializer
