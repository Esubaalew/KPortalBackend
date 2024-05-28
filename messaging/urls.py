# messaging/urls.py

from django.urls import path
from . import views
from .views import GroupMembers, SendEmailView

urlpatterns = [
    path('groups/', views.GroupListCreate.as_view(), name='group-list-create'),
    path('groups/<int:pk>/', views.GroupDetail.as_view(), name='group-detail'),
    path('messages/', views.MessageListCreate.as_view(), name='message-list-create'),
    path('messages/group/<int:group_id>/', views.MessageList.as_view(), name='group-message-list'),
    path('messages/private/<int:recipient_id>/', views.MessageList.as_view(), name='private-message-list'),
    path('private-chats/', views.AllPrivateChats.as_view(), name='all-private-chats'),
    path('group/<int:group_id>/members/', GroupMembers.as_view(), name='group-members'),
    path('send-email/', SendEmailView.as_view(), name='send-email'),
]
