from django.urls import path
from .views import IndexView


urlpatterns = [
    path('', view=IndexView.as_view(), name="index-page")
]
