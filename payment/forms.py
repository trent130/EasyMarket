from django import forms

class PaymentForm(forms.Form):
    phone_number = forms.CharField(
        max_length=12,
        min_length=10,
        label="M-Pesa Phone Number",
        help_text="Enter your M-Pesa registered phone number"
    )
    amount = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        disabled=True
    )
    account_reference = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.HiddenInput()
    )
    transaction_desc = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.HiddenInput()
    )

    def clean_phone_number(self):
        phone = self.cleaned_data['phone_number']
        # Remove any spaces or special characters
        phone = ''.join(filter(str.isdigit, phone))
        if not phone.isdigit():
            raise forms.ValidationError("Phone number must contain only digits")
        return phone
    # amount = forms.DecimalField(label='Amount', max_digits=10, decimal_places=2)
    # card_number = forms.CharField(label='Card Number', max_length=16)
    # expiration_date = forms.CharField(label='Expiration Date', max_length=5, help_text='Format: MM/YY')
    # cvv = forms.CharField(label='CVV', max_length=3)

