from django.contrib import admin

from .models import Loan, LoanPayment


@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    list_display = ("code", "member", "staff", "loan_amount", "payment_period", "payment_amount")
    list_select_related = ("member", "staff")
    search_fields = ("member__first_name", "member__last_name")


@admin.register(LoanPayment)
class LoanPaymentAdmin(admin.ModelAdmin):
    list_display = ("code", "loan", "amount", "date")
    list_filter = ("date",)
    list_select_related = ("loan__member",)
    search_fields = ("loan__member__first_name", "loan__member__last_name")
    date_hierarchy = "date"
