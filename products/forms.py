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
        fields = ['title', 'description', 'price', 'category', 'stock']
        widgets = {
            'description': forms.Textarea(attrs={'class':'form-control'}),
            'stock': forms.NumberInput(attrs={'class':'form-control'}),

        }


    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price <= 0:
            raise forms.ValidationError("Price must be greater than zero.")
        return price
    
    def clean_stock(self):
        stock = self.cleaned_data.get('stock')
        if stock <= 0:
            raise forms.ValidationError("stock is must be greater than zero.")
        return stock
            


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description']