from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer

CustomUser = get_user_model()


class ConversationViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ConversationSerializer

    def get_queryset(self):
        return (
            Conversation.objects
            .filter(participants=self.request.user)
            .prefetch_related('participants__userprofile', 'messages__sender__userprofile')
            .select_related('product')
        )

    def create(self, request):
        other_user_id = request.data.get('user_id')
        product_id = request.data.get('product_id')

        if not other_user_id:
            return Response({'error': 'user_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            other_user = CustomUser.objects.get(id=other_user_id)
        except CustomUser.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        if other_user == request.user:
            return Response({'error': 'Cannot start a conversation with yourself'}, status=status.HTTP_400_BAD_REQUEST)

        # Return existing conversation if found
        qs = Conversation.objects.filter(participants=request.user).filter(participants=other_user)
        qs = qs.filter(product_id=product_id) if product_id else qs.filter(product__isnull=True)
        existing = qs.first()

        if existing:
            serializer = self.get_serializer(existing)
            return Response(serializer.data)

        conversation = Conversation.objects.create(product_id=product_id or None)
        conversation.participants.add(request.user, other_user)
        serializer = self.get_serializer(conversation)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get', 'post'])
    def messages(self, request, pk=None):
        conversation = self.get_object()

        if request.method == 'GET':
            msgs = conversation.messages.select_related('sender__userprofile').order_by('created_at')
            serializer = MessageSerializer(msgs, many=True, context={'request': request})
            return Response(serializer.data)

        content = request.data.get('content', '').strip()
        if not content:
            return Response({'error': 'Content is required'}, status=status.HTTP_400_BAD_REQUEST)

        message = Message.objects.create(
            conversation=conversation,
            sender=request.user,
            content=content,
        )
        # Bump conversation updated_at so it surfaces at top of list
        Conversation.objects.filter(pk=conversation.pk).update(updated_at=message.created_at)

        serializer = MessageSerializer(message, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['patch'])
    def read(self, request, pk=None):
        conversation = self.get_object()
        conversation.messages.exclude(sender=request.user).update(read=True)
        return Response({'status': 'marked as read'})

    def destroy(self, request, *args, **kwargs):
        conversation = self.get_object()
        conversation.participants.remove(request.user)
        if conversation.participants.count() == 0:
            conversation.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
