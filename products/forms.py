from django import forms
from .models import Product,Image

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['title', 'description', 'price', 'student', 'category']

class ImageForm(forms.ModelForm):
    class Meta:
        model = Image
        fields = ['image', 'description']