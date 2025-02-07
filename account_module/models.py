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
        "account_module.AccountSettings",
        on_delete=models.CASCADE,
        verbose_name=_("توضیحات"),
        related_name="account",
        null=True,
        blank=True,
    )

    phone_number = models.IntegerField(
        unique=True,
        null=True,
        blank=True,
        db_index=True,
    )


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


    class Meta:
        verbose_name = _("تنظیمات کاربر")
        verbose_name_plural = _("تنظیمات کاربران")
