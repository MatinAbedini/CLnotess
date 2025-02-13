from uuid import uuid4
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

# Create your models here.


class Account(AbstractUser):
    active_code = models.UUIDField(default=uuid4, editable=False, db_index=True)

    profile_image = models.FileField(
        verbose_name=_("تصویر پروفایل"),
        upload_to="account_module/profile_images/",
        null=True,
    )

    settings = models.OneToOneField(
        "AccountSettings",
        on_delete=models.CASCADE,
        verbose_name=_("توضیحات"),
        related_name="account",
        null=True
    )

    def save(self, *args, **kwargs):
        # If settings is not created, creates it automatically for user
        if self.settings is None:
            settings = AccountSettings.objects.create()
            self.settings = settings

        super().save(*args, **kwargs)

class AccountSettings(models.Model):
    sidebar_navbar_theme = models.CharField(
        max_length=14,
        default="theme-6-active",
        db_index=True,
        choices=[
            ("theme-1-active", _("سفید - سیاه")),
            ("theme-2-active", _("سیاه - سفید")),
            ("theme-3-active", _("سفید - سیاه کامل")),
            ("theme-4-active", _("سیاه - سفید کامل")),
            ("theme-5-active", _("سفید - سفید")),
            ("theme-6-active", _("سیاه - سیاه")),
        ]
    )

    sidebar_primary_color = models.CharField(
        max_length=19,
        default="pimary-color-blue",
        db_index=True,
        choices=[
            ("pimary-color-red", _("قرمز")),
            ("pimary-color-blue", _("آبی")),
            ("pimary-color-green", _("سبز")),
            ("pimary-color-yellow", _("زرد")),
            ("pimary-color-pink", _("صورتی")),
            ("pimary-color-orange", _("نارنجی")),
            ("pimary-color-gold", _("طلایی")),
            ("pimary-color-silver", _("نقره ای")),
        ]
    )

    class Meta:
        verbose_name = _("تنظیمات کاربر")
        verbose_name_plural = _("تنظیمات کاربران")
