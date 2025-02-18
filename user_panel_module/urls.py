from django.urls import path

from . import views

urlpatterns = [
    path("edit-account/", views.UserPanelEditUser.as_view(), name="edit-account-page"),
    path("change-email/", views.UserPanelChangeEmailForm.as_view(), name="change-email-page"),
    path("change-password/", views.UserPanelChangePassword.as_view(), name="change-password-page"),
    path("appearance-settings/", views.UserPanelAppearanceSettings.as_view(), name="appearance-settings-page"),
]
