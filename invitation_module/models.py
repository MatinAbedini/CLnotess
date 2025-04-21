from django.utils.translation import gettext_lazy as _
from django.core.validators import MaxValueValidator, MinValueValidator
from account_module.models import Account
from django_jalali.db import models as jmodels
from django.db import models
from uuid import uuid4

# Create your models here.


class Invitation(models.Model):
    creation_date = jmodels.jDateTimeField(verbose_name=_("تاریخ ساخت"), auto_now_add=True)
    is_delete = models.BooleanField(verbose_name=_("حدف شده / نشده"), default=False)

    type = models.IntegerField(
        verbose_name=_("نوع"),
        default=1,
        choices=[
            (1, _("عضویت دانش آموز")),
            (2, _("عضویت معلم"))
        ],
        validators=[MinValueValidator(1), MaxValueValidator(2)]
    )

    assigned_class = models.ForeignKey(
        "class_module.Class",
        on_delete=models.CASCADE,
        related_name="assigned_invitations",
        verbose_name=_("معین شده برای کلاس"),
        null=True
    )

    created_by = models.ForeignKey(
        Account,
        verbose_name=_("ساخته شده توسط"),
        related_name="created_invitations",
        on_delete=models.SET_NULL,
        null=True,
        db_index=True,
    )


    class Meta:
        verbose_name = _("درخواست")
        verbose_name_plural = _("درخواست ها")

    def __str__(self):
        return f"{self.pk} - {self.created_by}"


    def assign_users(assigned_class, created_by, assigned_users, is_teacher=False):
        """
        Creates invitations for assigned users,
        to join the class, as a student.

        Args:
            assigned_class: The class which users will receive the invitation to join.
            created_by: The user who wants to invite others to their class.
            assigned_users: Users who will receive the invitation.
            is_teacher: If the invitation is for teachers. Default = False
        """

        # Create A new Invitation named base_invitation
        # Find assigned users using their full name, And save it as assigned_users
        # If the invitation already exists, use it instead of creating a new one

        type = 2 if is_teacher else 1

        base_invitation = Invitation.objects.filter(
            assigned_class=assigned_class,
            created_by=created_by,
            type=type
        )

        if not base_invitation.exists():
            base_invitation = Invitation(
                assigned_class=assigned_class,
                created_by=created_by,
                type=type
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


class InvitationAssignedTo(models.Model):
    is_delete = models.BooleanField(verbose_name=_("حدف شده / نشده"), default=False)
    uuid = models.UUIDField(verbose_name=_("شناسه"), default=uuid4, editable=False, unique=True, db_index=True)

    invitation = models.ForeignKey(
        Invitation,
        on_delete=models.CASCADE,
        related_name="assigned_to",
        verbose_name=_("ریکوئست")
    )

    assigned_to = models.ForeignKey(
        Account,
        on_delete=models.CASCADE,
        related_name="assigned_invitation",
        verbose_name=_("معین شده برای")
    )

    lesson = models.ForeignKey(
        "lesson_module.Lesson",
        verbose_name=_("درس"),
        related_name="invitations",
        on_delete=models.CASCADE,
        null=True
    )

    status = models.IntegerField(
        verbose_name=_("وضعیت"),
        default=3,
        choices=[
            (1, _("قبول شده")),
            (2, _("رد شده")),
            (3, _("در انتظار"))
        ],
        validators=[MinValueValidator(1), MaxValueValidator(3)]
        )

    class Meta:
        verbose_name = _("کاربران معین شده برای درخواست")
        verbose_name_plural = _("کاربر معین شده برای درخواست")

    def __str__(self):
        return f"{self.invitation} - {self.assigned_to}"
