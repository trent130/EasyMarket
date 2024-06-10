from django import forms
from .models import Product, Category


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['title', 'description', 'price', 'category', 'image', 'stock']
        widgets = {
            'description': forms.Textarea(attrs={'class':'form-control'}),
            'stock': forms.NumberInput(attrs={'class':'form-control'}),
            'image': forms.FileInput(attrs={'class':'form-control'})
        }

    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price <= 0:
            raise forms.ValidationError("Price must be greater than zero.")
        return price

    def clean_stock(self):
        stock = self.cleaned_data.get('stock')
        if stock <= 0:
            raise forms.ValidationError("Stock must be greater than zero.")
        return stock

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description']