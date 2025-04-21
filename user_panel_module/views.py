from django.utils.translation import gettext_lazy as _
from django.contrib.auth.views import PasswordChangeView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import UpdateView
from django.urls import reverse_lazy
from django.shortcuts import render

from account_module.models import Account, AccountSettings
from user_panel_module.forms import *
from utils.mail_service import send_mail_service

# Create your views here.


class UserPanelEditUser(LoginRequiredMixin, UpdateView):
    template_name = "user_panel_module/user-panel-edit-user.html"
    success_url = reverse_lazy("edit-account-page")
    form_class = EditAccountForm
    model = Account

    def get_object(self, queryset=None):
        return self.request.user  # Automatically gets the logged-in user


class UserPanelAppearanceSettings(LoginRequiredMixin, UpdateView):
    template_name = "user_panel_module/user-panel-appearance-settings.html"
    success_url = reverse_lazy("appearance-settings-page")
    form_class = EditAppearanceSettingsForm
    model = AccountSettings

    def get_object(self, queryset=None):
        return self.request.user.settings   # Automatically get the logged-in user's settings


class UserPanelChangePassword(LoginRequiredMixin, PasswordChangeView):
    template_name = "user_panel_module/user-panel-change-password.html"
    success_url = reverse_lazy("user-panel-page")
    form_class = UserPanelChangePasswordForm


class UserPanelEmailPassword(LoginRequiredMixin, UpdateView):
    template_name = "user_panel_module/user-panel-change-password.html"
    success_url = reverse_lazy("user-panel-page")
    form_class = UserPanelChangeEmailForm
    model = Account

    def get_object(self, queryset=None):
        return self.request.user   # Automatically get the logged-in user

    def form_valid(self, form):
        old_email = form.cleaned_data.get("old_email")
        new_email = form.cleaned_data.get("new_email")

        if old_email != self.request.user.email:
            form.add_error("old_email", _(".ایمیلی که وارد کرده اید با ایمیل شما مطابقت نمی باشد"))
            return self.form_invalid(form)

        send_mail_service(_("تغییر ایمیل"), "", [new_email], {"": ""})

        return super().form_valid(form)


def user_panel_menu_partial(request):
    return render(request, "user_panel_module/components/user-panel-menu-partial.html")
