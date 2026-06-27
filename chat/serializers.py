from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Conversation, Message

CustomUser = get_user_model()


class ParticipantSerializer(serializers.ModelSerializer):
    avatar = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'avatar']

    def get_avatar(self, obj):
        try:
            request = self.context.get('request')
            avatar = obj.userprofile.avatar
            if avatar and request:
                return request.build_absolute_uri(avatar.url)
        except Exception:
            pass
        return None


class MessageSerializer(serializers.ModelSerializer):
    sender = ParticipantSerializer(read_only=True)

    class Meta:
        model = Message
        fields = ['id', 'sender', 'content', 'created_at', 'read']
        read_only_fields = ['id', 'sender', 'created_at', 'read']


class ConversationSerializer(serializers.ModelSerializer):
    other_user = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()
    product = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = ['id', 'other_user', 'last_message', 'unread_count', 'product', 'created_at', 'updated_at']

    def get_other_user(self, obj):
        request = self.context.get('request')
        other = obj.get_other_user(request.user)
        if other:
            return ParticipantSerializer(other, context=self.context).data
        return None

    def get_last_message(self, obj):
        last = obj.messages.last()
        if last:
            return MessageSerializer(last, context=self.context).data
        return None

    def get_unread_count(self, obj):
        request = self.context.get('request')
        return obj.unread_count_for(request.user)

    def get_product(self, obj):
        if obj.product:
            return {
                'id': obj.product.id,
                'title': obj.product.title,
                'price': float(obj.product.price),
                'image': obj.product.image_url if hasattr(obj.product, 'image_url') else None,
            }
        return None
