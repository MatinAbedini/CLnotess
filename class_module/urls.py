from django.urls import path
from . import views


urlpatterns = [
    path("create", views.ClassCreateView.as_view(), name=""),
    path("add-student", views.AddStudentView.as_view(), name=""),
    path("list", views.ClassListView.as_view(), name="class-list-page")
]
