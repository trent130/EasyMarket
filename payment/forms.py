from django import forms

class PaymentForm(forms.Form):
    amount = forms.DecimalField(label='Amount', max_digits=10, decimal_places=2)
    card_number = forms.CharField(label='Card Number', max_length=16)
    expiration_date = forms.CharField(label='Expiration Date', max_length=5, help_text='Format: MM/YY')
    cvv = forms.CharField(label='CVV', max_length=3)
