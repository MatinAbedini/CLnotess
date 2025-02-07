from django.urls import path
from .views import *

urlpatterns = [
    # Exam views
    path("create-exam/", ExamCreateView.as_view(), name="create-exam-page"),
    path("update-exam/<uuid>", ExamUpdateView.as_view(), name="update-exam-page"),
    path("exams-list/", ExamListView.as_view(), name="exam-list-page"),
    path("exam-detail/<uuid>", ExamDetailView.as_view(), name="exam-detail-page"),

    # Exam Result views
    path("create-result/", ExamResultCreateView.as_view(), name=""),
    path("edit-result/<uuid>", ExamResultUpdateView.as_view(), name=""),
    path("result/<uuid>", ExamResultDetailView.as_view(), name=""),

    # Actions
    path("done/<uuid>", view=done_exam, name="done-exam-page"),
    path("not-done/<uuid>", view=not_done_exam, name="not-done-exam-page"),
    path("delete/<uuid>", view=delete_exam, name="delete-exam-page")
]
