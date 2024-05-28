from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import GPTView

urlpatterns = [
   path('', GPTView.as_view(), name='gpt'),
]