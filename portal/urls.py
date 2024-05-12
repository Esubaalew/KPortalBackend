from django.urls import path, include
from rest_framework import routers
from .views import (
    UserViewSet,
    ResourceViewSet,
    UserSignUpView,
    UserSignInView,
    logged_in_user,
    GetUserByUsername, LikeViewSet, CommentViewSet,
    UserResourceListView,
    FollowViewSet, UserSearchView, ResourceSearchView, PasswordResetRequestAPIView, PasswordResetConfirmAPIView,
    GitHubRepoSearchAPIView,
    LanguageViewSet
)

router = routers.DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'resources', ResourceViewSet, basename='resource')
router.register(r'likes', LikeViewSet)
router.register(r'comments', CommentViewSet)
router.register(r'follows', FollowViewSet)
router.register(r'languages', LanguageViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('signup/', UserSignUpView.as_view(), name='user-signup'),
    path('signin/', UserSignInView.as_view(), name='user-signin'),
    path('loggedin/', logged_in_user, name='logged-in-user'),
    path('user/<str:username>/', GetUserByUsername.as_view(), name='get-user-by-username'),
    path('user/<str:username>/resources/', UserResourceListView.as_view(), name='user-resources'),
    path('follow/', FollowViewSet.as_view({'post': 'follow_user'}), name='follow-user'),
    path('unfollow/', FollowViewSet.as_view({'post': 'unfollow_user'}), name='unfollow-user'),
    path('like/<int:pk>/', ResourceViewSet.as_view({'post': 'like'}), name='resource-like'),
    path('unlike/<int:pk>/', ResourceViewSet.as_view({'post': 'unlike'}), name='resource-unlike'),
    path('comment/<int:pk>/', ResourceViewSet.as_view({'post': 'comment'}), name='resource-comment'),
    path('account/search/', UserSearchView.as_view(), name='user-search'),
    path('res/search/', ResourceSearchView.as_view(), name='resource_search'),
    path('password-reset/', PasswordResetRequestAPIView.as_view(), name='password_reset_request'),
    path('password-reset-confirm/<str:uidb64>/<str:token>/', PasswordResetConfirmAPIView.as_view(),
         name='password_reset_confirm'),
    path('github/repos/', GitHubRepoSearchAPIView.as_view(), name='github_repo_search'),
]
