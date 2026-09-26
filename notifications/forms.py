from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm


class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=False, label="E-posta")

    class Meta(UserCreationForm.Meta):
        model = get_user_model()
        fields = ("username", "email")
