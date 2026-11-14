from django.contrib import admin

from .models import Saving


@admin.register(Saving)
class SavingAdmin(admin.ModelAdmin):
    list_display = ("code", "member", "account", "staff", "payment_method", "amount", "date")
    list_filter = ("payment_method", "date")
    list_select_related = ("member", "account", "staff")
    search_fields = ("member__first_name", "member__last_name", "account__account_number")
    date_hierarchy = "date"
