from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=254, help_text='Required. Inform a valid email address.')
    role_choices = [
        ('buyer', 'Buyer'),
        ('seller', 'Seller'),
        ('both', 'Both'),
    ]
    role = forms.ChoiceField(choices=role_choices)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'role']

class ContactForm(forms.Form):
    username = forms.CharField()
