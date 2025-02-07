from django.contrib import admin
from .models import Class, ClassTeacherRole

# Register your models here.

@admin.register(Class)
class ClassAdmin(admin.ModelAdmin):
    list_display = ("id", "__str__", "creation_date", "modify_date", "is_active", "is_delete")
    list_filter = ("creation_date", "modify_date", "is_active")
    search_fields = ("class_name", "school_name")


@admin.register(ClassTeacherRole)
class ClassTeacherAdmin(admin.ModelAdmin):
    pass
