from django.utils.translation import gettext_lazy as _
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from uuid import uuid4

from account_module.models import Account
from class_module.models import Class
from lesson_module.models import Lesson

# Create your models here.


class Invitation(models.Model):
    creation_date = models.DateTimeField(verbose_name=_("تاریخ ساخت"), auto_now_add=True)
    is_active = models.BooleanField(verbose_name=_("فعال / غیرفعال"), default=True)
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
        Class,
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


class InvitationAssignedTo(models.Model):
    is_active = models.BooleanField(verbose_name=_("فعال / غیرفعال"), default=True)
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
