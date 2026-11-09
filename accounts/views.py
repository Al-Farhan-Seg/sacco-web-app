from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse

from core.search import search

from .forms import AccountForm
from .models import Account


# READ: list the accounts, with search and pages of 10
@login_required
def account_list(request):
    accounts = Account.objects.select_related("member").order_by("-id")

    q = request.GET.get("q", "").strip()
    if q:
        accounts = search(
            accounts,
            q,
            fields=["account_number", "account_type", "member__first_name", "member__last_name"],
            codes={"ACC": "pk", "MEM": "member_id"},
        )

    page_obj = Paginator(accounts, 10).get_page(request.GET.get("page"))

    context = {
        "object_list": page_obj.object_list,
        "page_obj": page_obj,
        "q": q,
        "search_hint": "Search account number, member or ACC-001",
        "page_title": "Accounts",
        "add_label": "Add account",
        "add_url": reverse("account_add"),
    }
    return render(request, "accounts/account_list.html", context)


# CREATE: show the empty form (GET) or save it (POST)
@login_required
def account_create(request):
    if request.method == "POST":
        form = AccountForm(request.POST)
        if form.is_valid():
            account = form.save()
            messages.success(request, f"{account.code} saved")
            return HttpResponse(status=204)  # modal.js reloads the page on 204
        context = {"form": form, "modal_title": "Add account"}
        return render(request, "partials/_modal_form.html", context, status=400)
    else:
        form = AccountForm()

    context = {"form": form, "modal_title": "Add account"}
    return render(request, "partials/_modal_form.html", context)


# UPDATE: show the form filled with the account (GET) or save the changes (POST)
@login_required
def account_update(request, pk):
    account = get_object_or_404(Account, pk=pk)

    if request.method == "POST":
        form = AccountForm(request.POST, instance=account)
        if form.is_valid():
            account = form.save()
            messages.success(request, f"{account.code} saved")
            return HttpResponse(status=204)
        context = {"form": form, "modal_title": f"Edit {account.code}"}
        return render(request, "partials/_modal_form.html", context, status=400)
    else:
        form = AccountForm(instance=account)

    context = {"form": form, "modal_title": f"Edit {account.code}"}
    return render(request, "partials/_modal_form.html", context)


# DELETE: ask for confirmation (GET) or delete (POST)
@login_required
def account_delete(request, pk):
    account = get_object_or_404(Account, pk=pk)

    if request.method == "POST":
        code = account.code
        account.delete()
        messages.success(request, f"{code} deleted")
        return HttpResponse(status=204)

    context = {"object": account, "delete_note": "its savings"}
    return render(request, "partials/_modal_delete.html", context)
