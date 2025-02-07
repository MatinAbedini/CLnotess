from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import ListView
from django.urls import reverse

from class_module.models import Class, ClassTeacherRole
from .models import Invitation, InvitationAssignedTo

# Create your views here.


class InvitationListView(ListView):
    model = Invitation
    template_name = "invitation_module/invitation-list.html"
    context_object_name = "invitations"
    ordering = "-status"


    def dispatch(self, request: HttpRequest, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseForbidden("شما به این صفحه دسترسی ندارید")

        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        base_query = (
            InvitationAssignedTo.objects.filter(
                assigned_to=self.request.user,
                is_active=True,
                is_delete=False
            ).prefetch_related("invitation")
        )

        return base_query


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
            is_active=True,
            is_delete=False,
            uuid=uuid
        )
        .exclude(status=1)
        .prefetch_related("invitation")
        .only("status", "invitation__assigned_class", "lesson", "invitation__type")
    )

    # Check the type of invitation
    # Add user as a student to class, if type is 1
    # Add the user as a teacher to class, if type is 2

    if invite.invitation.type == 1:
        invite.invitation.assigned_class.assigned_to.add(user)
    else:
        update_class: ClassTeacherRole = (
            ClassTeacherRole(
                teacher=user,
                assigned_class=invite.invitation.assigned_class,
                lesson=invite.lesson
            )
        )

        update_class.save()


    # Change the status of invite
    # Redirect the user to invitations list page

    invite.status = 1
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
            is_active=True,
            is_delete=False,
            uuid=uuid
        )
        .exclude(status=2)
        .only("status")
    )

    # Remove the user from assigned class

    if invite.status == 1:
        assigned_class: Class = (
            Class.objects.filter(
                assigned_to=user,
                is_active=True,
                is_delete=False
            )
            .first()
        )
        assigned_class.assigned_to.remove(user)
        assigned_class.save()

        if invite.invitation.type == 2:
            assigned_teacher_role: ClassTeacherRole = (
                ClassTeacherRole.objects.filter(
                    teacher=user,
                    for_class=assigned_class,
                    is_active=True,
                    is_delete=False
                )
                .first()
            )

            assigned_class.is_delete = True
            assigned_teacher_role.save()


    # Change the status of invite
    # Redirect the user to invitations list page

    invite.status = 2
    invite.save()

    return redirect(reverse("invitation-list-page"))
