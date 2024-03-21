from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from products.models import Category

class LoginForm(forms.Form):
    username = forms.CharField(label="Username", max_length=150, required=True)
    password = forms.CharField(label="Password", widget=forms.PasswordInput, required=True)

class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=254, help_text='Required. Inform a valid email address.')
    role_choices = [
        ('buyer', 'Buyer'),
        ('seller', 'Seller'),
        ('both', 'Both'),
    ]
    role = forms.ChoiceField(label="Role", choices=role_choices)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'role']
        labels = {
            'username': 'Username',
            'email': 'Email',
            'password1': 'Password',
            'password2': 'Confirm Password',
        }

class ContactForm(forms.Form):
    username = forms.CharField(label="Username", max_length=150, required=True)
    email = forms.EmailField(label="Email", max_length=254, required=True)
    subject = forms.CharField(label="Subject", max_length=100, required=True)
    message = forms.CharField(label="Message", widget=forms.Textarea, required=True)

class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        labels = {
            'first_name': 'First Name',
            'last_name': 'Last Name',
            'email': 'Email',
        }

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description']