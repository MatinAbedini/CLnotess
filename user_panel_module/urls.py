from django.urls import path
from . import views

urlpatterns = [
    path("dashboard/", views.UserPanelDashboard, name="user-panel-dashboard-page"),
]
