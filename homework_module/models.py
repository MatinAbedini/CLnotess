from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
from account_module import models as account_models
from django_jalali.db import models as jmodels
from utils.validators import validate_file_size
from django.urls import reverse
from django.db import models
from uuid import uuid4

# Create your models here.


class Homework(models.Model):
    title = models.CharField(verbose_name=_("موضوع"), max_length=100, null=False, blank=False, db_index=True)
    description = models.TextField(verbose_name=_("توضیحات"), max_length=1500, null=False, blank=False)
    creation_date = jmodels.jDateTimeField(verbose_name=_("تاریخ ایجاد شدن"), auto_now_add=True, db_index=True)
    modify_date = jmodels.jDateTimeField(verbose_name=_("تاریخ ایجاد تغییر"), auto_now=True, db_index=True)
    for_date = jmodels.jDateField(verbose_name=_("برای تاریخ"), null=False, blank=False)
    is_delete = models.BooleanField(verbose_name=_("حذف شده / حذف نشده"), default=False, db_index=True)
    uuid = models.UUIDField(verbose_name=_("شناسه"), default=uuid4, editable=False, unique=True, db_index=True)

    lesson = models.ForeignKey(
        "lesson_module.lesson",
        verbose_name=_("درس"),
        related_name="homeworks",
        on_delete=models.SET_DEFAULT,
        default=1,
    )

    created_by = models.ForeignKey(
        account_models.Account,
        verbose_name=_("ساخته شده توسط"),
        related_name="created_homeworks",
        on_delete=models.SET_NULL,
        editable=False,
        null=True,
        db_index=True,
    )

    def __str__(self) -> str:
        return f"{self.title}"

    def get_absolute_url(self) -> str:
        return reverse("homework-detail-page", args=[self.uuid])

    class Meta:
        verbose_name = _("تکلیف")
        verbose_name_plural = _("تکالیف")


class HomeworkCreatedFor(models.Model):
    creation_date = jmodels.jDateTimeField(verbose_name=_("تاریخ ایجاد شدن"), auto_now_add=True, db_index=True)
    modify_date = jmodels.jDateTimeField(verbose_name=_("تاریخ ایجاد شدن"), auto_now=True, db_index=True)
    uuid = models.UUIDField(verbose_name=_("شناسه"), default=uuid4, editable=False, unique=True, db_index=True)

    status = models.IntegerField(
        verbose_name=_("وضعیت"),
        db_index=True,
        default=3,
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

    homework = models.ForeignKey(
        "Homework",
        verbose_name=_("تکلیف"),
        related_name="for_class",
        on_delete=models.CASCADE
    )

    assigned_class = models.ForeignKey(
        "class_module.Class",
        verbose_name=_("کلاس"),
        related_name="student_homeworks",
        on_delete=models.CASCADE
    )

    result = models.OneToOneField(
        "HomeworkResult",
        verbose_name=_("نتیجه تکلیف"),
        related_name="homework",
        on_delete=models.SET_NULL,
        null=True,
    )

    feedback = models.OneToOneField(
        "HomeworkFeedback",
        verbose_name=_("بازخورد تکلیف"),
        related_name="homework",
        on_delete=models.SET_NULL,
        null=True,
    )

    assigned_to = models.ForeignKey(
        "account_module.Account",
        verbose_name=_("دانش آموز"),
        related_name="assigned_homework",
        on_delete=models.CASCADE,
    )

    def __str__(self) -> str:
        return f"{self.homework.title} - {self.assigned_to}"

    def get_absolute_url(self) -> str:
        return reverse("homework-detail-page", args=[self.uuid])

    class Meta:
        verbose_name = _("کاربر معین شده برای تکلیف")
        verbose_name_plural = _("کاربران معین شده برای تکلیف")


class HomeworkResult(models.Model):
    description = models.TextField(verbose_name=_("توضیحات نتیجه تکلیف"), max_length=1500, null=True, blank=True)
    creation_date = jmodels.jDateTimeField(verbose_name=_("تاریخ ایجاد شدن"), auto_now_add=True, db_index=True)
    modify_date = jmodels.jDateTimeField(verbose_name=_("تاریخ ایجاد شدن"), auto_now=True, db_index=True)
    is_delete = models.BooleanField(verbose_name=_("حذف شده / حذف نشده"), default=False, db_index=True)

    result_status = models.IntegerField(
        verbose_name=_("وضعیت نتیجه تکلیف"),
        default=2,
        db_index=True,
        validators=(
            MinValueValidator(1),
            MaxValueValidator(2),
        ),
        choices=[
            (1, _("کامل")),
            (2, _("در انتظار")),
            (3, _("ناقص")),
        ],
    )

    class Meta:
        verbose_name = _("نتیجه تکلیف")
        verbose_name_plural = _("نتیجه تکالیف")


class HomeworkFeedback(models.Model):
    description = models.TextField(verbose_name=_("توضیحات بازخورد تکلیف"), max_length=1500, null=True, blank=True)
    creation_date = jmodels.jDateTimeField(verbose_name=_("تاریخ ایجاد شدن"), auto_now_add=True, db_index=True)
    modify_date = jmodels.jDateTimeField(verbose_name=_("تاریخ ایجاد شدن"), auto_now=True, db_index=True)
    is_delete = models.BooleanField(verbose_name=_("حذف شده / نشده"), default=False, db_index=True)
    uuid = models.UUIDField(verbose_name=_("شناسه"), default=uuid4, editable=False, unique=True, db_index=True)

    class Meta:
        verbose_name = _("بازخورد تکلیف")
        verbose_name_plural = _("بازخورد تکالیف")


class HomeworkResultFile(models.Model):
    creation_date = jmodels.jDateTimeField(verbose_name=_("تاریخ ایجاد شدن"), auto_now_add=True, db_index=True)
    modify_date = jmodels.jDateTimeField(verbose_name=_("تاریخ ایجاد شدن"), auto_now=True, db_index=True)
    is_delete = models.BooleanField(verbose_name=_("حذف شده / حذف نشده"), default=False, db_index=True)

    homework = models.ForeignKey(
        "HomeworkResult",
        verbose_name=_("تکلیف"),
        related_name="results",
        on_delete=models.CASCADE,
        db_index=True,
    )

    file = models.FileField(
        verbose_name=_("فایل های نتیجه تکلیف"),
        upload_to="homework_module/homework_results/",
        validators=[validate_file_size],
        db_index=True,
    )

    def __str__(self):
        return f"{self.homework}"

    class Meta:
        verbose_name = _("فایل نتیجه تکلیف")
        verbose_name_plural = _("فایل های نتیجه تکلیف")


class HomeworkFeedbackFile(models.Model):
    creation_date = jmodels.jDateTimeField(verbose_name=_("تاریخ ایجاد شدن"), auto_now_add=True, db_index=True)
    modify_date = jmodels.jDateTimeField(verbose_name=_("تاریخ ایجاد شدن"), auto_now=True, db_index=True)
    is_delete = models.BooleanField(verbose_name=_("حذف شده / حذف نشده"), default=False, db_index=True)

    homework = models.ForeignKey(
        "HomeworkFeedback",
        verbose_name=_("تکلیف"),
        related_name="feedbacks",
        on_delete=models.CASCADE,
        db_index=True,
    )

    file = models.FileField(
        verbose_name=_("فایل های بازخورد تکلیف"),
        upload_to="homework_module/homework_results/",
        validators=[validate_file_size],
        db_index=True,
    )

    def __str__(self):
        return f"{self.homework}"

    class Meta:
        verbose_name = _("فایل بازخورد تکلیف")
        verbose_name_plural = _("فایل های بازخورد تکلیف")
