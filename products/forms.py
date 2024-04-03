from django import forms
from .models import Product, Image, Category
from django.forms import modelformset_factory

class ImageForm(forms.ModelForm):
    class Meta:
        model = Image
        fields = ['image', 'description']
        widgets = {
            'description': forms.TextInput(attrs={'class': 'form-control'})
        }

ImageFormSet = modelformset_factory(Image, form=ImageForm, extra=1)

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['title', 'description', 'price', 'student', 'category']

    def save(self, commit=True):
        product = super().save(commit=commit)
        if commit:
            for form in self.cleaned_data['images']:
                if form:  # Check if image data is provided
                    image = Image(product=product, **form)  # Create Image instance with product association
                    image.save()
        return product


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description']