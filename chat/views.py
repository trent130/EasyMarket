from .models import Message, Reaction
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from rest_framework.response import Response

try:
    from channels.layers import get_channel_layer
    from asgiref.sync import async_to_sync
    CHANNELS_AVAILABLE = True
except ImportError:
    CHANNELS_AVAILABLE = False


@login_required
def chat_room(request):
    messages = Message.objects.all()
    for message in messages:
        message.read = True
        message.save()
    return JsonResponse({'messages': list(messages.values())})


@login_required
def send_message(request):
    if request.method == 'POST':
        user = request.user
        message_content = request.POST.get('message', '')

        if message_content.strip():
            # Save message to database
            message = Message.objects.create(user=user, content=message_content)

            # Send message to the channel layer with timestamp
            if CHANNELS_AVAILABLE:
                timestamp = message.timestamp.strftime('%Y-%m-%d %H:%M:%S')
                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.group_send)(
                    'chat_room',
                    {
                        'type': 'chat_message',
                        'username': user.username,
                        'message': message_content,
                        'timestamp': timestamp
                    }
                )

            return JsonResponse({'status': 'success'})
        else:
            return JsonResponse({'status': 'error', 'message': 'Message cannot be empty'})


@login_required
def clear_messages(request):
    Message.objects.all().delete()
    return JsonResponse({'status': 'success'})


@login_required
def get_messages(request):
    messages = Message.objects.all()
    data = [{'username': message.user.username, 'message': message.content, 'timestamp': message.timestamp.strftime(
        '%Y-%m-%d %H:%M:%S')} for message in messages]
    return JsonResponse(data, safe=False)


@login_required
@csrf_exempt
def typing_status(request):
    if request.method == 'POST':
        user = request.user
        typing = request.POST.get('typing', 'false')

        if CHANNELS_AVAILABLE:
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                'chat_room',
                {
                    'type': 'typing_status',
                    'username': user.username,
                    'typing': typing
                }
            )
        return HttpResponse('OK')


@login_required
def add_reaction(request):
    if request.method == 'POST':
        user = request.user
        message_id = request.POST.get('message_id')
        emoji = request.POST.get('emoji')

        message = Message.objects.get(id=message_id)
        reaction, created = Reaction.objects.get_or_create(emoji=emoji, user=user)

        message.reactions.add(reaction)

        return JsonResponse({'status': 'success'})
