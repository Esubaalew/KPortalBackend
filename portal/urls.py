from django.urls import path, include
from rest_framework import routers
from .views import UserViewSet, ResourceViewSet

router = routers.DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'resources', ResourceViewSet, basename='resource')

urlpatterns = [
    path('', include(router.urls)),
]