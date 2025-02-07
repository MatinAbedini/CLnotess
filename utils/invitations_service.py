from django.db.models.functions import Concat
from django.db.models import F, Value, CharField
from account_module.models import Account
from invitation_module.models import Invitation, InvitationAssignedTo
from lesson_module.models import Lesson


def create_student_invitations(assigned_class, created_by, assigned_users):
    """
    Creates invitations for assigned users,
    to join the class, as a student.

    Args:
        assigned_class: The class which users will receive the invitation to join.
        created_by: The user who wants to invite others to their class.
        assigned_users: Users who will receive the invitation.
    """

    # Create A new Invitation named base_invitation
    # Find assigned users using their full name, And save it as assigned_users
    # If the invitation already exists, use it instead of creating a new one

    base_invitation = Invitation.objects.filter(
        assigned_class=assigned_class,
        created_by=created_by,
        type=1
    )

    if not base_invitation.exists():
        base_invitation = Invitation(
            assigned_class=assigned_class,
            created_by=created_by,
            type=1
        )

    # Assign Invitation to students

    invitations = [
        InvitationAssignedTo(
            invitation=base_invitation,
            assigned_to=assigned_user,
        )
        for assigned_user in assigned_users
    ]

    # Save the base invitation and send (assign) the invitation to users
    base_invitation.save()
    InvitationAssignedTo.objects.bulk_create(invitations)


def create_teacher_invitations(assigned_class, created_by, teachers_lesson_list):
    """
        Creates invitations for assigned users, to join a class,
        as a teacher for the specified lesson.

    Args:
        assigned_class: The class which users will receive the invitation to join.
        created_by: The user who wants to invite others to their class.
        teachers_lesson_list: The list of teachers and their lessons.
    """

    # Create A new Invitation named base_invitation
    # Find assigned users using their full name, And save it as assigned_users
    # If the invitation already exists, use it instead of creating a new one

    base_invitation = Invitation.objects.filter(
        assigned_class=assigned_class,
        created_by=created_by,
        type=2
    )

    if not base_invitation.exists():
        base_invitation = Invitation(
            assigned_class=assigned_class,
            created_by=created_by,
            type=2
        )

    # Assign Invitation to users,
    # lesson is essential and it should be included in teachers_lesson_list
    # If its is not included, the program will raise an error

    if teachers_lesson_list is None:
        raise ValueError("""Lesson is required, make sure that:
                        You have included the lesson in the teachers_lesson_list,
                        and the structure is like this: "teacher-fullname - lesson" """)


    invitations = [
        InvitationAssignedTo(
            invitation=base_invitation,
            lesson=Lesson.objects.get(
                name=teachers_lesson.split(" - ")[1],
                is_active=True,
                is_delete=False
            ),
            assigned_to=(
                Account.objects.annotate(
                    full_name=Concat(
                        F("first_name"), Value(" "), F("last_name"),
                        output_field=CharField()
                    )
                )
                .get(
                    is_active=True,
                    full_name__in=[
                        teachers_lesson_list.split(" - ")[0]
                        for teachers_lesson_list in teachers_lesson_list
                    ],
                )
            ),
        )
        for teachers_lesson in teachers_lesson_list
    ]

    # Save the base invitation and send (assign) the invitation to users
    base_invitation.save()
    InvitationAssignedTo.objects.bulk_create(invitations)
