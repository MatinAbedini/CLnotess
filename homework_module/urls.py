from django.urls import path
from .views import *

urlpatterns = [
    # Homework views
    path("create/", HomeworkCreateView.as_view(), name="create-homework-page"),
    path("list/", HomeworkListView.as_view(), name="homework-list-page"),
    path("edit/<uuid>", HomeworkUpdateView.as_view(), name="edit-homework-page"),
    path("detail/<uuid>", HomeworkDetailView.as_view(), name="homework-detail-page"),
    path("result/<uuid>", HomeworkResultDetailView.as_view(), name="homework-result-page"),

    # Homework Result views
    path("create-result/<uuid>", HomeworkResultCreateView.as_view(), name="create-homework-result-page"),
    path("edit-result/<uuid>", HomeworkResultUpdateView.as_view(), name="edit-homework-result-page"),
    path("result-files/<uuid>", HomeworkResultFileListView.as_view(), name="homework-result-list-page"),

    # Homework Feedback views
    path("create-feedback/<uuid>", HomeworkFeedbackCreateView.as_view(), name="create-homework-feedback-page"),
    path("edit-feedback/<uuid>", HomeworkFeedbackUpdateView.as_view(), name="edit-homework-feedback-page"),
    path("feedback-files/<uuid>", HomeworkFeedbackFileListView.as_view(), name="homework-feedback-list-page"),

    # Actions
    path("done/<uuid>", view=done_homework, name="done-homework-page"),
    path("in-progress/<uuid>", view=in_progress_homework, name="in-progress-homework-page"),
    path("not-done/<uuid>", view=not_done_homework, name="not-done-homework-page"),
    path("complete/<uuid>", view=complete_homework, name="complete-homework-page"),
    path("waiting/<uuid>", view=waiting_homework, name="waiting-homework-page"),
    path("not-complete/<uuid>", view=not_complete_homework, name="not-complete-homework-page"),
    path("delete/<type>/<uuid>", view=delete_homework, name="delete-homework-page"),
]
