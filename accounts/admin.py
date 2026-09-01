from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Account

class AccountAdmin(UserAdmin):
    list_display = ("email", "username", "first_name", "last_name", "last_login", "created_date")
    readonly_fields = ("last_login", "created_date")
    list_display_links = ("email", "username", "first_name")

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()
    

admin.site.register(Account, AccountAdmin)