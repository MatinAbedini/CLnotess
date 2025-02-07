from .invitations_service import create_student_invitations, create_teacher_invitations
from django.db.models.functions import Concat
from django.db.models import F, Value, CharField
from account_module.models import Account
from class_module.models import Class


def add_students(assigned_class, user, students, is_class_uuid):
    """
    Sends Invitation for users to join a class as student.

    Args:
        class_uuid: The uuid of the class.
        user: The user who wants to send invitation.
        students: Users who will receive invitation.
        is_class_uuid: If the class is identified by its uuid.
    """

    # If the class is identified by its uuid (is_class_uuid=True)
    # Save the class using its uuid as assigned_class
    # If its active, its not deleted and its created by the user

    if is_class_uuid:
        assigned_class: Class = (
            Class.objects.get(
                created_by=user,
                uuid=assigned_class,
                is_active=True,
                is_delete=False
            )
        )


    # Find and save students with their full name
    # If they are active

    students = (
        Account.objects.annotate(
            full_name=Concat(
                F("first_name"), Value(" "), F("last_name"),
                output_field=CharField()
            )
        )
        .filter(
            full_name__in=students.split(","),
            is_active=True,
        )
    )


    # Send the invitation
    create_student_invitations(assigned_class, user, students)


def add_teachers(assigned_class, user, teachers: str, is_class_uuid):
    """
    Sends Invitation for users to join a class as teacher.

    Args:
        class_uuid: The uuid of the class.
        user: The user who wants to send invitation.
        teachers: Users who will receive invitation.
        is_class_uuid: If the class is identified by its uuid.
    """

    # If the class is identified by its uuid (is_class_uuid=True)
    # Save the class using its uuid as assigned_class
    # If its active, its not deleted and its created by the user

    if is_class_uuid:
        assigned_class: Class = (
            Class.objects.get(
                created_by=user,
                uuid=assigned_class,
                is_active=True,
                is_delete=False
            )
        )


    # Send the invitation
    create_teacher_invitations(assigned_class, user, teachers.split(","))
