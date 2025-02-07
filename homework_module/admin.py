from django.contrib import admin
from .models import Homework, HomeworkCreatedFor, HomeworkResult

# Register your models here.

@admin.register(Homework)
class HomeworkAdmin(admin.ModelAdmin):
    list_display = ("id", "__str__", "created_by", "creation_date", "creation_date", "is_active", "is_delete")
    list_filter = ("is_active", "creation_date", "creation_date")
    search_fields = ("title", "description")


@admin.register(HomeworkCreatedFor)
class HomeworkCreatedForAdmin(admin.ModelAdmin):
    list_display = ("id", "homework", "assigned_to", "status", "homework__is_active", "homework__is_delete")
    list_filter = ("status", "homework__is_active", "homework__is_delete")
    search_fields = ("homework", "assigned_to")

@admin.register(HomeworkResult)
class HomeworkResultAdmin(admin.ModelAdmin):
    list_display = ("id", "homework", "student", "status", "is_active", "is_delete")
    list_filter = ("status", "is_active", "is_delete")
    search_fields = ("student",)
