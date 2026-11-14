from django.contrib import admin

from .models import Account


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ("code", "account_number", "member", "account_type", "opening_balance")
    list_filter = ("account_type",)
    list_select_related = ("member",)
    search_fields = ("account_number", "member__first_name", "member__last_name")
