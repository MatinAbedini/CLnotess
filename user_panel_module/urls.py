from django.urls import path, reverse_lazy
from django.contrib.auth.views import PasswordChangeView

from . import views

urlpatterns = [
    path("", views.UserPanelDashboard.as_view(), name="user-panel-page"),
    path("edit-account/", views.UserPanelEditUser.as_view(), name="edit-account-page"),
    path("change-email/", views.UserPanelDashboard.as_view(), name="change-email-page"),
    path("change-password/", views.UserPanelChangePassword.as_view(), name="change-password-page"),
    path("appearance-settings/", views.UserPanelAppearanceSettings.as_view(), name="appearance-settings-page"),
]
