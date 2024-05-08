from django.contrib.auth import authenticate, login
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, action, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import CustomUserSerializer, ResourceSerializer, UserSerializer, UserSignInSerializer, LikeSerializer, \
    CommentSerializer, FollowSerializer
from rest_framework import viewsets, status, generics, permissions
from PyPDF2 import PdfReader
from .models import Resource, CustomUser, Like, Comment, Follow
import os
from docx import Document


class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    @action(detail=True, methods=['get'])
    def followers(self, request, pk=None):
        user = self.get_object()
        followers = user.followers.all()
        serializer = FollowSerializer(followers, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def following(self, request, pk=None):
        user = self.get_object()
        following = user.following.all()
        serializer = FollowSerializer(following, many=True)
        return Response(serializer.data)


class ResourceViewSet(viewsets.ModelViewSet):
    queryset = Resource.objects.select_related('owner').prefetch_related('likes', 'comments')
    serializer_class = ResourceSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

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
            elif file_obj.name.endswith('.docx'):
                doc = Document(file_obj)
                metadata['title'] = doc.core_properties.title if doc.core_properties.title else os.path.basename(
                    file_obj.name)

            return Response(metadata)
        except Resource.DoesNotExist:
            return Response({'error': 'Resource not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['post'])
    def like(self, request, pk=None):
        resource = self.get_object()
        user = request.user
        like, created = Like.objects.get_or_create(resource=resource, user=user)
        if created:
            return Response({'message': 'Resource liked'})
        else:
            return Response({'message': 'Resource already liked'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post', 'delete'])
    def unlike(self, request, pk=None):
        resource = self.get_object()
        user = request.user
        like = Like.objects.filter(resource=resource, user=user).first()
        if like:
            like.delete()
            return Response({'message': 'Resource unliked'})
        else:
            return Response({'message': 'Resource not liked'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def comment(self, request, pk=None):
        resource = self.get_object()
        user = request.user
        comment_text = request.data.get('comment')
        if comment_text:
            comment = Comment.objects.create(resource=resource, user=user, comment=comment_text)
            return Response({'message': 'Comment added'})
        else:
            return Response({'error': 'Comment text is required'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def comments(self, request, pk=None):
        resource = self.get_object()
        comments = resource.comments.all()
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def likes(self, request, pk=None):
        resource = self.get_object()
        likes = resource.likes.all()
        serializer = LikeSerializer(likes, many=True)
        return Response(serializer.data)


class UserSignUpView(generics.CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

    def perform_create(self, serializer):
        user = serializer.save()
        if user:
            refresh = RefreshToken.for_user(user)
            # Return tokens as JSON data along with HTTP 201 Created
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_201_CREATED)


class UserSignInView(generics.CreateAPIView):
    serializer_class = UserSignInSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def logged_in_user(request):
    user = request.user
    user_data = {
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name

    }
    return Response(user_data)


class GetUserByUsername(APIView):
    def get(self, request, username):
        try:
            user = CustomUser.objects.get(username=username)
            serializer = CustomUserSerializer(user)
            return Response(serializer.data)
        except CustomUser.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)


class LikeViewSet(viewsets.ModelViewSet):
    queryset = Like.objects.all()
    serializer_class = LikeSerializer


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer


class UserResourceListView(generics.ListAPIView):
    serializer_class = ResourceSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        username = self.kwargs['username']
        user = get_object_or_404(CustomUser, username=username)
        return Resource.objects.filter(owner=user)


class FollowViewSet(viewsets.ModelViewSet):
    queryset = Follow.objects.all()
    serializer_class = FollowSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    @action(detail=False, methods=['post'])
    def follow_user(self, request):
        followed_user_id = request.data.get('followed_user_id')
        follower = request.user
        try:
            followed_user = CustomUser.objects.get(id=followed_user_id)
            if follower != followed_user:
                Follow.objects.create(follower=follower, followed_user=followed_user)
                return Response({'message': f'You are now following {followed_user.username}'})
            else:
                return Response({'error': 'You cannot follow yourself'})
        except CustomUser.DoesNotExist:
            return Response({'error': 'User not found'})

    @action(detail=False, methods=['post'])
    def unfollow_user(self, request):
        followed_user_id = request.data.get('followed_user_id')
        follower = request.user
        try:
            followed_user = CustomUser.objects.get(id=followed_user_id)
            follow_instance = Follow.objects.filter(follower=follower, followed_user=followed_user)
            if follow_instance.exists():
                follow_instance.delete()
                return Response({'message': f'You have unfollowed {followed_user.username}'})
            else:
                return Response({'error': 'You were not following this user'})
        except CustomUser.DoesNotExist:
            return Response({'error': 'User not found'})
