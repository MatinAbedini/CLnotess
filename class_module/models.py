from django.utils.translation import gettext_lazy as _
from django.db import models
from uuid import uuid4

from account_module.models import Account
from lesson_module.models import Lesson

# Create your models here.


class Class(models.Model):
    class_name = models.CharField(verbose_name=_("نام کلاس"), max_length=100, blank=False, null=False)
    school_name = models.CharField(verbose_name=_("نام آموزشگاه (مدرسه)"), max_length=120, null=True, blank=True)
    creation_date = models.DateTimeField(auto_now_add=True, verbose_name=_("تاریخ ساخت"))
    modify_date = models.DateTimeField(auto_now=True, verbose_name=_("تاریخ ویرایش"))
    is_active = models.BooleanField(default=True, db_index=True, verbose_name=_("فعال / غیرفعال"))
    is_delete = models.BooleanField(default=False, db_index=True, verbose_name=_("حذف شده / نشده"))
    uuid = models.UUIDField(default=uuid4, editable=False, db_index=True, verbose_name=_("شناسه"))

    created_by = models.ForeignKey(
        Account,
        verbose_name=_("ساخته شده توسط"),
        related_name="created_classes",
        on_delete=models.SET_NULL,
        null=True,
        db_index=True,
    )

    assigned_to = models.ManyToManyField(
        "account_module.Account",
        verbose_name=_("دانش آموز"),
        related_name="assigned_classes",
        blank=True
    )


    def __str__(self) -> str:
        return f"کلاس {self.class_name} {self.school_name}"


    class Meta:
        verbose_name = _("کلاس")
        verbose_name_plural = _("کلاس ها")


class ClassTeacherRole(models.Model):
    teacher = models.ForeignKey("account_module.Account", verbose_name=_("معلم"), related_name="lesson", on_delete=models.CASCADE)
    assigned_class = models.ForeignKey("Class", verbose_name=_("برای کلاس"), related_name="teachers", on_delete=models.CASCADE)
    lesson = models.ForeignKey("lesson_module.Lesson", verbose_name=_("درس"), related_name="teachers", on_delete=models.CASCADE)


    def __str__(self) -> str:
        return f"{self.assigned_class.__str} - {self.teacher} / {self.lesson}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.assigned_class.assigned_to.add(self.teacher)

    class Meta:
        verbose_name = "نفش معلم در کلاس"
        verbose_name_plural = "نقش های معلم در کلاس ها"
