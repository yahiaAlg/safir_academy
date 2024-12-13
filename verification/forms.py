from django import forms
from django.contrib.auth.forms import AuthenticationForm

class StaffLoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Username'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Password'
    }))

class ManualSearchForm(forms.Form):
    registration_id = forms.UUIDField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter Registration ID'
    }))