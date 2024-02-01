from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth import authenticate, login
from .forms import LoginForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

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
    form = LoginForm()
    context = {'title': 'login', 'form': form}
    return render(request, 'staticpages/account/login.html', context)

def register(request):
    context = {'title': 'register'}
    return render(request, 'staticpages/account/register.html')

def search(request):
    context = {'title': 'search'}
    return render(request, 'marketplace/search.html')

@login_required
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

@login_required
def orders(request):
    context = {'title': 'orders'}
    return render(request, 'orders/order.html')

def user_Login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(
                request,
                username=cd['username'],
                password=cd['password']
            )
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return HttpResponse('Authenticated Successfully')
                else:
                    return HttpResponse('Disabled Account')
            else:
                return HttpResponse('Invalid Login')
    else:
        form = LoginForm()
    return render(request, 'staticpages/account/login.html', {'form': form})  
def password_reset(request):
    context = {'title': 'password_reset'}
    return render(request, 'staticpages/account/password_reset.html')

def user_profile(request):
    context = {'title': 'user_profile'}
    return render(request, 'staticpages/account/profile.html')

def cart(request):
    context = {'title': 'cart'}
    return render(request, 'marketplace/cart.html')

# def user_register(request):
#     context = {'title': 'user_register'}  
#     return render(request, 'staticpages/account/register.html')

# def user_logout(request):
#     context = {'title': 'user_logout'}
#     return render(request, 'staticpages/account/logout.html')

# def user_profile_edit(request):
#     context = {'title': 'user_profile_edit'}
#     return render(request, 'staticpages/account/profile_edit.html')

# def user_profile_delete(request):
#     context = {'title': 'user_profile_delete'}
#     return render(request, 'staticpages/account/profile_delete.html')

# def user_profile_password(request):
#     context = {'title': 'user_profile_password'}      
#     return render(request, 'staticpages/account/profile_password.html')

# def user_profile_orders(request): 
#     context = {'title': 'user_profile_orders'}
#     return render(request, 'staticpages/account/profile_orders.html')

# def user_profile_order_details(request):
#     context = {'title': 'user_profile_order_details'}
#     return render(request, 'staticpages/account/profile_order_details.html')

