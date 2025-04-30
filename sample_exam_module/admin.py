from django.contrib import admin
from . import models

# Register your models here.


@admin.register(models.SampleExam)
class SampleExamAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "created_by", "creation_date", "modify_date", "lesson", "is_delete")
    list_filter = ("is_delete", "creation_date", "modify_date")
    search_fields = ("title", "text")

    def save_model(self, request, obj, form, change):
        # If a new Homework is created, then created_by will set to user
        if not change:
            obj.created_by = request.user

        return super().save_model(request, obj, form, change)


@admin.register(models.SampleExamFiles)
class SampleExamFilesAdmin(admin.ModelAdmin):
    list_display = ("id", "creation_date", "modify_date", "sample_exam", "is_delete")
    list_filter = ("is_delete", "creation_date", "modify_date")
