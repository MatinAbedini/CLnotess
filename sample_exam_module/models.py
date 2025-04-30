from django.utils.translation import gettext_lazy as _
from django_jalali.db import models as jmodels
from django.urls import reverse
from django.db import models

from utils.validators import MaxFileSize
from uuid import uuid4


# Create your models here.


class SampleExam(models.Model):
    title = models.CharField(verbose_name=_("موضوع"), max_length=100, null=False, blank=False, db_index=True)
    text = models.TextField(verbose_name=_("متن"), max_length=10000, null=True, blank=True)
    creation_date = jmodels.jDateTimeField(verbose_name=_("تاریخ ایجاد شدن"), auto_now_add=True, db_index=True)
    modify_date = jmodels.jDateTimeField(verbose_name=_("تاریخ ویرایش"), auto_now=True)
    is_delete = models.BooleanField(verbose_name=_("حذف شده / حذف نشده"), default=False, db_index=True)
    uuid = models.UUIDField(verbose_name=_("شناسه"), default=uuid4, editable=False, unique=True, db_index=True)

    lesson = models.ForeignKey(
        "lesson_module.lesson",
        verbose_name=_("درس"),
        related_name="sample_exams",
        on_delete=models.SET_DEFAULT,
        default=1,
    )

    created_by = models.ForeignKey(
        "account_module.Account",
        verbose_name=_("ساخته شده توسط"),
        related_name="created_sample_exams",
        on_delete=models.SET_NULL,
        editable=False,
        null=True,
        db_index=True,
    )

    assigned_class = models.ManyToManyField(
        "class_module.Class",
        verbose_name=_("برای کلاس"),
        related_name="assigned_sample_exams",
        db_index=True,
    )

    assigned_to = models.ForeignKey(
        "account_module.Account",
        verbose_name=_("دانش آموز"),
        related_name="assigned_sample_exams",
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = _("نمونه سوال امتحانی")
        verbose_name_plural = _("نمونه سوالات امتحانی")

    def __str__(self) -> str:
        return self.title

    def get_absolute_url(self):
        return reverse("sample_exam_detail", kwargs={"uuid": self.uuid})


class SampleExamFiles(models.Model):
    creation_date = jmodels.jDateTimeField(verbose_name=_("تاریخ ایجاد شدن"), auto_now_add=True, db_index=True)
    modify_date = jmodels.jDateTimeField(verbose_name=_("تاریخ ایجاد شدن"), auto_now=True, db_index=True)
    is_delete = models.BooleanField(verbose_name=_("حذف شده / حذف نشده"), default=False, db_index=True)

    sample_exam = models.ForeignKey(
        "SampleExam",
        verbose_name=_("نمونه سوال امتحانی"),
        related_name="files",
        on_delete=models.CASCADE,
    )

    file = models.FileField(
        verbose_name=_("فایل"),
        upload_to="sample_exam_module/",
        validators=[MaxFileSize(3)],
        null=False,
    )

    class Meta:
        verbose_name = _("فایل نمونه سوال امتحانی")
        verbose_name_plural = _("فایل های نمونه سوالات امتحانی")

    def __str__(self) -> str:
        return f"{self.sample_exam.tile} - {self.file}"
