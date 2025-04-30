from django.utils.translation import gettext_lazy as _
from django_jalali.db import models as jmodels
from django.urls import reverse
from django.db import models

from utils.validators import MaxFileSize
from uuid import uuid4


# Create your models here.


class Note(models.Model):
    title = models.CharField(verbose_name=_("موضوع"), max_length=100, null=False, blank=False, db_index=True)
    text = models.TextField(verbose_name=_("متن"), max_length=10000, null=True, blank=True)
    creation_date = jmodels.jDateTimeField(verbose_name=_("تاریخ ایجاد شدن"), auto_now_add=True, db_index=True)
    modify_date = jmodels.jDateTimeField(verbose_name=_("تاریخ ویرایش"), auto_now=True)
    is_delete = models.BooleanField(verbose_name=_("حذف شده / حذف نشده"), default=False, db_index=True)
    uuid = models.UUIDField(verbose_name=_("شناسه"), default=uuid4, editable=False, unique=True, db_index=True)

    lesson = models.ForeignKey(
        "lesson_module.lesson",
        verbose_name=_("درس"),
        related_name="notes",
        on_delete=models.SET_DEFAULT,
        default=1,
    )

    created_by = models.ForeignKey(
        "account_module.Account",
        verbose_name=_("ساخته شده توسط"),
        related_name="created_notes",
        on_delete=models.SET_NULL,
        editable=False,
        null=True,
        db_index=True,
    )

    assigned_class = models.ManyToManyField(
        "class_module.Class",
        verbose_name=_("برای کلاس"),
        related_name="assigned_notes",
        db_index=True,
    )

    assigned_to = models.ForeignKey(
        "account_module.Account",
        verbose_name=_("دانش آموز"),
        related_name="assigned_notes",
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = _("نکات درسی")
        verbose_name_plural = _("نکات درسی")

    def __str__(self) -> str:
        return self.title

    def get_absolute_url(self):
        return reverse("note_detail", kwargs={"uuid": self.uuid})


class NoteFiles(models.Model):
    creation_date = jmodels.jDateTimeField(verbose_name=_("تاریخ ایجاد شدن"), auto_now_add=True, db_index=True)
    modify_date = jmodels.jDateTimeField(verbose_name=_("تاریخ ایجاد شدن"), auto_now=True, db_index=True)
    is_delete = models.BooleanField(verbose_name=_("حذف شده / حذف نشده"), default=False, db_index=True)

    note = models.ForeignKey(
        "Note",
        verbose_name=_("برای نکته درسی"),
        related_name="files",
        on_delete=models.CASCADE,
    )

    file = models.FileField(
        verbose_name=_("فایل"),
        upload_to="note_module/",
        validators=[MaxFileSize(3)],
        null=False,
    )

    class Meta:
        verbose_name = _("فایل نکات درسی")
        verbose_name_plural = _("فایل های نکات درسی")

    def __str__(self) -> str:
        return f"{self.note.tile} - {self.file}"
