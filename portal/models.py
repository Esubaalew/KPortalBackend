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
