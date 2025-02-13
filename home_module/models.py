from django.utils.translation import gettext_lazy as _
from django_jalali.db import models as jmodels
from django.db import models

# Create your models here.

class Contact(models.Model):
    name = models.CharField(verbose_name=_("نام"), max_length=100, null=False, blank=False)
    email = models.EmailField(verbose_name=_("آدرس ایمیل"), max_length=254, null=False, blank=False, db_index=True)
    title = models.CharField(verbose_name=_("موضوع"), max_length=100, null=False, blank=False, db_index=True)
    message = models.TextField(verbose_name=_("متن پیام"), max_length=1500, null=False, blank=False)
    admin_message = models.TextField(verbose_name=_("متن جواب"), max_length=1500, null=True, blank=True)
    creation_date = jmodels.jDateTimeField(verbose_name=_("تاریخ ایجاد شدن"), auto_now_add=True, db_index=True)
    modify_date = jmodels.jDateTimeField(verbose_name=_("تاریخ ویرایش"), auto_now=True, db_index=True)
    is_active = models.BooleanField(verbose_name=_("فعال / غیرفعال"), default=True, db_index=True)
    is_delete = models.BooleanField(verbose_name=_("حذف شده / حذف نشده"), default=False, db_index=True)
    is_read_by_admin = models.BooleanField(verbose_name=_("خوانده شده / نشده"), default=False, db_index=True)

    class Meta:
        verbose_name = _("پیام")
        verbose_name_plural = _("پیام ها")

    def __str__(self):
        return f"{self.email} - {self.title}"
