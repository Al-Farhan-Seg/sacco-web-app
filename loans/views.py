from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse

from core.search import search

from .forms import LoanForm, LoanPaymentForm
from .models import Loan, LoanPayment


# ---------------------------------------------------------------- Loans


# READ: list the loans, with search and pages of 10
@login_required
def loan_list(request):
    loans = Loan.objects.select_related("member", "staff").order_by("-id")

    q = request.GET.get("q", "").strip()
    if q:
        loans = search(
            loans,
            q,
            fields=[
                "member__first_name",
                "member__last_name",
                "staff__first_name",
                "staff__last_name",
                "payment_period",
            ],
            codes={"LN": "pk", "MEM": "member_id", "STF": "staff_id"},
        )

    page_obj = Paginator(loans, 10).get_page(request.GET.get("page"))

    context = {
        "object_list": page_obj.object_list,
        "page_obj": page_obj,
        "q": q,
        "search_hint": "Search member, staff or LN-001",
        "page_title": "Loans",
        "add_label": "Add loan",
        "add_url": reverse("loan_add"),
    }
    return render(request, "loans/loan_list.html", context)


# CREATE: show the empty form (GET) or save it (POST)
@login_required
def loan_create(request):
    if request.method == "POST":
        form = LoanForm(request.POST)
        if form.is_valid():
            loan = form.save()
            messages.success(request, f"{loan.code} saved")
            return HttpResponse(status=204)  # modal.js reloads the page on 204
        context = {"form": form, "modal_title": "Add loan"}
        return render(request, "partials/_modal_form.html", context, status=400)
    else:
        form = LoanForm()

    context = {"form": form, "modal_title": "Add loan"}
    return render(request, "partials/_modal_form.html", context)


# UPDATE: show the form filled with the loan (GET) or save the changes (POST)
@login_required
def loan_update(request, pk):
    loan = get_object_or_404(Loan, pk=pk)

    if request.method == "POST":
        form = LoanForm(request.POST, instance=loan)
        if form.is_valid():
            loan = form.save()
            messages.success(request, f"{loan.code} saved")
            return HttpResponse(status=204)
        context = {"form": form, "modal_title": f"Edit {loan.code}"}
        return render(request, "partials/_modal_form.html", context, status=400)
    else:
        form = LoanForm(instance=loan)

    context = {"form": form, "modal_title": f"Edit {loan.code}"}
    return render(request, "partials/_modal_form.html", context)


# DELETE: ask for confirmation (GET) or delete (POST)
@login_required
def loan_delete(request, pk):
    loan = get_object_or_404(Loan, pk=pk)

    if request.method == "POST":
        code = loan.code
        loan.delete()
        messages.success(request, f"{code} deleted")
        return HttpResponse(status=204)

    context = {"object": loan, "delete_note": "its payments"}
    return render(request, "partials/_modal_delete.html", context)


# ------------------------------------------------------- Loan payments


# READ: list the loan payments, with search and pages of 10
@login_required
def payment_list(request):
    payments = LoanPayment.objects.select_related("loan__member").order_by("-id")

    q = request.GET.get("q", "").strip()
    if q:
        payments = search(
            payments,
            q,
            fields=["loan__member__first_name", "loan__member__last_name"],
            codes={"PAY": "pk", "LN": "loan_id"},
        )

    page_obj = Paginator(payments, 10).get_page(request.GET.get("page"))

    context = {
        "object_list": page_obj.object_list,
        "page_obj": page_obj,
        "q": q,
        "search_hint": "Search member, loan or PAY-001",
        "page_title": "Loan payments",
        "add_label": "Add loan payment",
        "add_url": reverse("payment_add"),
    }
    return render(request, "loans/payment_list.html", context)


# CREATE: show the empty form (GET) or save it (POST)
@login_required
def payment_create(request):
    if request.method == "POST":
        form = LoanPaymentForm(request.POST)
        if form.is_valid():
            payment = form.save()
            messages.success(request, f"{payment.code} saved")
            return HttpResponse(status=204)  # modal.js reloads the page on 204
        context = {"form": form, "modal_title": "Add loan payment"}
        return render(request, "partials/_modal_form.html", context, status=400)
    else:
        form = LoanPaymentForm()

    context = {"form": form, "modal_title": "Add loan payment"}
    return render(request, "partials/_modal_form.html", context)


# UPDATE: show the form filled with the payment (GET) or save the changes (POST)
@login_required
def payment_update(request, pk):
    payment = get_object_or_404(LoanPayment, pk=pk)

    if request.method == "POST":
        form = LoanPaymentForm(request.POST, instance=payment)
        if form.is_valid():
            payment = form.save()
            messages.success(request, f"{payment.code} saved")
            return HttpResponse(status=204)
        context = {"form": form, "modal_title": f"Edit {payment.code}"}
        return render(request, "partials/_modal_form.html", context, status=400)
    else:
        form = LoanPaymentForm(instance=payment)

    context = {"form": form, "modal_title": f"Edit {payment.code}"}
    return render(request, "partials/_modal_form.html", context)


# DELETE: ask for confirmation (GET) or delete (POST)
@login_required
def payment_delete(request, pk):
    payment = get_object_or_404(LoanPayment, pk=pk)

    if request.method == "POST":
        code = payment.code
        payment.delete()
        messages.success(request, f"{code} deleted")
        return HttpResponse(status=204)

    context = {"object": payment}
    return render(request, "partials/_modal_delete.html", context)
