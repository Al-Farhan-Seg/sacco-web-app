from django.db.models import Count, Sum

from accounts.models import Account
from loans.models import Loan, LoanPayment
from members.models import Member
from savings.models import Saving
from staff.models import Staff
from withdrawals.models import Withdrawal


def summary():
    """The dashboard's numbers, each worked out by the database."""
    accounts = Account.objects.aggregate(count=Count("id"), opening=Sum("opening_balance"))
    savings_total = Saving.objects.aggregate(total=Sum("amount"))["total"] or 0
    loans = Loan.objects.aggregate(count=Count("id"), total=Sum("loan_amount"))
    repayments_total = LoanPayment.objects.aggregate(total=Sum("amount"))["total"] or 0
    withdrawals = Withdrawal.objects.aggregate(count=Count("id"), total=Sum("amount"))

    loans_total = loans["total"] or 0
    return {
        "members": Member.objects.count(),
        "staff": Staff.objects.count(),
        "accounts": accounts["count"],
        "total_savings": (accounts["opening"] or 0) + savings_total,
        "loans_count": loans["count"],
        "loans_total": loans_total,
        "repayments_total": repayments_total,
        "still_owed": loans_total - repayments_total,
        "withdrawals_count": withdrawals["count"],
        "withdrawals_total": withdrawals["total"] or 0,
        "recent_savings": Saving.objects.select_related("member").order_by("-id")[:5],
        "recent_loans": Loan.objects.select_related("member").order_by("-id")[:5],
    }
