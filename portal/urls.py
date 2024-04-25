from django.urls import path, include
from rest_framework import routers
from .views import UserViewSet, ResourceViewSet, get_file_metadata

router = routers.DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'resources', ResourceViewSet, basename='resource')

urlpatterns = [
    path('', include(router.urls)),
    path('metadata/<int:file_id>/', get_file_metadata, name='file-metadata'),
]