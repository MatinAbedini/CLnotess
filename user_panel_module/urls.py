from django.urls import path
from . import views

urlpatterns = [
    path("", views.UserPanelDashboard.as_view(), name="user-panel-page"),
    path("edit-account/", views.UserPanelDashboard.as_view(), name="edit-account-page"),
    path("change-email/", views.UserPanelDashboard.as_view(), name="change-email-page"),
    path("change-password/", views.UserPanelDashboard.as_view(), name="change-password-page"),
    path("appearance-settings/", views.UserPanelDashboard.as_view(), name="appearance-settings-page"),
]
