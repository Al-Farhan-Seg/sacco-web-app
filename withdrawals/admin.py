from django.contrib import admin

from .models import Withdrawal


@admin.register(Withdrawal)
class WithdrawalAdmin(admin.ModelAdmin):
    list_display = ("code", "member", "amount", "date")
    list_filter = ("date",)
    list_select_related = ("member",)
    search_fields = ("member__first_name", "member__last_name")
    date_hierarchy = "date"
