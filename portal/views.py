import six
from django.contrib.auth import authenticate, login
from django.core.mail import send_mail
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from rest_framework.decorators import api_view, action, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.tokens import PasswordResetTokenGenerator


class MyTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return (
                six.text_type(user.pk) + six.text_type(timestamp) +
                six.text_type(user.is_active)
        )


password_reset_token_generator = MyTokenGenerator()

from KPortalBackend import settings
from .serializers import CustomUserSerializer, ResourceSerializer, UserSerializer, UserSignInSerializer, LikeSerializer, \
    CommentSerializer, FollowSerializer, UserSearchSerializer, ResourceSearchSerializer, PasswordResetConfirmSerializer, \
    PasswordResetRequestSerializer
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


class UserSearchView(APIView):
    def get(self, request):
        serializer = UserSearchSerializer(data=request.query_params)
        if serializer.is_valid():
            query = serializer.validated_data['query']

            users = CustomUser.objects.filter(
                Q(username__icontains=query) | Q(first_name__icontains=query) | Q(last_name__icontains=query))

            serializer = CustomUserSerializer(users, many=True)
            return Response(serializer.data)
        else:

            return Response(
                serializer.errors,
                status=400
            )


class ResourceSearchView(APIView):
    def get(self, request):
        serializer = ResourceSearchSerializer(data=request.query_params)
        if serializer.is_valid():
            query = serializer.validated_data['query']

            resources = Resource.objects.filter(
                Q(caption__icontains=query) | Q(topic__icontains=query) | Q(language__icontains=query))

            serializer = ResourceSerializer(resources, many=True)
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=400)


class PasswordResetRequestAPIView(APIView):
    serializer_class = PasswordResetRequestSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        email = request.data.get('email')
        user = CustomUser.objects.filter(email=email).first()
        if user:
            token = password_reset_token_generator.make_token(user)
            uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
            reset_link = f"{settings.FRONTEND_URL}/password-reset-confirm/{uidb64}/{token}/"
            send_mail(
                'Password Reset',
                f'Click the following link to reset your password: {reset_link}',
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False,
            )
            return Response({'message': 'Password reset link has been sent to your email.'}, status=status.HTTP_200_OK)
        return Response({'error': 'User with this email does not exist.'}, status=status.HTTP_404_NOT_FOUND)


class PasswordResetConfirmAPIView(APIView):
    serializer_class = PasswordResetConfirmSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, uidb64, token):
        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Decode the uidb64 to get user ID
            try:
                user_id = urlsafe_base64_decode(uidb64).decode()
            except (TypeError, ValueError, OverflowError):
                user_id = None

            if user_id is not None:
                user = CustomUser.objects.filter(pk=user_id).first()

                # Validate the token
                if user and password_reset_token_generator.check_token(user, token):
                    new_password = serializer.validated_data.get('new_password')
                    user.set_password(new_password)
                    user.save()
                    return Response({'message': 'Password reset successful.'}, status=status.HTTP_200_OK)
                else:
                    return Response({'error': 'Invalid or expired token.'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'error': 'Invalid user ID.'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
