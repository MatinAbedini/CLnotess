from django.utils.translation import gettext_lazy as _
from django.db.models import F, Value, CharField, QuerySet
from django_jalali.db import models as jmodels
from django.db.models.functions import Concat
from django.core.exceptions import ValidationError
from django.db import models

from invitation_module.models import Invitation
from account_module.models import Account
from uuid import uuid4

# Create your models here.


class Class(models.Model):
    class_name = models.CharField(verbose_name=_("نام کلاس"), max_length=100, blank=False, null=False)
    school_name = models.CharField(verbose_name=_("نام آموزشگاه (مدرسه)"), max_length=120, null=True, blank=True)
    creation_date = jmodels.jDateTimeField(verbose_name=_("تاریخ ایجاد شدن"), auto_now_add=True, db_index=True)
    modify_date = jmodels.jDateTimeField(verbose_name=_("تاریخ ایجاد تغییر"), auto_now=True, db_index=True)
    is_delete = models.BooleanField(default=False, db_index=True, verbose_name=_("حذف شده / نشده"))
    uuid = models.UUIDField(default=uuid4, editable=False, db_index=True, verbose_name=_("شناسه"))

    created_by = models.ForeignKey(
        Account,
        verbose_name=_("ساخته شده توسط"),
        related_name="created_classes",
        on_delete=models.CASCADE,
        editable=False,
        db_index=True,
    )

    assigned_to = models.ManyToManyField(
        "account_module.Account",
        verbose_name=_("دانش آموز"),
        related_name="assigned_classes",
        blank=True
    )

    teacher = models.ManyToManyField(
        "account_module.Account",
        verbose_name=_("معلم"),
        related_name="assigned_teacher_role",
        blank=True,
    )

    def __str__(self) -> str:
        return f"کلاس {self.class_name} {self.school_name}"

    def clean(self) -> None:
        duplicated_class = Class.objects.filter(
            class_name=self.class_name,
            school_name=self.school_name,
            is_delete=False,
        )

        if duplicated_class.exists():
            raise ValidationError("کلاسی مشابه وجود دارد.")

        return super().clean()

    class Meta:
        verbose_name = _("کلاس")
        verbose_name_plural = _("کلاس ها")


    def assign_users(self, user: Account, students: QuerySet[Account] = None, teachers: QuerySet[Account] = None) -> None:
        """
        Sends Invitation for users to join a class as student.

        Args:
            user: The user who wants to send invitation.
            students: Users who will receive invitation as student.
            teachers: Users who will receive invitation as teacher.
        """

        # Find and save students and teachers using their full name
        # If they are active
        # Send invitation messages

        if students is not None:
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

            Invitation.assign_users(self, user, students, False)

        if teachers is not None:

            teachers = (
                Account.objects.annotate(
                    full_name=Concat(
                        F("first_name"), Value(" "), F("last_name"),
                        output_field=CharField()
                    )
                )
                .filter(
                    full_name__in=teachers.split(","),
                    is_active=True,
                )
            )

            Invitation.assign_users(self, user, teachers, True)
