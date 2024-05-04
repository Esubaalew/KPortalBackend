from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    first_name = models.CharField(max_length=30, blank=False, null=False)
    last_name = models.CharField(max_length=30, blank=False, null=False)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    bio = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.username


def upload_to(instance, filename):
    return f'resources/{instance.owner.username}/{filename}'


class Resource(models.Model):
    language = models.CharField(max_length=100)
    caption = models.CharField(max_length=255)
    topic = models.CharField(max_length=255)
    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    url = models.URLField(blank=True, null=True)
    file = models.FileField(upload_to=upload_to, blank=True, null=True)
    photo = models.ImageField(upload_to=upload_to, blank=True, null=True)
    date_shared = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date_shared']

    def __str__(self):
        return self.caption


class Like(models.Model):
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    date_liked = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['resource', 'user']

    def get_likes_count(self):
        return self.objects.count()

    def __str__(self):
        return f'{self.user.username} likes {self.resource.caption}'


class Comment(models.Model):
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    comment = models.TextField()
    date_commented = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    def get_comments_count(self):
        return self.objects.count()

    def __str__(self):
        return f'{self.user.username} commented on {self.resource.caption}'
