from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from .analytics import (
    exits_per_month,
    loan_book,
    repayments,
    savings_by_method,
    savings_per_month,
)
from .stats import summary


# Shows the home page with the SACCO's live numbers and a small analytics brief
@login_required
def index(request):
    context = summary()
    context["flows"] = savings_per_month()
    context["book"] = loan_book()
    return render(request, 'dashboard/index.html', context)


# Shows the full analytics page
@login_required
def analytics(request):
    context = {
        "flows": savings_per_month(),
        "exits": exits_per_month(),
        "book": loan_book(),
        "repayments": repayments(),
        "methods": savings_by_method(),
    }
    return render(request, 'dashboard/analytics.html', context)
