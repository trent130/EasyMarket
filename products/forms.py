from django import forms
from .models import Product, Image, Category
from multiupload.fields import MultiFileField

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['title', 'description', 'price', 'student', 'category']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})


class ImageForm(forms.ModelForm):
    image = MultiFileField(min_num=1, max_num=5, max_file_size=1024*1024*5)

    class Meta:
        model = Image
        fields = ['image', 'description']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description']