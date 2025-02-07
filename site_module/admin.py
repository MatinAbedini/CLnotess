from django.contrib import admin
from .models import SiteSettings


# Register your models here.


@admin.register(SiteSettings)
class Admin(admin.ModelAdmin):
    list_display = ("id", "site_name", "site_url", "is_main")
