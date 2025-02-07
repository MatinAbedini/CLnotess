from django import forms
from .models import Account
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import AuthenticationForm


class RegisterForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["password1"].widget.attrs.update({"class": "form-control"})
        self.fields["password2"].widget.attrs.update({"class": "form-control"})

    class Meta:
        model = Account
        fields = ("first_name", "last_name", "username", "email", "phone_number")

        widgets = {
            "first_name": forms.TextInput(
                attrs={"class": "form-control",}),
            "last_name": forms.TextInput(
                attrs={
                    "class": "form-control"
                }
            ),
            "username": forms.TextInput(
                attrs={
                    "class": "form-control"
                }
            ),
            "email": forms.EmailInput(
                attrs={
                    "class": "form-control"
                }
            ),
            "phone_number": forms.TextInput(
                attrs={
                    "class": "form-control"
                }
            ),
        }


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs.update({"class": "form-control"})
        self.fields["password"].widget.attrs.update({"class": "form-control"})
