from django.contrib import admin
from .models import Class, ClassTeacherRole

# Register your models here.

@admin.register(Class)
class ClassAdmin(admin.ModelAdmin):
    list_display = ("id", "__str__", "creation_date", "modify_date", "created_by", "is_active", "is_delete")
    list_filter = ("creation_date", "modify_date", "is_active")
    search_fields = ("class_name", "school_name")

    def save_model(self, request, obj, form, change):
        # If a new Homework is created, then created_by will set to user
        if not change:
            obj.created_by = request.user
            # obj.assigned_to.add(request.user)

        return super().save_model(request, obj, form, change)


@admin.register(ClassTeacherRole)
class ClassTeacherAdmin(admin.ModelAdmin):
    list_display = ("id", "teacher", "assigned_class", "lesson",)
    list_filter = ("lesson",)
    search_fields = ("assigned_class",)
