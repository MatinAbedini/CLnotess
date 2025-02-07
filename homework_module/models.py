from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
from account_module import models as account_models
from django.db import models
from django.urls import reverse
from uuid import uuid4


# Create your models here.

class Homework(models.Model):
    title = models.CharField(verbose_name=_("موضوع"), max_length=100, null=False, blank=False, db_index=True)
    description = models.TextField(verbose_name=_("توضیحات"), max_length=1500, null=False, blank=False)
    creation_date = models.DateField(verbose_name=_("تاریخ ایجاد شدن"), auto_now_add=True, db_index=True)
    modify_date = models.DateField(verbose_name=_("تاریخ ایجاد شدن"), auto_now=True, db_index=True)
    for_date = models.DateField(verbose_name=_("برای تاریخ"), null=False, blank=False)
    is_active = models.BooleanField(verbose_name=_("فعال / غیرفعال"), default=True, db_index=True)
    is_delete = models.BooleanField(verbose_name=_("حذف شده / حذف نشده"), default=False, db_index=True)
    uuid = models.UUIDField(verbose_name=_("شناسه"), default=uuid4, editable=False, unique=True, db_index=True)

    created_by = models.ForeignKey(
        account_models.Account,
        verbose_name=_("ساخته شده توسط"),
        related_name="created_homeworks",
        on_delete=models.SET_NULL,
        # editable=False,
        null=True,
        db_index=True,
    )

    difficulty = models.IntegerField(
        verbose_name=_("سطح ساخته"),
        default=1,
        db_index=True,
        choices=[
            (1, _("ساده")),
            (2, _("متوسط")),
            (3, _("سخت"))
        ],
        validators=(MinValueValidator(1), MaxValueValidator(3))
    )


    def __str__(self) -> str:
        return f"{self.title}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        homework_created_for_exists = (
            HomeworkCreatedFor.objects.filter(
                homework=self,
                assigned_to=self.created_by
            )
            .exists()
         )
        
        if not homework_created_for_exists:
            HomeworkCreatedFor(
                assigned_to=self.created_by,
                homework=self
            ).save()

    def get_absolute_url(self) -> str:
        return reverse("homework-detail-page", args=[self.uuid])

    class Meta:
        verbose_name = _("تکلیف")
        verbose_name_plural = _("تکالیف")


class HomeworkCreatedFor(models.Model):
    uuid = models.UUIDField(verbose_name=_("شناسه"), default=uuid4, editable=False, unique=True, db_index=True)


    homework = models.ForeignKey(
        "Homework",
        verbose_name=_("تکلیف"),
        related_name="for_class",
        on_delete=models.CASCADE
    )

    assigned_to = models.ForeignKey(
        "account_module.Account",
        verbose_name=_("دانش آموز"),
        related_name="assigned_homewrok",
        on_delete=models.CASCADE,
    )

    status = models.IntegerField(
        verbose_name=_("وضعیت"),
        default=3,
        db_index=True,
        validators=(
            MinValueValidator(1),
            MaxValueValidator(3),
        ),
        choices=[
            (1, _("انجام شده")),
            (2, _("درحال انجام")),
            (3, _("انجام نشده")),
        ],
    )


    def __str__(self) -> str:
        return f"{self.homework.title} - {self.assigned_to}"

    def get_absolute_url(self) -> str:
        return reverse("homework-detail-page", args=[self.uuid])

    class Meta:
        verbose_name = _("کاربر معین شده برای تکلیف")
        verbose_name_plural = _("کاربران معین شده برای تکلیف")


class HomeworkResult(models.Model):
    is_active = models.BooleanField(verbose_name=_("فعال / غیرفعال"), default=True, db_index=True)
    is_delete = models.BooleanField(verbose_name=_("حذف شده / نشده"), default=False, db_index=True)
    uuid = models.UUIDField(verbose_name=_("شناسه"), default=uuid4, editable=False, unique=True, db_index=True)


    homework = models.ForeignKey(
        "Homework",
        verbose_name=_("امتحان"),
        related_name=_("student_results"),
        on_delete=models.CASCADE,
        db_index=True
        )

    student = models.ForeignKey(
        "account_module.Account",
        verbose_name=_("دانش آموز"),
        related_name=_("homework_results"),
        on_delete=models.CASCADE,
        db_index=True
    )

    result = models.FileField(
        verbose_name=_("نتیجه تکلیف"),
        upload_to="homework_module/homework_results/",
        null=False,
        blank=False
    )

    status = models.IntegerField(
        verbose_name=_("نتیجه"),
        default=2,
        db_index=True,
        validators=(
            MinValueValidator(1),
            MaxValueValidator(2),
        ),
        choices=[
            (1, _("ناقص")),
            (2, _("کامل")),
        ],
    )


    class Meta:
        verbose_name = _("نتیجه امتحان")
        verbose_name_plural = _("نتیجه امتحانات")

    def __str__(self) -> str:
        return  f"{self.student} - {self.homework}"

    def get_absolute_url(self):
        return reverse("homework-result-detail-page", kwargs={"uuid": self.uuid})
