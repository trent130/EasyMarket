from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import redirect
from orders.models import Order
from django.http import HttpResponseNotAllowed
from django.shortcuts import redirect

@login_required
def checkout(request):
    if request.method == 'POST':
        user = request.user

        # Create a new order
        order = Order(user=user)

        # Add the items from the cart to the order
        for item in user.cart.all():
            order.items.add(item)

        # Save the order
        order.save()

        # Clear the cart
        user.cart.clear()
        user.save()

        messages.success(request, "Checkout successful. Your order is being processed.")
        return redirect('marketplace:order_confirmation', order_id=order.id)

    else:
        # If the request method is not POST, redirect to the cart page
        return redirect('marketplace:cart')

def clear_cart(request): 
    if request.method == 'POST':
        user = request.user
        user.cart.clear()
        user.save()
        return redirect('marketplace:cart_cleared')
    else:
        return HttpResponseNotAllowed(['POST'])

def cart(request):
    return render(request, 'marketplace/cart.html')

def cart_cleared(request):
    return render(request, 'marketplace/cart_cleared.html')








# from .models import Message, Reaction, UserProfile
# from django.views.decorators.csrf import csrf_exempt
# from django.http import HttpResponse
# from django.utils import timezone

# @login_required
# def chat_room(request):
#     messages = Message.objects.all()
#     for message in messages:
#         message.read = True
#         message.save()
#     return render(request, 'marketplace/chat_room.html', {'messages': messages})

# @login_required
# def send_message(request):
#     if request.method == 'POST':
#         user = request.user
#         message_content = request.POST.get('message', '')

#         if message_content.strip():
#             # Save message to database
#             message = Message.objects.create(user=user, content=message_content)

#             # Send message to the channel layer with timestamp
#             timestamp = message.timestamp.strftime('%Y-%m-%d %H:%M:%S')
#             channel_layer = get_channel_layer()
#             async_to_sync(channel_layer.group_send)(
#                 'chat_room',
#                 {
#                     'type': 'chat_message',
#                     'username': user.username,
#                     'message': message_content,
#                     'timestamp': timestamp
#                 }
#             )

#             return JsonResponse({'status': 'success'})
#         else:
#             return JsonResponse({'status': 'error', 'message': 'Message cannot be empty'})

# @login_required
# def clear_messages(request):
#     Message.objects.all().delete()
#     return JsonResponse({'status': 'success'})

# @login_required
# def get_messages(request):
#     messages = Message.objects.all()
#     data = [{'username': message.user.username, 'message': message.content, 'timestamp': message.timestamp.strftime('%Y-%m-%d %H:%M:%S')} for message in messages]
#     return JsonResponse(data, safe=False)

# @login_required
# @csrf_exempt
# def typing_status(request):
#     if request.method == 'POST':
#         user = request.user
#         typing = request.POST.get('typing', 'false')

#         # Broadcast typing status to other users in the chat room
#         channel_layer = get_channel_layer()
#         async_to_sync(channel_layer.group_send)(
#             'chat_room',
#             {
#                 'type': 'typing_status',
#                 'username': user.username,
#                 'typing': typing
#             }
#         )
#         return HttpResponse('OK')

# @login_required
# def add_reaction(request):
#     if request.method == 'POST':
#         user = request.user
#         message_id = request.POST.get('message_id')
#         emoji = request.POST.get('emoji')

#         message = Message.objects.get(id=message_id)
#         reaction, created = Reaction.objects.get_or_create(emoji=emoji, user=user)

#         message.reactions.add(reaction)

#         return JsonResponse({'status': 'success'})

