from django.contrib import admin
from .models import Class

# Register your models here.

@admin.register(Class)
class ClassAdmin(admin.ModelAdmin):
    list_display = ("id", "__str__", "creation_date", "modify_date", "created_by", "is_delete")
    list_filter = ("creation_date", "modify_date")
    search_fields = ("class_name", "school_name")

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user

        return super().save_model(request, obj, form, change)
