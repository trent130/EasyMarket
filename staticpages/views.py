from django.shortcuts import render

# Create your views here.
def index(request):
    context = {'title': 'home'}
    return render(request, 'staticpages/index.html')

def about(request):
    context: {'title' : 'about'}
    return render(request, 'staticpages/about.html')

def contact(request):
    context = {'title': 'contact'}
    return render(request, 'staticpages/contact.html')

def help(request):
    context = {'title': 'help'}
    return render(request, 'staticpages/help.html')

def signin(request):
    context = {'title': 'signin'}
    return render(request, 'marketplace/account/register.html')

def register(request):
    context = {'title': 'register'}
    return render(request, 'marketplace/account/register.html')

def search(request):
    context = {'title': 'search'}
    return render(request, 'marketplace/search.html')

def chat(request):
    context = {'title': 'chat'}
    return render(request, 'staticpages/chat.html')

def categories(request):
    context = {'title': 'categories'}
    return render(request, 'marketplace/categories.html')

# def room(request, room_name):
#     return render(request, 'staticpages/room.html', {
#         'room_name': room_name
#     })

def products(request):
    context = {'title': 'products'}
    return render(request, 'products/product.html')

def orders(request):
    context = {'title': 'orders'}
    return render(request, 'orders/order.html')