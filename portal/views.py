from django.contrib.auth import authenticate, login
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, action, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import CustomUserSerializer, ResourceSerializer, UserSerializer, UserSignInSerializer
from rest_framework import viewsets, status, generics, permissions
from PyPDF2 import PdfReader
from .models import Resource, CustomUser
import os
from docx import Document


class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer


class ResourceViewSet(viewsets.ModelViewSet):
    queryset = Resource.objects.all()
    serializer_class = ResourceSerializer

    @action(detail=True, methods=['get'])
    def metadata(self, request, pk=None):
        try:
            file_obj = self.get_object().file
            metadata = {'type': os.path.splitext(file_obj.name)[1][1:].upper(),
                        'size': round(file_obj.size / (1024 * 1024), 2)}

            if file_obj.name.endswith('.pdf'):
                with open(file_obj.path, 'rb') as file:
                    pdf = PdfReader(file)
                    metadata['title'] = pdf.docinfo.title if hasattr(pdf,
                                                                     'docinfo') and pdf.docinfo else os.path.basename(
                        file_obj.name)
            elif file_obj.name.endswith('.docx'):
                doc = Document(file_obj)
                metadata['title'] = doc.core_properties.title if doc.core_properties.title else os.path.basename(
                    file_obj.name)

            return Response(metadata)
        except Resource.DoesNotExist:
            return Response({'error': 'Resource not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserSignUpView(generics.CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

    def perform_create(self, serializer):
        user = serializer.save()
        if user:
            refresh = RefreshToken.for_user(user)
            # Return tokens as JSON data along with HTTP 201 Created
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_201_CREATED)


class UserSignInView(generics.CreateAPIView):
    serializer_class = UserSignInSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def logged_in_user(request):
    user = request.user
    user_data = {
        'username': user.username,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name

    }
    return Response(user_data)


class GetUserByUsername(APIView):
    def get(self, request, username):
        try:
            user = CustomUser.objects.get(username=username)
            serializer = CustomUserSerializer(user)
            return Response(serializer.data)
        except CustomUser.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
