# adminapp/forms.py
from django import forms

class UserRoleForm(forms.Form):
    role = forms.ChoiceField(choices=[(group.name, group.name) for group in Group.objects.all()])
