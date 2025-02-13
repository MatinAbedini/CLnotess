from django.contrib import admin
from . import models

# Register your models here.


@admin.register(models.Homework)
class HomeworkAdmin(admin.ModelAdmin):
    list_display = ("id", "__str__", "lesson", "created_by", "creation_date", "for_date", "is_delete")
    list_filter = ("is_delete", "lesson", "creation_date", "for_date")
    search_fields = ("title", "description")

    def save_model(self, request, obj, form, change):
        # If a new Homework is created, then created_by will set to user
        if not change:
            obj.created_by = request.user

        return super().save_model(request, obj, form, change)


@admin.register(models.HomeworkCreatedFor)
class HomeworkCreatedForAdmin(admin.ModelAdmin):
    list_display = ("id", "homework", "assigned_to", "creation_date", "modify_date", "homework__is_delete")
    list_filter = ("creation_date", "modify_date", "homework__is_delete")
    search_fields = ("homework", "assigned_to")

    def save_model(self, request, obj, form, change):
        # If a new Homework is created, then created_by will set to user
        if not change:
            obj.created_by = request.user

        return super().save_model(request, obj, form, change)


@admin.register(models.HomeworkResult)
class HomeworkResultAdmin(admin.ModelAdmin):
    list_display = ("id", "result_status", "creation_date", "modify_date", "is_delete")
    list_filter = ( "result_status", "creation_date", "modify_date", "is_delete")
    search_fields = ("result_description",)


@admin.register(models.HomeworkFeedback)
class HomeworkFeedbackAdmin(admin.ModelAdmin):
    list_display = ("id","creation_date", "modify_date", "is_delete")
    list_filter = ("creation_date", "modify_date", "is_delete")
    search_fields = ("feedback_description",)


@admin.register(models.HomeworkResultFile)
class HomeworkResultFileAdmin(admin.ModelAdmin):
    list_display = ("id", "creation_date", "modify_date", "is_delete")
    list_filter = ("creation_date", "modify_date","is_delete")
    search_fields = ("homework",)
