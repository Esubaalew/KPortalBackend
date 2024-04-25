from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from .serializers import CustomUserSerializer, ResourceSerializer
from rest_framework import viewsets
from PyPDF2 import PdfReader
from .models import Resource, CustomUser
import os


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

            return Response(metadata)
        except Resource.DoesNotExist:
            return Response({'error': 'Resource not found'}, status=404)
        except Exception as e:
            return Response({'error': str(e)}, status=500)
