from django.urls import path
from .views import *

urlpatterns = [
    # Homework views
    path("create/", HomeworkCreateView.as_view(), name="create-homework-page"),
    path("list/", HomeworkListView.as_view(), name="homework-list-page"),
    path("edit/<uuid>", HomeworkUpdateView.as_view(), name="edit-homework-page"),
    path("detail/<uuid>", HomeworkDetailView.as_view(), name="homework-detail-page"),

    # Homework Result views
    path("create-result/", HomeworkResultCreateView.as_view(), name=""),
    path("result/", HomeworkResultListView.as_view(), name="create-result-homework-page"),
    path("edit-result/<uuid>", HomeworkResultUpdateView.as_view(), name=""),
    path("result-detail/<uuid>", HomeworkResultDetailView.as_view(), name="homework-result-detail-page"),

    # Actions
    path("done/<uuid>", view=done_homework, name="done-homework-page"),
    path("in-progress/<uuid>", view=in_progress_homework, name="in-progress-homework-page"),
    path("not-done/<uuid>", view=not_done_homework, name="not-done-homework-page"),
    path("delete/<uuid>", view=delete_homework, name="delete-homework-page")
]
