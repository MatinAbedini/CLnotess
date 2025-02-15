from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from django_jalali.db import models as jmodels
from django.db import models
from django.urls import reverse
from uuid import uuid4

# Create your models here.


class Exam(models.Model):
    title = models.CharField(verbose_name=_("موضوع"), max_length=100, null=False, blank=False, db_index=True)
    description = models.TextField(verbose_name=_("توضیحات"), max_length=1500, null=False, blank=False)
    for_date = jmodels.jDateField(verbose_name=_("برای تاریخ"), null=False, blank=False)
    questions = models.IntegerField(verbose_name=_("تعداد سوالات"), default=20)
    creation_date = jmodels.jDateTimeField(verbose_name=_("تاریخ ایجاد شدن"), auto_now_add=True, db_index=True)
    modify_date = jmodels.jDateTimeField(verbose_name=_("تاریخ ویرایش"), auto_now=True)
    is_delete = models.BooleanField(verbose_name=_("حذف شده / حذف نشده"), default=False, db_index=True)
    is_active = models.BooleanField(verbose_name=_("فعال / غیرفعال"), default=True, db_index=True)
    uuid = models.UUIDField(verbose_name=_("شناسه"), default=uuid4, editable=False, unique=True, db_index=True)

    lesson = models.ForeignKey(
        "lesson_module.lesson",
        verbose_name=_("درس"),
        related_name="exams",
        on_delete=models.SET_DEFAULT,
        default=1,
    )

    duration = models.IntegerField(
        verbose_name=_("مدت زمان"),
        default=90,
        null=False,
        blank=False,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(1440)
        ]
    )

    created_by = models.ForeignKey(
        "account_module.Account",
        verbose_name=_("ساخته شده توسط"),
        related_name="created_exams",
        on_delete=models.SET_NULL,
        editable=False,
        null=True,
        db_index=True,
    )

    assigned_to = models.ManyToManyField(
        "class_module.Class",
        verbose_name=_("ساخته شده برای"),
        related_name="assigned_exams",
        db_index=True,
    )

    status = models.IntegerField(
        verbose_name=_("وضعیت"),
        default=1,
        db_index=True,
        choices=[
            (1, _("انجام شده")),
            (2, _("انجام نشده"))
        ],
        validators=(MinValueValidator(1), MaxValueValidator(2)),
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

    def __str__(self):
        return f"{self.title}"

    def get_absolute_url(self):
        return reverse("exam-detail-page", args=[self.uuid])

    class Meta:
        verbose_name = _("امتحان")
        verbose_name_plural = _("امتحانات")


class ExamResult(models.Model):
    correct_answers = models.IntegerField(verbose_name=_("جواب های درست"), null=False, blank=False, db_index=True)
    incorrect_answers = models.IntegerField(verbose_name=_("جواب های نادرست"), null=False, blank=False, db_index=True)
    result_description = models.TextField(verbose_name=_("توضیحات نتیجه امتحان"), max_length=1500, null=True, blank=True)
    creation_date = jmodels.jDateTimeField(verbose_name=_("تاریخ ایجاد شدن"), auto_now_add=True, db_index=True)
    modify_date = jmodels.jDateTimeField(verbose_name=_("تاریخ ایجاد شدن"), auto_now=True, db_index=True)
    is_delete = models.BooleanField(verbose_name=_("حذف شده / نشده"), default=False, db_index=True)
    uuid = models.UUIDField(verbose_name=_("شناسه"), default=uuid4, editable=False, unique=True, db_index=True)

    exam = models.ForeignKey(
        "Exam",
        verbose_name=_("امتحان"),
        related_name=_("student_results"),
        on_delete=models.CASCADE,
        db_index=True
        )

    student = models.ForeignKey(
        "account_module.Account",
        verbose_name=_("دانش آموز"),
        related_name=_("exam_results"),
        on_delete=models.CASCADE,
        db_index=True
    )

    def __str__(self) -> str:
        return  f"{self.student} - {self.exam}"

    def get_absolute_url(self):
        return reverse("exam-result", kwargs={"uuid": self.exam.uuid})

    class Meta:
        verbose_name = _("نتیجه امتحان")
        verbose_name_plural = _("نتیجه امتحانات")


class ExamResultFile(models.Model):
    creation_date = jmodels.jDateTimeField(verbose_name=_("تاریخ ایجاد شدن"), auto_now_add=True, db_index=True)
    modify_date = jmodels.jDateTimeField(verbose_name=_("تاریخ ایجاد شدن"), auto_now=True, db_index=True)
    is_delete = models.BooleanField(verbose_name=_("حذف شده / حذف نشده"), default=False, db_index=True)

    assigned_exam = models.ForeignKey(
        "ExamResult",
        verbose_name=_("امتحان نتیجه"),
        related_name="results",
        on_delete=models.CASCADE,
    )

    result_file = models.FileField(
        verbose_name=_("فایل های نتیجه امتحان"),
        upload_to="exam_module/exam_results/",
        null=True,
    )

    def __str__(self):
        return f"{self.assigned_exam} - {self.result_file}"

    class Meta:
        verbose_name = _("فایل نتیجه امتحان")
        verbose_name_plural = _("فایل های نتیجه امتحان")
