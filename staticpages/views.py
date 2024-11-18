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
    hero_slides = [
        {
            'image': 'images/bg_main.jpg',
            'title': 'Welcome to EasyMarket',
            'description': 'Buy and sell stuff and more. All within your campus community.',
            'primary_btn': {
                'text': 'Shop Now',
                'url': 'products:product_list'
            },
            'secondary_btn': {
                'text': 'Sell Now',
                'url': 'products:add_product'
            }
        },
        {
            'image': 'images/bg_main1.jpg',
            'title': 'Discover Exciting Deals',
            'description': 'Find amazing discounts on textbooks, gadgets, and more.',
            'primary_btn': {
                'text': 'Explore Now',
                'url': 'products:product_list'
            },
            'secondary_btn': {
                'text': 'Sell Now',
                'url': 'products:add_product'
            }
        },
        {
            'image': 'images/bg_main2.jpg',
            'title': 'Shop with Confidence',
            'description': 'Secure transactions and buyer protection guaranteed.',
            'primary_btn': {
                'text': 'Start Shopping',
                'url': 'products:product_list'
            },
            'secondary_btn': {
                'text': 'Sell Now',
                'url': 'products:add_product'
            }
        }
    ]
        
    featured_users = UserProfile.objects.order_by('?')[:6]
    featured_products = Product.objects.annotate(num_products=Count('image')).order_by('-num_products')[:9]

        # Features data
    features = [
        {
            'icon': 'fa-shield-alt',
            'title': 'Secure Transactions',
            'description': 'All transactions are protected and secure'
        },
        {
            'icon': 'fa-tags',
            'title': 'Best Deals',
            'description': 'Find the best prices on campus'
        },
        {
            'icon': 'fa-user-shield',
            'title': 'Verified Users',
            'description': 'All users are verified students'
        }
    ]

    testimonials = [
        {
            'name': 'John Doe',
            'role': 'CS Student',
            'image': 'images/background_.jpg',
            'quote': 'Found great deals on textbooks and study materials through EasyMarket.'
        },
        {
            'name': 'Jane Smith',
            'role': 'Business Student',
            'image': 'images/background_1.jpg',
            'quote': 'Sold my old textbooks and made enough money to buy new ones.'
        },
        {
            'name': 'Mike Johnson',
            'role': 'Engineering Student',
            'image': 'images/background_2.jpg',
            'quote': 'Found rare lab equipment at a fraction of the cost.'
        }
    ]

    context = {'title': 'home', 'featured_products': featured_products, 'features': features, 'featured_users': featured_users, 'hero_slides': hero_slides, 'testimonials': testimonials}
    return render(request, 'pages/staticpages/index.html', context)

def about(request):
    context = {'title' : 'about'}
    return render(request, 'pages/staticpages/about.html', context)


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
    return render(request, 'pages/staticpages/contact.html', {'form': form})

def contact_success(request):   
    return render(request, 'pages/staticpages/contact_success.html')


def help(request):
    context = {'title': 'help'}
    return render(request, 'pages/staticpages/help.html', context)

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
    return render(request, 'pages/registration/login.html', context)


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
    return render(request, 'pages/registration/register.html', context)
            
def search(request):
    context = {'title': 'search'}
    return render(request, 'pages/marketplace/search.html', context)

@login_required
def chat(request):
    context = {'title': 'chat'}
    return render(request, 'pages/staticpages/chat.html', context)

@login_required
def orders(request):
    context = {'title': 'orders'}
    return render(request, 'pages/orders/order.html', context)

def password_reset(request):
    context = {'title': 'password_reset'}
    return render(request, 'pages/registration/password_change_form.html', context)

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
    return render(request, 'pages/registration/profile.html', context)
@login_required
def cart(request):
    context = {'title': 'cart'}
    return render(request, 'pages/marketplace/cart.html', context)

@require_POST
def signout(request):
    logout(request)
    context = {'title': 'signout'}
    return render(request, 'pages/staticpages/account/logout.html', context)

@login_required
def dashboard(request):
    context = {'title' : 'dashboard'}
    return render(request, 'pages/staticpages/dashboard.html', context )


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
    return render(request, 'pages/staticpages/add_category.html', {'form': form})

def category_products(request, category_id):
    category = Category.objects.get(id=category_id)
    products = Product.objects.filter(category=category)
    return render(request, 'pages/staticpages/category_product.html', {'category': category, 'products': products})

def larrymax(request):
    context = {'title': 'larrymax'}
    return render(request, 'pages/staticpages/larrymax.html', context)
