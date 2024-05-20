import six
from django.contrib.auth import authenticate, login
from django.core.mail import send_mail, EmailMultiAlternatives
from django.db.models import Q, Count
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.html import strip_tags
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from rest_framework.decorators import api_view, action, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.tokens import PasswordResetTokenGenerator
import requests

from KPortalBackend import settings
from .serializers import CustomUserSerializer, ResourceSerializer, UserSerializer, UserSignInSerializer, LikeSerializer, \
    CommentSerializer, FollowSerializer, UserSearchSerializer, ResourceSearchSerializer, PasswordResetConfirmSerializer, \
    PasswordResetRequestSerializer, LanguageSerializer, TopUsersSerializer, TopLanguagesSerializer, \
    LanguageProportionSerializer
from rest_framework import viewsets, status, generics, permissions
from PyPDF2 import PdfReader
from .models import Resource, CustomUser, Like, Comment, Follow, Language
import os
from docx import Document


class MyTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return (
                six.text_type(user.pk) + six.text_type(timestamp) +
                six.text_type(user.is_active)
        )


password_reset_token_generator = MyTokenGenerator()


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

    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        user = self.get_object()
        user.is_active = False
        user.save()
        return Response({'status': 'user deactivated'})


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
            self.send_like_notification(resource, user)
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
            Comment.objects.create(resource=resource, user=user, comment=comment_text)
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

    def send_like_notification(self, resource, user):
        recipient_user = resource.owner
        subject = 'You Got a Like!'
        from_email = settings.EMAIL_HOST_USER
        recipient_email = recipient_user.email
        frontend_url = settings.FRONTEND_URL

        html_content = render_to_string('liked.html', {
            'recipient_username': recipient_user.username,
            'liker_first_name': user.first_name,
            'liker_last_name': user.last_name,
            'liker_username': user.username,
            'resource_caption': resource.caption,
            'resource_id': resource.id,
            'frontend_url': frontend_url,
        })
        text_content = strip_tags(html_content)

        msg = EmailMultiAlternatives(subject, text_content, from_email, [recipient_email])
        msg.attach_alternative(html_content, "text/html")
        msg.send(fail_silently=False)


class UserSignUpView(generics.CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

    def perform_create(self, serializer):
        user = serializer.save()
        if user:
            refresh = RefreshToken.for_user(user)
            self.send_welcome_email(user)
            # Return tokens as JSON data along with HTTP 201 Created
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_201_CREATED)

    def send_welcome_email(self, user):
        subject = 'Welcome to Enimar Portal!'
        from_email = settings.EMAIL_HOST_USER
        recipient_list = [user.email]
        frontend_url = settings.FRONTEND_URL

        html_content = render_to_string('welcome.html', {'username': user.username, 'frontend_url': frontend_url})
        text_content = strip_tags(html_content)

        msg = EmailMultiAlternatives(subject, text_content, from_email, recipient_list)
        msg.attach_alternative(html_content, "text/html")
        msg.send(fail_silently=False)


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
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

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
                follow, created = Follow.objects.get_or_create(follower=follower, followed_user=followed_user)
                if created:
                    self.send_follow_notification(followed_user, follower)
                    return Response({'message': f'You are now following {followed_user.username}'})
                else:
                    return Response({'message': 'You are already following this user'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'error': 'You cannot follow yourself'}, status=status.HTTP_400_BAD_REQUEST)
        except CustomUser.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

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
                return Response({'error': 'You were not following this user'}, status=status.HTTP_400_BAD_REQUEST)
        except CustomUser.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

    def send_follow_notification(self, followed_user, follower):
        subject = 'New Follower Alert!'
        from_email = settings.EMAIL_HOST_USER
        recipient_list = [followed_user.email]
        frontend_url = settings.FRONTEND_URL

        html_content = render_to_string('followed.html', {
            'followed_username': followed_user.username,
            'follower_first_name': follower.first_name,
            'follower_last_name': follower.last_name,
            'follower_username': follower.username,
            'frontend_url': frontend_url,
        })
        text_content = strip_tags(html_content)

        msg = EmailMultiAlternatives(subject, text_content, from_email, recipient_list)
        msg.attach_alternative(html_content, "text/html")
        msg.send(fail_silently=False)


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
                Q(caption__icontains=query) | Q(topic__icontains=query))

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

            # Render HTML email template
            html_content = render_to_string('password_reset_email.html', {'reset_link': reset_link})
            text_content = strip_tags(html_content)

            # Send email
            subject = 'Password Reset'
            from_email = settings.EMAIL_HOST_USER
            to_email = [email]

            msg = EmailMultiAlternatives(subject, text_content, from_email, to_email)
            msg.attach_alternative(html_content, "text/html")
            msg.send(fail_silently=False)

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


class GitHubRepoSearchAPIView(APIView):
    def get(self, request):
        search_query = request.query_params.get('query')
        if not search_query:
            return Response({'error': 'Search query is required'}, status=status.HTTP_400_BAD_REQUEST)

        github_api_url = f'https://api.github.com/search/repositories?q={search_query}'
        headers = {'Authorization': f'Bearer {settings.GITHUB_ACCESS_TOKEN}'}
        response = requests.get(github_api_url, headers=headers)

        if response.status_code == 200:
            search_results = response.json().get('items', [])
            return Response(search_results, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Failed to fetch search results'}, status=response.status_code)


class LanguageViewSet(viewsets.ModelViewSet):
    queryset = Language.objects.all()
    serializer_class = LanguageSerializer
    permission_classes = [permissions.AllowAny]


class LanguageResourceViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def list(self, request, language_id):
        try:
            resources = Resource.objects.filter(language_id=language_id)
            serializer = ResourceSerializer(resources, many=True)

            return Response(serializer.data)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class TopUsersAPIView(APIView):
    def get(self, request, format=None):
        top_users = CustomUser.objects.annotate(num_resources_shared=Count('resource')).order_by(
            '-num_resources_shared')[:10]
        serializer = TopUsersSerializer(top_users, many=True)
        return Response(serializer.data)


class TopLanguagesAPIView(APIView):
    def get(self, request, format=None):
        top_languages = Language.objects.annotate(num_resources=Count('resource')).order_by('-num_resources')[:10]
        serializer = TopLanguagesSerializer(top_languages, many=True)
        return Response(serializer.data)


class TopResourcesAPIView(APIView):
    def get(self, request, format=None):
        top_resources = Resource.objects.annotate(num_likes=Count('likes')).order_by('-num_likes')[:10]
        data = [{'resource_id': resource.id, 'num_likes': resource.num_likes} for resource in top_resources]
        return Response(data)


class LanguageProportionAPIView(APIView):
    def get(self, request, language_id):
        try:
            language = Language.objects.get(pk=language_id)
        except Language.DoesNotExist:
            return Response({"error": "Language not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = LanguageProportionSerializer(language)
        return Response(serializer.data)
