from django.contrib import admin
from .models import Exam, ExamResult

# Register your models here.

@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ("id", "__str__", "created_by", "creation_date", "modify_date", "for_date", "status", "difficulty", "is_active", "is_delete")
    list_filter = ("is_active", "is_delete", "creation_date", "modify_date", "status", "difficulty")
    search_fields = ("title", "description")


@admin.register(ExamResult)
class ExamResultAdmin(admin.ModelAdmin):
    list_display = ("id", "exam", "student", "is_active", "is_delete")
    list_filter = ("is_active", "is_delete")
    search_fields = ("exam", "student")
