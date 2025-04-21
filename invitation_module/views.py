from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import ListView
from django.http import HttpRequest
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse

from .models import Invitation, InvitationAssignedTo
from class_module.models import Class
from lesson_module.models import Lesson

# Create your views here.


class InvitationListView(LoginRequiredMixin, ListView):
    model = Invitation
    template_name = "invitation_module/invitation-list.html"
    context_object_name = "invitations"
    ordering = "-status"
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        lessons = Lesson.objects.all().only("name")

        context["status_filter"] = self.request.GET.get("status", "")
        context["lesson_filter"] = self.request.GET.get("lesson", "")
        context["type_filter"] = self.request.GET.get("type", "")
        context["lessons"] = [lesson.name for lesson in lessons]

        return context

    def get_queryset(self):
        # Save user and used filters
        # Filters assigned and not deleted invitations

        user = self.request.user
        type_filter: str = self.request.GET.get("type", "")
        status_filter: str = self.request.GET.get("status", "")
        lesson_filter: str = self.request.GET.get("lesson", "")

        if not hasattr(self, "base_query"):
            self.base_query = (
                InvitationAssignedTo.objects.filter(
                    assigned_to=user,
                    is_delete=False
                )
                .prefetch_related("invitation")
            )

        # Filter invitations by type, status and lesson field,
        # If user has filter invitations using them

        if type_filter != "":
            type_filter = list(map(int, type_filter.split(",")))
            self.base_query = self.base_query.filter(invitation__type__in=type_filter)

        if status_filter != "":
            status_filter = list(map(int, status_filter.split(",")))
            self.base_query = self.base_query.filter(status__in=status_filter)

        if lesson_filter != "":
            lesson_filter = lesson_filter.split(",")
            self.base_query = self.base_query.filter(lesson__name__in=lesson_filter)

        return self.base_query


@login_required
def accept_invitation(request, uuid):
    """
    Accepts an invitation using entered uuid in url,
    if:
        1.user is authenticated
        2.the request is assigned to user
    """

    # Save the user
    # Save invitation, if its assigned to user

    user = request.user
    invite: InvitationAssignedTo = get_object_or_404(
        InvitationAssignedTo.objects.filter(
            assigned_to=user,
            is_delete=False,
            uuid=uuid,
        )
        .exclude(status=1)
        .prefetch_related("invitation")
        .only("status", "invitation__assigned_class", "lesson", "invitation__type")
    )

    # Check the type of invitation
    # Add user as a student to class, if type is 1
    # Add the user as a teacher to class, if type is 2

    if invite.status == 3 and invite.invitation.type == 2:
        invite.invitation.assigned_class.teacher.add(user)


    # Change the status of invite
    # Redirect the user to invitations list page

    invite.status = 1
    invite.invitation.assigned_class.assigned_to.add(user)
    invite.save()

    return redirect(reverse("invitation-list-page"))

@login_required
def reject_invitation(request, uuid):
    """
    Rejects an invitation using entered uuid in url,
    if:
        1.user is authenticated
        2.the request is assigned or created by user
    """

    # Save the user
    # Save invitation, if its assigned to user

    user = request.user
    invite: InvitationAssignedTo = get_object_or_404(
        InvitationAssignedTo.objects.filter(
            assigned_to=user,
            is_delete=False,
            uuid=uuid,
        )
        .exclude(status=2)
        .only("status")
    )

    assigned_class = (
        Class.objects.get(
            assigned_to=user,
            is_active=True,
            is_delete=False
        )
    )

    # Remove the user from assigned class

    if invite.status == 3 and invite.invitation.type == 2:
        assigned_class.teacher.remove(user)

    # Change the status of invite
    # Redirect the user to invitations list page

    assigned_class.assigned_to.remove(user)
    invite.status = 2

    assigned_class.save()
    invite.save()

    return redirect(reverse("invitation-list-page"))
