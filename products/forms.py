# from django import forms
# from .models import Product, Category


# class ProductForm(forms.ModelForm):
#     class Meta:
#         model = Product
#         fields = ['title', 'description', 'price', 'category', 'image', 'stock']
#         widgets = {
#             'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
#             'stock': forms.NumberInput(attrs={'class': 'form-control', 'rows': 5}),
#             'image': forms.FileInput(attrs={'class': 'form-control', 'rows': 5}),
#         }

#     def clean_price(self):
#         price = self.cleaned_data.get('price')
#         if price <= 0:
#             raise forms.ValidationError("Price must be greater than zero.")
#         return price

#     def clean_stock(self):
#         stock = self.cleaned_data.get('stock')
#         if stock <= 0:
#             raise forms.ValidationError("Stock must be greater than zero.")
#         return stock


# class CategoryForm(forms.ModelForm):
#     class Meta:
#         model = Category
#         fields = '__all__'
#     widgets = {
#         'image': forms.ClearableFileInput(attrs={'class': 'form-control', 'rows': 5}),
#         'name': forms.TextInput(attrs={'class': 'form-control', 'rows': 5}),
#         'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
#     }
