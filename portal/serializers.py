from django.contrib.auth import authenticate
from rest_framework import serializers
from .models import CustomUser, Resource, Like, Comment, Follow, Language


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'first_name', 'last_name', 'bio']


class ResourceSerializer(serializers.ModelSerializer):
    likes_count = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()
    language_name = serializers.CharField(source='language.name')  # Add this line

    class Meta:
        model = Resource
        fields = [
            'id', 'language_name',
            'caption', 'topic', 'owner', 'url', 'file',
            'photo', 'date_shared', 'date_modified',
            'likes_count', 'comments_count'
        ]

    def get_likes_count(self, obj):
        return obj.likes.count()

    def get_comments_count(self, obj):
        return obj.comments.count()


class UserSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField()
    last_name = serializers.CharField()

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'username', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = self.Meta.model.objects.create_user(
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user


class UserSignInSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            raise serializers.ValidationError("Username and password are required.")

        user = authenticate(username=username, password=password)

        if not user:
            raise serializers.ValidationError("Invalid credentials.")

        data['user'] = user
        return data


class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = '__all__'

    def create(self, validated_data):
        user = self.context['request'].user
        like, created = Like.objects.get_or_create(user=user, **validated_data)
        return like


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'

    def create(self, validated_data):
        user = self.context['request'].user
        comment = Comment.objects.create(user=user, **validated_data)
        return comment


class FollowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Follow
        fields = '__all__'


class UserSearchSerializer(serializers.Serializer):
    query = serializers.CharField()

    def validate_query(self, value):
        """
        Validate the query parameter.
        """
        if not value.strip():
            raise serializers.ValidationError("Query parameter cannot be empty.")
        return value


class ResourceSearchSerializer(serializers.Serializer):
    query = serializers.CharField()

    def validate_query(self, value):
        """
        Validate the query parameter.
        """
        if not value.strip():
            raise serializers.ValidationError("Query parameter cannot be empty.")
        return value


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()


class PasswordResetConfirmSerializer(serializers.Serializer):
    new_password = serializers.CharField(min_length=8)


class LanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Language
        fields = ['id', 'name', 'shorty', 'description']
