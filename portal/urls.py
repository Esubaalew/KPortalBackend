from django.urls import path, include
from rest_framework import routers
from .views import UserViewSet, LinkResourceViewSet, FileResourceViewSet

router = routers.DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'link-resources', LinkResourceViewSet, basename='link-resource')
router.register(r'file-resources', FileResourceViewSet, basename='file-resource')


urlpatterns = [
    path('', include(router.urls)),
]
