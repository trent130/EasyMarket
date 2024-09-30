from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from .forms import LoginForm, SignUpForm, ProfileForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.views.decorators.http import require_POST
from django.contrib import messages
from .forms import CategoryForm, ContactForm, UserProfileForm
from django.core.mail import send_mail
from marketplace.models import UserProfile
from products.models import Category, Product
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Count

def index(request):
    featured_users = UserProfile.objects.order_by('?')[:6]
    featured_products = Product.objects.annotate(num_products=Count('image')).order_by('-num_products')[:9]
    context = {'title': 'home', 'featured_products': featured_products, 'featured_users': featured_users}
    return render(request, 'staticpages/index.html', context)

def about(request):
    context = {'title' : 'about'}
    return render(request, 'staticpages/about.html', context)


def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            message = form.cleaned_data['message']

            send_mail(
                'Contact Form Submission from {}'.format(name),
                message,
                email,
                ['warsamegift@gmail.com'],  # Replace with your email
            )
            return redirect('marketplace:contact_success')
        else:
            # Form is not valid, so render the form with errors
            return render(request, 'staticpages/contact.html', {'form': form})
    else:
        form = ContactForm()
    return render(request, 'staticpages/contact.html', {'form': form})

def contact_success(request):   
    return render(request, 'staticpages/contact_success.html')


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
    return render(request, 'registration/login.html', context)


def register(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            if User.objects.filter(email=email).exists():
                messages.success(request,  'A user with this email already exists.')
                return redirect('register')
            form.save(commit=False)  
            
            # role = form.cleaned_data.get('role')
            # if role == 'seller' or role == 'buyer':
            #     User.is_student = True
            #     User.is_basic = False
            
            user = form.save() #save the user instance
            
            # Log in the user after successful registration
            login(request, user)
            # Redirect to the home page after successful registration
            return redirect('home')
        else:
            return HttpResponse('Invalid Registration')
    else:
        form = SignUpForm()
    context = {'title': 'register', 'form': form}
    return render(request, 'registration/register.html', context)
            
def search(request):
    context = {'title': 'search'}
    return render(request, 'marketplace/search.html', context)

@login_required
def chat(request):
    context = {'title': 'chat'}
    return render(request, 'staticpages/chat.html', context)

@login_required
def orders(request):
    context = {'title': 'orders'}
    return render(request, 'orders/order.html', context)

def password_reset(request):
    context = {'title': 'password_reset'}
    return render(request, 'registration/password_change_form.html', context)

@login_required
def user_profile(request):
    if request.method == 'POST':
        user_form = ProfileForm(request.POST, instance=request.user)
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('user_profile')
    else:
        user_form = ProfileForm(instance=request.user)
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        profile_form = UserProfileForm(instance=profile)
        
    context = {'title': 'profile', 'user_form': user_form, 'profile_form': profile_form}
    return render(request, 'staticpages/account/profile.html', context)
@login_required
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


@user_passes_test(lambda u: u.is_superuser, login_url='/larrymax/')
@login_required
def add_category(request):
    if not request.user.is_superuser:
        messages.error(request, 'Only superusers can add categories.')
        return redirect('home')  # or wherever you want to redirect

    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('products:categories')
    else:
        form = CategoryForm()
    return render(request, 'staticpages/add_category.html', {'form': form})

def category_products(request, category_id):
    category = Category.objects.get(id=category_id)
    products = Product.objects.filter(category=category)
    return render(request, 'staticpages/category_product.html', {'category': category, 'products': products})

def larrymax(request):
    context = {'title': 'larrymax'}
    return render(request, 'staticpages/larrymax.html', context)
