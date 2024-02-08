# views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Message
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.utils import timezone

@login_required
def chat_room(request):
    messages = Message.objects.all()
    return render(request, 'marketplace/chat_room.html', {'messages': messages})

@login_required
def send_message(request):
    if request.method == 'POST':
        user = request.user
        message_content = request.POST.get('message', '')

        if message_content.strip():
            # Save message to database
            message = Message.objects.create(user=user, content=message_content)

            # Send message to the channel layer with timestamp
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
    data = [{'username': message.user.username, 'message': message.content, 'timestamp': message.timestamp.strftime('%Y-%m-%d %H:%M:%S')} for message in messages]
    return JsonResponse(data, safe=False)

# @login_required
# def chat(request):
#     context = {'title': 'chat'}
#     return render(request, 'staticpages/chat.html', context)

@login_required
@csrf_exempt
def typing_status(request):
    if request.method == 'POST':
        user = request.user
        typing = request.POST.get('typing', 'false')
        
        # Broadcast typing status to other users in the chat room
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