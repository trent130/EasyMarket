from django import forms

class PaymentForm(forms.Form):

    phone_number = forms.CharField(max_length=15, label='Phone Number')
    amount = forms.DecimalField(max_digits=8, decimal_places=2, label='Amount')
    account_reference = forms.CharField(max_length=50, label='Account Reference')
    transaction_desc = forms.CharField(max_length=100, label='Transaction Description')

    def clean_phone_number(self):
        phone_number = self.cleaned_data['phone_number']
        if not phone_number.startswith('+254'):
            raise forms.ValidationError("Please enter a valid phone number starting with +254.")
        return phone_number

    def clean_amount(self):
        amount = self.cleaned_data['amount']
        # Validate amount (e.g., ensure it's greater than zero)
        if amount <= 0:
            raise forms.ValidationError("Please enter a valid amount greater than zero.")
        return amount

    # amount = forms.DecimalField(label='Amount', max_digits=10, decimal_places=2)
    # card_number = forms.CharField(label='Card Number', max_length=16)
    # expiration_date = forms.CharField(label='Expiration Date', max_length=5, help_text='Format: MM/YY')
    # cvv = forms.CharField(label='CVV', max_length=3)

