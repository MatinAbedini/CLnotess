from django.utils.translation import gettext_lazy as _
from django.contrib.auth.forms import PasswordChangeForm
from django_recaptcha.fields import ReCaptchaField
from django import forms

from account_module.models import Account, AccountSettings


class EditAccountForm(forms.ModelForm):
    captcha = ReCaptchaField()

    class Meta:
        model = Account
        fields = ("first_name", "last_name", "username", "profile_image")
        labels = {
            "first_name": _("نام کوچک"),
            "last_name": _("نام خانوادگی"),
            "username": _("نام کاربری"),
            "profile_image": _("تصویر پروفایل"),
        }

        widgets = {
            "first_name": forms.TextInput(attrs={
                "class": "form-control filled-input rounded-input",
                "placeholder": _("نام کوچک"),
                "dir": "rtl",
            }),
            "last_name": forms.TextInput(attrs={
                "class": "form-control filled-input rounded-input",
                "placeholder": _("نام خانوادگی"),
                "dir": "rtl",
            }),
            "username": forms.TextInput(attrs={
                "class": "form-control filled-input rounded-input",
                "placeholder": _("نام کاربری"),
                "dir": "rtl",
            }),
        }


class EditAppearanceSettingsForm(forms.ModelForm):
    class Meta:
        model = AccountSettings
        fields = ("sidebar_navbar_theme", "sidebar_primary_color")
        labels = {
            "sidebar_navbar_theme": _("تم خارجی"),
            "sidebar_primary_color": _("رنگ بندی نوار کناری"),
        }

        widgets = {
            "sidebar_navbar_theme": forms.Select(attrs={
                "class": "form-control",
                "dir": "rtl",
            }),
            "sidebar_primary_color": forms.Select(attrs={
                "class": "form-control",
                "dir": "rtl",
            }),
        }


class UserPanelChangePasswordForm(PasswordChangeForm):
    captcha = ReCaptchaField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["old_password"].widget.attrs.update({
            "class": "form-control",
            "placeholder":_("رمز عبور قبلی"),
            "dir":"rtl"
        })

        self.fields["new_password1"].widget.attrs.update({
            "class": "form-control",
            "placeholder":_("رمزعبور جدید"),
            "dir":"rtl"
        })

        self.fields["new_password2"].widget.attrs.update({
            "class": "form-control",
            "placeholder":_("تکرار رمزعبور جدید"),
            "dir":"rtl"
        })


class UserPanelChangeEmailForm(forms.ModelForm):
    captcha = ReCaptchaField()
    old_email = forms.EmailField(
        required=True,
        label=_("ایمیل قبلی"),
        widget=forms.EmailInput(attrs={
            "class": "form-control",
            "placeholder":_("ایمیل قبلی"),
            "dir":"rtl"
        })
    )

    class Meta:
        model = Account
        fields = ("email",)
        labels = {
            "email": _("ایمیل جدید"),
        }

        widgets = {
            "email": forms.EmailInput(attrs={
                "class": "form-control",
                "placeholder":_("ایمیل جدید"),
                "dir":"rtl"
            }),
        }
