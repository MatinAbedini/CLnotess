from django.contrib import admin
from . import models

# Register your models here.

@admin.register(models.Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ("id", "__str__", "created_by", "creation_date", "modify_date", "for_date", "status", "difficulty", "is_delete")
    list_filter = ("is_delete", "creation_date", "modify_date", "status", "difficulty")
    search_fields = ("title", "description")

    def save_model(self, request, obj, form, change):
        # If a new Exam is created, then created_by will set to user
        if not change:
            obj.created_by = request.user

        return super().save_model(request, obj, form, change)


@admin.register(models.ExamResult)
class ExamResultAdmin(admin.ModelAdmin):
    list_display = ("id", "exam", "student", "correct_answers", "incorrect_answers", "is_delete")
    list_filter = ( "correct_answers", "incorrect_answers", "is_delete")
    search_fields = ("exam", "student", "result_description")


@admin.register(models.ExamResultFile)
class ExamResultFileAdmin(admin.ModelAdmin):
    list_display = ("id", "creation_date", "modify_date", "is_delete")
    list_filter = ("creation_date", "modify_date","is_delete")
    search_fields = ("assigned_exam",)
