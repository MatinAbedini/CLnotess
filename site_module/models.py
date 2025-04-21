from django.db import models
from django.utils.translation import gettext_lazy as _


# Create your models here.


class SiteSettings(models.Model):
    site_name = models.CharField(max_length=120, null=False, blank=False, verbose_name=_("نام سایت"))
    site_url = models.CharField(max_length=120, null=False, blank=False, verbose_name=_("آدرس سایت"))
    about_us = models.TextField(null=False, blank=False, verbose_name=_("درباره ی ما"))
    help_file = models.FileField(null=True, verbose_name=_("فایل راهنما"))
    is_main = models.BooleanField(db_index=True, default=False, verbose_name=_("اصلی / غیر اصلی"))

    def __str__(self):
        return f"{self.site_name}"

    class Meta:
        verbose_name = _("تنضیمات سایت")
        verbose_name_plural = _("تنضیمات سایت")
