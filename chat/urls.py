from django.urls import path, include
from rest_framework import routers
from .views import ChatRoomViewSet, MessageViewSet

router = routers.DefaultRouter()
router.register(r'chatrooms', ChatRoomViewSet)
router.register(r'messages', MessageViewSet)

urlpatterns = [
    path('', include(router.urls))
]
