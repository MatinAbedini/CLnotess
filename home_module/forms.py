from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import gettext_lazy as _
from django_recaptcha.fields import ReCaptchaField
from .models import Account
from django import forms


class RegisterForm(UserCreationForm):
    captcha = ReCaptchaField()

    class Meta:
        model = Account
        fields = ("name", "email", "title", "message")

        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": _("نام"),
                    "data-validation":"required"
                }
            ),
            "title": forms.EmailInput(
                attrs={
                    "class": "form-control",
                    "placeholder": _("ایمیل"),
                    "data-validatio":"required"
                }
            ),
            "email": forms.EmailInput(
                attrs={
                    "class": "form-control",
                    "placeholder": _("آدرس ایمیل"),
                    "data-validatio":"email"
                }
            ),
            "message": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": _("پیام"),
                    "data-validatio":"required"
                }
            ),
        }
