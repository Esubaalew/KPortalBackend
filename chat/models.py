# from django.db import models
# from portal.models import CustomUser
#
#
# class ChatRoom(models.Model):
#     ROOM_TYPES = (
#         ('one_to_one', 'One-to-One'),
#         ('group', 'Group'),
#     )
#     name = models.CharField(max_length=100)
#     description = models.TextField()
#     room_type = models.CharField(max_length=20, choices=ROOM_TYPES)
#     participants = models.ManyToManyField(CustomUser, related_name='chat_rooms', blank=True)
#
#     def __str__(self):
#         return self.name
#
#
# class Message(models.Model):
#     user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
#     chat_room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE)
#     content = models.TextField()
#     timestamp = models.DateTimeField(auto_now_add=True)
#
#     def __str__(self):
#         return self.content
