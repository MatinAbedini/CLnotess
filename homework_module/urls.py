from django.urls import path
from .views import *

urlpatterns = [
    # Homework views
    path("create/", HomeworkCreateView.as_view(), name="create-homework-page"),
    path("list/", HomeworkListView.as_view(), name="homework-list-page"),
    path("edit/<uuid>", HomeworkUpdateView.as_view(), name="edit-homework-page"),
    path("detail/<uuid>", HomeworkDetailView.as_view(), name="homework-detail-page"),

    # Homework Result views
    path("create-result/", HomeworkResultCreateView.as_view(), name="create-homework-result-page"),
    path("create-result/<uuid>", HomeworkResultCreateView.as_view(), name="create-homework-result-page"),
    path("result-files/", HomeworkResultFileListView.as_view(), name="homework-result-list-page"),
    path("result-files/<uuid>", HomeworkResultFileListView.as_view(), name="homework-result-list-page"),
    path("create-feedback/", HomeworkFeedbackCreateView.as_view(), name="create-homework-feedback-page"),
    path("create-feedback/<uuid>", HomeworkFeedbackCreateView.as_view(), name="create-homework-feedback-page"),
    path("feedback-files/", HomeworkFeedbackFileListView.as_view(), name="homework-feedback-list-page"),
    path("feedback-files/<uuid>", HomeworkFeedbackFileListView.as_view(), name="homework-feedback-list-page"),
    path("edit-result/<uuid>", HomeworkFeedbackUpdateView.as_view(), name="edit-homework-feedback-page"),
    path("edit-feedback/<uuid>", HomeworkFeedbackUpdateView.as_view(), name="edit-homework-feedback-page"),

    # Actions
    path("done/<uuid>", view=done_homework, name="done-homework-page"),
    path("in-progress/<uuid>", view=in_progress_homework, name="in-progress-homework-page"),
    path("not-done/<uuid>", view=not_done_homework, name="not-done-homework-page"),
    path("delete/<uuid>", view=delete_homework, name="delete-homework-page"),
    path("download/r/<uuid>", view=download_homework_result, name="download-result-homework-page"),
    path("download/f/<uuid>", view=download_homework_feedback, name="download-feedback-homework-page")
]
