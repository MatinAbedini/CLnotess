from django.contrib import admin
from .models import Invitation, InvitationAssignedTo

# Register your models here.


@admin.register(Invitation)
class InvitationAdmin(admin.ModelAdmin):
    list_display = ("id", "created_by", "creation_date", "type", "is_delete")
    list_filter = ("creation_date", "type", "is_delete")
    search_fields = ("created_by",)


@admin.register(InvitationAssignedTo)
class InvitationAssignedToAdmin(admin.ModelAdmin):
    list_display = ("id", "assigned_to", "status", "is_delete")
    list_filter = ("status", "is_delete")
    search_fields = ("assigned_to",)
