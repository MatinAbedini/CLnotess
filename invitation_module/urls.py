from django.urls import path
from .views import InvitationListView, accept_invitation, reject_invitation


urlpatterns = [
    path("list/", view=InvitationListView.as_view(), name="invitation-list-page"),

    # Actions
    path("accept/<uuid>", view=accept_invitation, name="accept-invitation-page"),
    path("reject/<uuid>", view=reject_invitation, name="reject-invitation-page")
]
