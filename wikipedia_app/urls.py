from django.urls import path
from .views import get_wikipedia_article, search_wikipedia

urlpatterns = [
    path('article/<str:title>/', get_wikipedia_article, name='get_wikipedia_article'),
    path('search/<str:query>/', search_wikipedia, name='search_wikipedia'),
]
