from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse

from core.search import search

from .forms import WithdrawalForm
from .models import Withdrawal


# READ: list the withdrawals, with search and pages of 10
@login_required
def withdrawal_list(request):
    withdrawals = Withdrawal.objects.select_related("member").order_by("-id")

    q = request.GET.get("q", "").strip()
    if q:
        withdrawals = search(
            withdrawals,
            q,
            fields=["member__first_name", "member__last_name"],
            codes={"WDR": "pk", "MEM": "member_id"},
        )

    page_obj = Paginator(withdrawals, 10).get_page(request.GET.get("page"))

    context = {
        "object_list": page_obj.object_list,
        "page_obj": page_obj,
        "q": q,
        "search_hint": "Search member or WDR-001",
        "page_title": "Withdrawals",
        "add_label": "Add withdrawal",
        "add_url": reverse("withdrawal_add"),
    }
    return render(request, "withdrawals/withdrawal_list.html", context)


# CREATE: show the empty form (GET) or save it (POST)
@login_required
def withdrawal_create(request):
    if request.method == "POST":
        form = WithdrawalForm(request.POST)
        if form.is_valid():
            withdrawal = form.save()
            messages.success(request, f"{withdrawal.code} saved")
            return HttpResponse(status=204)  # modal.js reloads the page on 204
        context = {"form": form, "modal_title": "Add withdrawal"}
        return render(request, "partials/_modal_form.html", context, status=400)
    else:
        form = WithdrawalForm()

    context = {"form": form, "modal_title": "Add withdrawal"}
    return render(request, "partials/_modal_form.html", context)


# UPDATE: show the form filled with the withdrawal (GET) or save the changes (POST)
@login_required
def withdrawal_update(request, pk):
    withdrawal = get_object_or_404(Withdrawal, pk=pk)

    if request.method == "POST":
        form = WithdrawalForm(request.POST, instance=withdrawal)
        if form.is_valid():
            withdrawal = form.save()
            messages.success(request, f"{withdrawal.code} saved")
            return HttpResponse(status=204)
        context = {"form": form, "modal_title": f"Edit {withdrawal.code}"}
        return render(request, "partials/_modal_form.html", context, status=400)
    else:
        form = WithdrawalForm(instance=withdrawal)

    context = {"form": form, "modal_title": f"Edit {withdrawal.code}"}
    return render(request, "partials/_modal_form.html", context)


# DELETE: ask for confirmation (GET) or delete (POST)
@login_required
def withdrawal_delete(request, pk):
    withdrawal = get_object_or_404(Withdrawal, pk=pk)

    if request.method == "POST":
        code = withdrawal.code
        withdrawal.delete()
        messages.success(request, f"{code} deleted")
        return HttpResponse(status=204)

    context = {"object": withdrawal}
    return render(request, "partials/_modal_delete.html", context)
