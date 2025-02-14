from django.contrib.auth.views import PasswordChangeView
from django.views.generic.edit import UpdateView
from django.views.generic import TemplateView
from django.urls import reverse, reverse_lazy
from django.shortcuts import redirect, render

from account_module.models import Account, AccountSettings
from user_panel_module.forms import *

# Create your views here.


class UserPanelDashboard(TemplateView):
    template_name = "user_panel_module/user-panel-dashboard.html"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(reverse("login-page"))

        return super().dispatch(request, *args, **kwargs)


class UserPanelEditUser(UpdateView):
    template_name = "user_panel_module/user-panel-edit-user.html"
    success_url = reverse_lazy("edit-account-page")
    form_class = EditAccountForm
    model = Account

    def get_object(self, queryset=None):
        return self.request.user  # Automatically get the logged-in user

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(reverse("login-page"))

        return super().dispatch(request, *args, **kwargs)


class UserPanelAppearanceSettings(UpdateView):
    template_name = "user_panel_module/user-panel-appearance-settings.html"
    success_url = reverse_lazy("appearance-settings-page")
    form_class = EditAppearanceSettingsForm
    model = AccountSettings

    def get_object(self, queryset=None):
        return self.request.user.settings  # Automatically get the logged-in user

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(reverse("login-page"))

        return super().dispatch(request, *args, **kwargs)


class UserPanelChangePassword(PasswordChangeView):
    template_name = "user_panel_module/user-panel-change-password.html"
    success_url = reverse_lazy("user-panel-page")
    form_class = UserPanelChangePasswordForm

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(reverse("homework-list-page"))

        return super().dispatch(request, *args, **kwargs)


def user_panel_menu_partial(request):
    return render(request, "user_panel_module/components/user-panel-menu-partial.html")
