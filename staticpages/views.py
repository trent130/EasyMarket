from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from .forms import LoginForm, SignUpForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.views.decorators.http import require_POST


def index(request):
    context = {'title': 'home'}
    return render(request, 'staticpages/index.html', context)

def about(request):
    context = {'title' : 'about'}
    return render(request, 'staticpages/about.html', context)

def contact(request):
    context = {'title': 'contact'}
    return render(request, 'staticpages/contact.html', context)

def help(request):
    context = {'title': 'help'}
    return render(request, 'staticpages/help.html', context)

def signin(request):
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
    context = {'title': 'login', 'form': form}
    return render(request, 'staticpages/account/login.html', context)


def register(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponse('Registration Successful')
        else:
            return HttpResponse('Invalid Registration')
    else:
        form = SignUpForm()
    context = {'title': 'register', 'form': form}
    return render(request, 'staticpages/account/register.html', context)

        
def search(request):
    context = {'title': 'search'}
    return render(request, 'marketplace/search.html', context)

@login_required
def chat(request):
    context = {'title': 'chat'}
    return render(request, 'staticpages/chat.html', context)

def categories(request):
    context = {'title': 'categories'}
    return render(request, 'marketplace/categories.html', context)


@login_required
def orders(request):
    context = {'title': 'orders'}
    return render(request, 'orders/order.html', context)

def password_reset(request):
    context = {'title': 'password_reset'}
    return render(request, 'staticpages/registration/password_change_form.html', context)

@login_required
def user_profile(request):
    context = {'title': 'user_profile'}
    return render(request, 'staticpages/account/profile.html', context)

def cart(request):
    context = {'title': 'cart'}
    return render(request, 'marketplace/cart.html', context)

@require_POST
def signout(request):
    logout(request)
    context = {'title': 'signout'}
    return render(request, 'staticpages/account/logout.html', context)

@login_required
def dashboard(request):
    context = {'title' : 'dashboard'}
    return render(request, 'staticpages/dashboard.html', context )