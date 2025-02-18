from django.utils.translation import gettext_lazy as _
from django.contrib.auth.admin import UserAdmin
from django.contrib import admin

from .models import Account, AccountSettings

# Register your models here.

@admin.register(Account)
class AccountAdmin(UserAdmin):
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (_("Personal info"), {"fields": ("first_name", "last_name", "email", "settings", "profile_image")}),
        (_("Permissions"), {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )

@admin.register(AccountSettings)
class AccountSettings(admin.ModelAdmin):
    list_display = ("id", "sidebar_navbar_theme", "sidebar_primary_color", "account")
