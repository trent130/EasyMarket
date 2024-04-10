from django import forms

class ContactForm(forms.Form):
    name = forms.CharField(widget=forms.TextInput(attrs={'class': 'requiredField'}))
    email = forms.EmailField(widget=forms.TextInput(attrs={'class': 'requiredField'}))
    message = forms.CharField(widget=forms.Textarea(attrs={'class': 'requiredField'}))

class searchForm(forms.Form):
    query = forms.CharField(label= 'search', max_length= 50)

class AddToCartForm(forms.Form):
    product_id = forms.IntegerField(widget=forms.HiddenInput())
    quantity = forms.IntegerField(label='Quantity', min_value=1, max_value=100)

class UpdateCartForm(forms.Form):
    quantity = forms.IntegerField(label='Quantity', min_value=1)
    
class RemoveFromCartForm(forms.Form):
    item_id = forms.IntegerField(widget=forms.HiddenInput())