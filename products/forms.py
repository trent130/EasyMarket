from django import forms
from .models import Product, Image, Category


class ImageForm(forms.ModelForm):
    class Meta:
        model = Image
        fields = ['image', 'description']
        widgets = {
            'description': forms.TextInput(attrs={'class': 'form-control'})
        }

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['title', 'description', 'price', 'category']




class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description']