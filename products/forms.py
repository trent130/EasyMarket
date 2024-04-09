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
        fields = ['title', 'description', 'price', 'category', 'student']  # Include 'student' field
        widgets = {
            'description': forms.Textarea(attrs={'cols': 40, 'rows': 10, 'class': 'form-control'}),
            'student': forms.HiddenInput(),  # Hide student field if you don't want to display it in the form
        }

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description']