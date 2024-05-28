# messaging/models.py

from portal.models import CustomUser
from django.db import models
from django.utils import timezone


class Group(models.Model):
    name = models.CharField(max_length=255)
    members = models.ManyToManyField(CustomUser, related_name='chat_groups')

    def __str__(self):
        return self.name


class Message(models.Model):
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, null=True, blank=True)
    recipient = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='messages', null=True, blank=True)
    content = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f'{self.sender} to {self.recipient or self.group}: {self.content[:20]}'
