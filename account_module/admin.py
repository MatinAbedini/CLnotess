from django.contrib import admin
from .models import Account, AccountSettings
from django.contrib.auth.admin import UserAdmin

# Register your models here.

@admin.register(Account)
class AccountAdmin(UserAdmin):
    pass

@admin.register(AccountSettings)
class AccountSettings(admin.ModelAdmin):
    pass
