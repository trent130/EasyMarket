from django import forms


class AddToCartForm(forms.Form):
    quantity = forms.IntegerField(min_value=1, initial=1)

    def __init__(self, *args, **kwargs):
        self.product_id = kwargs.pop('product_id', None)
        super().__init__(*args, **kwargs)


class UpdateCartForm(forms.Form):
    quantity = forms.IntegerField(min_value=0)
