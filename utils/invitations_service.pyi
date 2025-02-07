from account_module.models import Account
from lesson_module.models import Lesson
from class_module.models import Class
from django.db.models import QuerySet


def create_student_invitations(
        assigned_class: Class,
        created_by: Account,
        assigned_users: QuerySet[Account],
    ) -> None: ...


def create_teacher_invitations(
        assigned_class: Class,
        created_by: Account,
        teachers_lesson_list: list[str] | None = None,
    ) -> None: ...
