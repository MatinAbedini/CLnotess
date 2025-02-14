from django.urls import path
from . import views


urlpatterns = [
    path("list/", views.ClassListView.as_view(), name="class-list-page"),
    path("create/", views.ClassCreateView.as_view(), name="create-class-page"),
    path("add-student/", views.AddStudentView.as_view(), name="add-student-class-page"),
    path("add-teacher/", views.AddTeacherView.as_view(), name="add-teacher-class-page"),

    # Actions
    path("delete/<uuid>", views.delete_class, name="delete-class-page"),
    path("leave/<uuid>", views.leave_class, name="leave-class-page"),
]
