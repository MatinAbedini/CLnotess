from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
from django_jalali.db import models as jmodels
from django.db.models.query import QuerySet
from django.urls import reverse
from django.db import models

from utils.validators import MaxFileSize
from class_module.models import Class
from uuid import uuid4

# Create your models here.


class Homework(models.Model):
    title = models.CharField(verbose_name=_("موضوع"), max_length=100, null=False, blank=False, db_index=True)
    description = models.TextField(verbose_name=_("توضیحات"), max_length=1500, null=False, blank=False)
    for_date = jmodels.jDateField(verbose_name=_("برای تاریخ"), null=False, blank=False)
    creation_date = jmodels.jDateTimeField(verbose_name=_("تاریخ ایجاد شدن"), auto_now_add=True, db_index=True)
    modify_date = jmodels.jDateTimeField(verbose_name=_("تاریخ ایجاد تغییر"), auto_now=True, db_index=True)
    is_delete = models.BooleanField(verbose_name=_("حذف شده / حذف نشده"), default=False, db_index=True)
    uuid = models.UUIDField(verbose_name=_("شناسه"), default=uuid4, editable=False, unique=True, db_index=True)

    lesson = models.ForeignKey(
        "lesson_module.Lesson",
        verbose_name=_("درس"),
        related_name="homeworks",
        on_delete=models.CASCADE,
        default=1,
    )

    created_by = models.ForeignKey(
        "account_module.Account",
        verbose_name=_("ساخته شده توسط"),
        related_name="created_homeworks",
        on_delete=models.SET_NULL,
        editable=False,
        null=True,
        db_index=True,
    )

    assigned_class = models.ManyToManyField(
        "class_module.Class",
        verbose_name=_("برای کلاس"),
        related_name="assigned_homeworks",
        db_index=True,
    )

    def __str__(self) -> str:
        return f"{self.title}"

    def get_absolute_url(self) -> str:
        return reverse("homework-detail-page", args=[self.uuid])

    class Meta:
        verbose_name = _("تکلیف")
        verbose_name_plural = _("تکالیف")


    def assign_homework(self, classes: QuerySet[Class]) -> None:
        """Assigns the homework to students of entered classes.

        Args:
            classes: Classes which you want to assign homework to their students.
        """

        # Create HomeworkCreatedFor (relation table for homework and students),
        # For each student of each classes

        duplicated_homeworks = (
            HomeworkCreatedFor.objects.filter(
                homework=self,
                assigned_class__in=self.assigned_class.all(),
                is_delete=True,
            )
        )

        duplicated_homeworks_assigned_to = set(duplicated_homeworks.values_list("assigned_to", flat=True))
        duplicated_homeworks_assigned_class = set(duplicated_homeworks.values_list("assigned_class", flat=True))

        homeworks: QuerySet[HomeworkCreatedFor] = [
            HomeworkCreatedFor(
                homework=self,
                assigned_class=class_,
                assigned_to=student,
                status=3
            )

            for class_ in classes
            for student in class_.assigned_to.all()
            if class_ not in duplicated_homeworks_assigned_class and student not in duplicated_homeworks_assigned_to
        ]


        # If clear is true, it will unassign old classes and students from the homework,
        # Else, it will assign new classes to the homework

        duplicated_homeworks.update(is_delete=False, status=3)
        HomeworkCreatedFor.objects.bulk_create(homeworks)
        self.assigned_class.add(*classes)

    def unassign_homework(self, classes: QuerySet[Class]) -> None:
        """Unassigns a homework from students of entered classes

        Args:
            classes: Classes which you want to unassign homework from it.
        """

        # Unassign homework form students of entered classes (Set is_delete to True)
        unassign_homeworks = (
            HomeworkCreatedFor.objects.filter(
                homework=self,
                assigned_class__in=classes,
                is_delete=False,
            )
        )

        unassign_homeworks.update(is_delete=True)
        self.assigned_class.remove(*classes)


class HomeworkCreatedFor(models.Model):
    creation_date = jmodels.jDateTimeField(verbose_name=_("تاریخ ایجاد شدن"), auto_now_add=True, db_index=True)
    modify_date = jmodels.jDateTimeField(verbose_name=_("تاریخ ایجاد شدن"), auto_now=True, db_index=True)
    is_delete = models.BooleanField(verbose_name=_("حذف شده / حذف نشده"), default=False, db_index=True)
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
        related_name="assigned_users",
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
        related_name="assigned_homeworks",
        on_delete=models.CASCADE,
    )

    def __str__(self) -> str:
        return f"{self.homework.title} - {self.assigned_to}"

    def get_absolute_url(self) -> str:
        return reverse("homework-detail-page", args=[self.uuid])

    class Meta:
        verbose_name = _("کاربر معین شده برای تکلیف")
        verbose_name_plural = _("کاربران معین شده برای تکالیف")


class HomeworkResult(models.Model):
    description = models.TextField(verbose_name=_("توضیحات نتیجه تکلیف"), max_length=1500, null=True, blank=True)
    creation_date = jmodels.jDateTimeField(verbose_name=_("تاریخ ایجاد شدن"), auto_now_add=True, db_index=True)
    modify_date = jmodels.jDateTimeField(verbose_name=_("تاریخ ایجاد شدن"), auto_now=True, db_index=True)
    is_delete = models.BooleanField(verbose_name=_("حذف شده / حذف نشده"), default=False, db_index=True)
    uuid = models.UUIDField(verbose_name=_("شناسه"), default=uuid4, editable=False, unique=True, db_index=True)

    result_status = models.IntegerField(
        verbose_name=_("وضعیت نتیجه تکلیف"),
        default=2,
        db_index=True,
        validators=(
            MinValueValidator(1),
            MaxValueValidator(3),
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
    description = models.TextField(verbose_name=_("توضیحات"), max_length=1500, null=True, blank=True)
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
        verbose_name=_("فایل"),
        upload_to="homework_module/homework_results/",
        validators=[MaxFileSize(3)],
        db_index=True,
    )

    def __str__(self):
        return f"{self.homework}"

    class Meta:
        verbose_name = _("فایل نتیجه تکلیف")
        verbose_name_plural = _("فایل های نتیجه تکالیف")


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
        upload_to="homework_module/homework_feedbacks/",
        validators=[MaxFileSize(5)],
        db_index=True,
    )

    def __str__(self):
        return f"{self.homework}"

    class Meta:
        verbose_name = _("فایل بازخورد تکلیف")
        verbose_name_plural = _("فایل های بازخورد تکالیف")
