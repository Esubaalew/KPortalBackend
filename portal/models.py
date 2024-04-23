from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    first_name = models.CharField(max_length=30, blank=False, null=False)
    last_name = models.CharField(max_length=30, blank=False, null=False)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    bio = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.username


RESOURCE_TYPES = [
    ('Link', 'Link'),
    ('File', 'File'),
]


class Resource(models.Model):
    language = models.CharField(max_length=100)
    caption = models.CharField(max_length=255)
    topic = models.CharField(max_length=255)
    resource_type = models.CharField(max_length=20, choices=RESOURCE_TYPES, default='Link')
    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    date_shared = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.caption


class LinkResource(Resource):
    url = models.URLField()

    def __str__(self):
        return f"{self.caption} - {self.url}"


def upload_to(instance, filename):
    return f'resources/{instance.owner.username}/{filename}'


class FileResource(Resource):
    file = models.FileField(upload_to=upload_to, verbose_name='File (PDF)')

    def __str__(self):
        return f"{self.caption} - {self.file}"
