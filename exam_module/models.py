from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
from django_jalali.db import models as jmodels
from django.db.models.query import QuerySet
from django.urls import reverse
from django.db import models

from uuid import uuid4
from class_module.models import Class
from utils.validators import MaxFileSize

# Create your models here.


class Exam(models.Model):
    title = models.CharField(verbose_name=_("موضوع"), max_length=100, null=False, blank=False, db_index=True)
    description = models.TextField(verbose_name=_("توضیحات"), max_length=1500, null=False, blank=False)
    for_date = jmodels.jDateField(verbose_name=_("برای تاریخ"), null=False, blank=False)
    questions = models.IntegerField(verbose_name=_("تعداد سوالات"), default=20)
    creation_date = jmodels.jDateTimeField(verbose_name=_("تاریخ ایجاد شدن"), auto_now_add=True, db_index=True)
    modify_date = jmodels.jDateTimeField(verbose_name=_("تاریخ ویرایش"), auto_now=True)
    is_delete = models.BooleanField(verbose_name=_("حذف شده / حذف نشده"), default=False, db_index=True)
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

    assigned_class = models.ManyToManyField(
        "class_module.Class",
        verbose_name=_("برای کلاس"),
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
        verbose_name=_("سطح سختی"),
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


    def assign_exam(self, classes: QuerySet[Class]) -> None:
        """Assigns the exam to students of entered classes.

        Args:
            classes: Classes which you want to assign exam to their students.
        """

        # Create ExamCreatedFor (relation table for exam and students),
        # For each student of each classes

        duplicated_exams = (
            ExamCreatedFor.objects.filter(
                exam=self,
                assigned_class__in=self.assigned_class.all(),
                is_delete=True,
            )
        )

        duplicated_exams_assigned_to = set(duplicated_exams.values_list("assigned_to", flat=True))
        duplicated_exams_assigned_class = set(duplicated_exams.values_list("assigned_class", flat=True))

        exams: QuerySet[ExamCreatedFor] = [
            ExamCreatedFor(
                exam=self,
                assigned_class=class_,
                assigned_to=student,
                status=3
            )

            for class_ in classes
            for student in class_.assigned_to.all()
            if class_ not in duplicated_exams_assigned_class and student not in duplicated_exams_assigned_to
        ]

        # If clear is true, it will unassign old classes and students from the exam,
        # Else, it will assign new classes to the exam

        duplicated_exams.update(is_delete=False, status=3)
        ExamCreatedFor.objects.bulk_create(exams)
        self.assigned_class.add(*classes)

    def unassign_exam(self, classes: QuerySet[Class]) -> None:
        """Unassigns a exam from students of entered classes

        Args:
            classes: Classes which you want to unassign exam from it.
        """

        # Unassign exam form students of entered classes (Set is_delete to True)
        unassign_exams = (
            ExamCreatedFor.objects.filter(
                exam=self,
                assigned_class__in=classes,
                is_delete=False,
            )
        )

        unassign_exams.update(is_delete=True)
        self.assigned_class.remove(*classes)


class ExamCreatedFor(models.Model):
    creation_date = jmodels.jDateTimeField(verbose_name=_("تاریخ ایجاد شدن"), auto_now_add=True, db_index=True)
    modify_date = jmodels.jDateTimeField(verbose_name=_("تاریخ ایجاد شدن"), auto_now=True, db_index=True)
    is_delete = models.BooleanField(verbose_name=_("حذف شده / حذف نشده"), default=False, db_index=True)
    uuid = models.UUIDField(verbose_name=_("شناسه"), default=uuid4, editable=False, unique=True, db_index=True)

    status = models.IntegerField(
        verbose_name=_("وضعیت"),
        db_index=True,
        default=2,
        validators=(
            MinValueValidator(1),
            MaxValueValidator(2),
        ),
        choices=[
            (1, _("انجام شده")),
            (2, _("انجام نشده")),
        ],
    )

    exam = models.ForeignKey(
        "Exam",
        verbose_name=_("امتحان"),
        related_name="assigned_users",
        on_delete=models.CASCADE
    )

    assigned_class = models.ForeignKey(
        "class_module.Class",
        verbose_name=_("کلاس"),
        related_name="student_exams",
        on_delete=models.CASCADE
    )

    result = models.OneToOneField(
        "ExamResult",
        verbose_name=_("نتیجه امتحان"),
        related_name="exam",
        on_delete=models.SET_NULL,
        null=True,
    )

    feedback = models.OneToOneField(
        "ExamFeedback",
        verbose_name=_("بازخورد امتحان"),
        related_name="exam",
        on_delete=models.SET_NULL,
        null=True,
    )

    assigned_to = models.ForeignKey(
        "account_module.Account",
        verbose_name=_("دانش آموز"),
        related_name="assigned_exams",
        on_delete=models.CASCADE,
    )

    def __str__(self) -> str:
        return f"{self.exam.title} - {self.assigned_to}"

    def get_absolute_url(self) -> str:
        return reverse("exam-detail-page", args=[self.uuid])

    class Meta:
        verbose_name = _("کاربر معین شده برای امتحان")
        verbose_name_plural = _("کاربران معین شده برای امتحانات")


class ExamResult(models.Model):
    correct_answers = models.IntegerField(verbose_name=_("جواب های درست"), default=0, blank=False, db_index=True)
    not_answered = models.IntegerField(verbose_name=_("جواب های داده نشده"), default=0, blank=False, db_index=True)
    incorrect_answers = models.IntegerField(verbose_name=_("جواب های نادرست"), default=0, blank=False, db_index=True)
    description = models.TextField(verbose_name=_("توضیحات"), max_length=1500, null=True, blank=True)
    creation_date = jmodels.jDateTimeField(verbose_name=_("تاریخ ایجاد شدن"), auto_now_add=True, db_index=True)
    modify_date = jmodels.jDateTimeField(verbose_name=_("تاریخ ایجاد شدن"), auto_now=True, db_index=True)
    is_delete = models.BooleanField(verbose_name=_("حذف شده / نشده"), default=False, db_index=True)
    uuid = models.UUIDField(verbose_name=_("شناسه"), default=uuid4, editable=False, unique=True, db_index=True)

    result = models.IntegerField(
        verbose_name=_("نتیجه امتحان"),
        default=1,
        db_index=True,
        validators=(
            MinValueValidator(1),
            MaxValueValidator(2),
        ),
        choices=[
            (1, _("قبول شده")),
            (2, _("رد شده")),
        ],
    )

    class Meta:
        verbose_name = _("نتیجه امتحان")
        verbose_name_plural = _("نتیجه امتحانات")


class ExamFeedback(models.Model):
    description = models.TextField(verbose_name=_("توضیحات"), max_length=1500, null=True, blank=True)
    creation_date = jmodels.jDateTimeField(verbose_name=_("تاریخ ایجاد شدن"), auto_now_add=True, db_index=True)
    modify_date = jmodels.jDateTimeField(verbose_name=_("تاریخ ایجاد شدن"), auto_now=True, db_index=True)
    is_delete = models.BooleanField(verbose_name=_("حذف شده / نشده"), default=False, db_index=True)
    uuid = models.UUIDField(verbose_name=_("شناسه"), default=uuid4, editable=False, unique=True, db_index=True)

    class Meta:
        verbose_name = _("بازخورد امتحان")
        verbose_name_plural = _("بازخورد امتحان")


class ExamResultFile(models.Model):
    creation_date = jmodels.jDateTimeField(verbose_name=_("تاریخ ایجاد شدن"), auto_now_add=True, db_index=True)
    modify_date = jmodels.jDateTimeField(verbose_name=_("تاریخ ایجاد شدن"), auto_now=True, db_index=True)
    is_delete = models.BooleanField(verbose_name=_("حذف شده / حذف نشده"), default=False, db_index=True)

    exam = models.ForeignKey(
        "ExamResult",
        verbose_name=_("امتحان"),
        related_name="results",
        on_delete=models.CASCADE,
    )

    file = models.FileField(
        verbose_name=_("فایل"),
        upload_to="exam_module/exam_results/",
        validators=[MaxFileSize(3)],
        null=False,
    )

    def __str__(self):
        return f"{self.exam} - {self.file}"

    class Meta:
        verbose_name = _("فایل نتیجه امتحان")
        verbose_name_plural = _("فایل های نتیجه امتحانات")


class ExamFeedbackFile(models.Model):
    creation_date = jmodels.jDateTimeField(verbose_name=_("تاریخ ایجاد شدن"), auto_now_add=True, db_index=True)
    modify_date = jmodels.jDateTimeField(verbose_name=_("تاریخ ایجاد شدن"), auto_now=True, db_index=True)
    is_delete = models.BooleanField(verbose_name=_("حذف شده / حذف نشده"), default=False, db_index=True)

    exam = models.ForeignKey(
        "ExamFeedback",
        verbose_name=_("امتحان"),
        related_name="feedbacks",
        on_delete=models.CASCADE,
    )

    file = models.FileField(
        verbose_name=_("فایل"),
        upload_to="exam_module/exam_feedbacks/",
        validators=[MaxFileSize(3)],
        null=False,
    )

    def __str__(self):
        return f"{self.exam} - {self.file}"

    class Meta:
        verbose_name = _("فایل بازخورد امتحان")
        verbose_name_plural = _("فایل های بازخورد امتحانات")
