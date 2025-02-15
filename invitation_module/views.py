from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import ListView
from django.urls import reverse

from class_module.models import Class, ClassTeacherRole
from lesson_module.models import Lesson
from .models import Invitation, InvitationAssignedTo

# Create your views here.


class InvitationListView(ListView):
    model = Invitation
    template_name = "invitation_module/invitation-list.html"
    context_object_name = "invitations"
    ordering = "-status"
    paginate_by = 10

    def dispatch(self, request: HttpRequest, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(reverse("login-page"))

        return super().dispatch(request, *args, **kwargs)

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

        base_query = (
            InvitationAssignedTo.objects.filter(
                assigned_to=user,
                is_delete=False
            ).prefetch_related("invitation")
        )

        # Filter invitations by type, status and lesson field,
        # If user has filter invitations using them

        if type_filter != "":
            type_filter = list(map(int, type_filter.split(",")))
            base_query = base_query.filter(invitation__type__in=type_filter)

        if status_filter != "":
            status_filter = list(map(int, status_filter.split(",")))
            base_query = base_query.filter(status__in=status_filter)

        if lesson_filter != "":
            lesson_filter = lesson_filter.split(",")
            base_query = base_query.filter(lesson__name__in=lesson_filter)

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
