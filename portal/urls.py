from django.urls import path, include
from rest_framework import routers
from .views import (
    UserViewSet,
    ResourceViewSet,
    UserSignUpView,
    UserSignInView,
    logged_in_user,
    GetUserByUsername

)

router = routers.DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'resources', ResourceViewSet, basename='resource')

urlpatterns = [
    path('', include(router.urls)),
    path('signup/', UserSignUpView.as_view(), name='user-signup'),
    path('signin/', UserSignInView.as_view(), name='user-signin'),
    path('loggedin/', logged_in_user, name='logged-in-user'),
    path('user/<str:username>/', GetUserByUsername.as_view(), name='get-user-by-username'),

]
