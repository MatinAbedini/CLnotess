from account_module.models import Account
from lesson_module.models import Lesson
from class_module.models import Class


def add_students(
        assigned_class: Class,
        user: Account,
        students: str,
        is_class_uuid: bool
    ) -> None: ...

def add_teachers(
        assigned_class: Class,
        created_by: Account,
        teachers: str,
        is_class_uuid: bool
    ) -> None: ...
