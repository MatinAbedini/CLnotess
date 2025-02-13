from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import gettext_lazy as _
from django_recaptcha.fields import ReCaptchaField
from .models import Account
from django import forms


class RegisterForm(UserCreationForm):
    captcha = ReCaptchaField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["password1"].widget.attrs.update({
            "class": "form-control",
            "placeholder": _("رمز عبور"),
            "dir": "rtl",
        })

        self.fields["password2"].widget.attrs.update({
            "class": "form-control",
            "placeholder": _("تکرار رمز عبور"),
            "dir": "rtl",
        })

    class Meta:
        model = Account
        fields = ("first_name", "last_name", "username", "email")

        widgets = {
            "first_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": _("نام"),
                    "dir": "rtl",
                }
            ),
            "last_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": _("نام خانوادگی"),
                    "dir": "rtl",
                }
            ),
            "username": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": _("نام کاربری"),
                    "dir": "rtl",
                }
            ),
            "email": forms.EmailInput(
                attrs={
                    "class": "form-control",
                    "placeholder": _("ایمیل"),
                    "dir": "rtl",
                }
            ),
        }


class LoginForm(AuthenticationForm):
    captcha = ReCaptchaField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs.update({
            "class": "form-control",
            "placeholder":_("نام کاربری را وارد کنید"),
            "dir":"rtl"
        })

        self.fields["password"].widget.attrs.update({
            "class": "form-control",
            "placeholder":_("رمزعبور را وارد کنید"),
            "dir":"rtl"
        })
