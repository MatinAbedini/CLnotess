from django.urls import path
from .views import *

urlpatterns = [
# Exam views
    path("create/", ExamCreateView.as_view(), name="create-exam-page"),
    path("list/", ExamListView.as_view(), name="exam-list-page"),
    path("edit/<uuid>", ExamUpdateView.as_view(), name="edit-exam-page"),
    path("detail/<uuid>", ExamDetailView.as_view(), name="exam-detail-page"),
    path("feedback/<uuid>", ExamFeedbackDetailView.as_view(), name="exam-result-page"),

    # Exam Result views
    path("create-result/<uuid>", ExamResultCreateView.as_view(), name="create-exam-result-page"),
    path("edit-result/<uuid>", ExamResultUpdateView.as_view(), name="edit-exam-result-page"),
    path("result-files/<uuid>", ExamResultFileListView.as_view(), name="exam-result-list-page"),

    # exam Feedback views
    path("create-feedback/<uuid>", ExamFeedbackCreateView.as_view(), name="create-exam-feedback-page"),
    path("edit-feedback/<uuid>", ExamFeedbackUpdateView.as_view(), name="edit-exam-feedback-page"),
    path("feedback-files/<uuid>", ExamFeedbackFileListView.as_view(), name="exam-feedback-list-page"),

    # Actions
    path("delete/<type>/<uuid>", view=delete_exam, name="delete-exam-page"),
    path("not-done/<uuid>", view=not_done_exam, name="not-done-exam-page"),
    path("done/<uuid>", view=done_exam, name="done-exam-page"),
    path("pass/<uuid>", view=pass_exam, name="pass-exam-page"),
    path("fail/<uuid>", view=fail_exam, name="fail-exam-page"),
]
