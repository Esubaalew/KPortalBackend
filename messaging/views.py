# messaging/views.py
from django.core.mail import EmailMessage

from django.core.exceptions import ObjectDoesNotExist
from rest_framework import generics, status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Group, Message
from .serializers import GroupSerializer, MessageSerializer, PrivateChatSerializer, LatestMessageSerializer
from portal.models import CustomUser
from django.db.models import Q, Max


class GroupListCreate(generics.ListCreateAPIView):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [IsAuthenticated]


class GroupDetail(generics.RetrieveAPIView):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [IsAuthenticated]


class MessageListCreate(generics.ListCreateAPIView):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        sender = self.request.user
        recipient_id = self.request.data.get('recipient_id')
        group_id = self.request.data.get('group_id')
        content = self.request.data.get('content')

        recipient = CustomUser.objects.get(id=recipient_id) if recipient_id else None
        group = Group.objects.get(id=group_id) if group_id else None

        serializer.save(sender=sender, recipient=recipient, group=group, content=content)


class MessageList(generics.ListAPIView):
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        group_id = self.kwargs.get('group_id')
        recipient_id = self.kwargs.get('recipient_id')

        if group_id:
            return Message.objects.filter(group_id=group_id).order_by('timestamp')
        elif recipient_id:
            recipient = CustomUser.objects.get(id=recipient_id)
            return Message.objects.filter(
                Q(sender=user, recipient=recipient) |
                Q(sender=recipient, recipient=user)
            ).order_by('timestamp')
        return Message.objects.none()


class AllPrivateChats(generics.ListAPIView):
    serializer_class = PrivateChatSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        latest_messages = Message.objects.filter(
            Q(sender=user) | Q(recipient=user)
        ).values('sender', 'recipient').annotate(latest_timestamp=Max('timestamp')).order_by('-latest_timestamp')

        unique_chat_users = set()
        for chat in latest_messages:
            if chat['sender'] != user.id:
                unique_chat_users.add(chat['sender'])
            if chat['recipient'] != user.id:
                unique_chat_users.add(chat['recipient'])

        unique_chat_users_with_latest_message = []
        for other_user_id in unique_chat_users:
            try:
                other_user = CustomUser.objects.get(id=other_user_id)
                latest_message = Message.objects.filter(
                    (Q(sender=user) & Q(recipient=other_user)) | (Q(sender=other_user) & Q(recipient=user))
                ).order_by('-timestamp').first()
                unique_chat_users_with_latest_message.append({
                    'user': other_user,
                    'latest_message': latest_message
                })
            except ObjectDoesNotExist:
                pass

        unique_chat_users_with_latest_message.sort(key=lambda x: x['latest_message'].timestamp, reverse=True)

        return unique_chat_users_with_latest_message


class GroupMembers(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, group_id):
        try:
            group = Group.objects.get(id=group_id)
            members = group.members.all()
            member_ids = [member.id for member in members]
            return Response({'members': member_ids})
        except Group.DoesNotExist:
            return Response({'error': 'Group not found'}, status=status.HTTP_404_NOT_FOUND)


class SendEmailView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        subject = request.data.get('subject')
        content = request.data.get('content')
        recipient_email = request.data.get('recipient_email')
        attachment = request.FILES.get('attachment')
        sender = request.user

        # Debug statements to verify data
        print(f"Subject: {subject}")
        print(f"Content: {content}")
        print(f"Recipient Email: {recipient_email}")
        print(f"Attachment: {attachment}")

        if not recipient_email:
            return Response({'error': 'Recipient email is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            email = EmailMessage(subject, content, to=[recipient_email])

            if attachment:
                email.attach(attachment.name, attachment.read(), attachment.content_type)

            email.send()

            return Response({'message': 'Email sent successfully'}, status=status.HTTP_200_OK)
        except Exception as e:
            print(f"Error: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
