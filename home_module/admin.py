from django.contrib import admin
from . import models

# Register your models here.


@admin.register(models.Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "email", "title", "creation_date", "modify_date", "is_active", "is_delete", "is_read_by_admin")
    list_filter = ("creation_date", "modify_date", "is_active", "is_delete", "is_read_by_admin")
    search_fields = ("name", "email", "title", "message")
