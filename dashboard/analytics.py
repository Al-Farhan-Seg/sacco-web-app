from datetime import date

from django.db.models import Sum
from django.db.models.functions import TruncMonth

from loans.models import Loan, LoanPayment
from savings.models import Saving
from withdrawals.models import Withdrawal


def month_starts(count=12, today=None):
    """First day of each of the last `count` months, oldest first."""
    today = today or date.today()
    year, month = today.year, today.month
    months = []
    for _ in range(count):
        months.append(date(year, month, 1))
        month -= 1
        if month == 0:
            year, month = year - 1, 12
    return months[::-1]


def monthly_totals(model, months):
    """Sum of `amount` per month; a month with no rows counts as 0."""
    rows = (
        model.objects.filter(date__gte=months[0])
        .annotate(month=TruncMonth("date"))
        .values("month")
        .annotate(total=Sum("amount"))
    )
    by_month = {row["month"]: row["total"] for row in rows}
    return [by_month.get(month, 0) for month in months]


def monthly_chart(series):
    """Last 12 months for one or more series, given as [(css_class, model)].

    Bar heights are percentages of the biggest value shown, so the template
    does no arithmetic.
    """
    months = month_starts()
    values = {css: monthly_totals(model, months) for css, model in series}
    biggest = max(max(v) for v in values.values())
    rows = []
    for i, month in enumerate(months):
        bars = []
        for css, _ in series:
            value = values[css][i]
            pct = max(2, round(100 * value / biggest)) if value else 0
            bars.append({"css": css, "value": value, "pct": pct})
        rows.append({"label": month.strftime("%b"), "full": month.strftime("%B %Y"), "bars": bars})
    return {"rows": rows, "totals": {css: sum(v) for css, v in values.items()}}


def savings_per_month():
    return monthly_chart([("in", Saving)])


def exits_per_month():
    """A withdrawal is a member leaving; the amount is their final balance paid out."""
    return monthly_chart([("out", Withdrawal)])


def repayments():
    return monthly_chart([("in", LoanPayment)])


def loan_book():
    """How much of the money lent has been paid back."""
    lent = Loan.objects.aggregate(total=Sum("loan_amount"))["total"] or 0
    repaid = LoanPayment.objects.aggregate(total=Sum("amount"))["total"] or 0
    return {
        "lent": lent,
        "repaid": repaid,
        "owed": lent - repaid,
        "percent": round(100 * repaid / lent) if lent else 0,
    }


def savings_by_method():
    """Each payment method's share of all savings."""
    names = dict(Saving.METHOD_CHOICES)
    rows = (
        Saving.objects.values("payment_method")
        .annotate(total=Sum("amount"))
        .order_by("-total")
    )
    grand_total = sum(row["total"] for row in rows)
    return {
        "rows": [
            {
                "label": names[row["payment_method"]],
                "total": row["total"],
                "pct": round(100 * row["total"] / grand_total),
            }
            for row in rows
        ],
        "total": grand_total,
    }
