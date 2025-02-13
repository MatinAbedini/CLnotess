from django.urls import path, include
from . import views

urlpatterns = [
    path("register/", views.RegisterView.as_view(), name="register-page"),
    path("login/", views.LoginView.as_view(), name="login-page"),
    path("logout/", views.logout_view, name="logout-page"),
    path('active-account/<active_code>', views.activation_view, name='active-account-page'),
]
