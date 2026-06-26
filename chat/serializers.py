from rest_framework import serializers
from .models import ChatModel


class GroupChatSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatModel
        fields = '__all__'


class ChatSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatModel
        fields = '__all__'
