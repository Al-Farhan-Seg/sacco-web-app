from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse

from core.search import search

from .forms import SavingForm
from .models import Saving


# READ: list the savings, with search and pages of 10
@login_required
def saving_list(request):
    savings = Saving.objects.select_related("member", "account", "staff").order_by("-id")

    q = request.GET.get("q", "").strip()
    if q:
        savings = search(
            savings,
            q,
            fields=[
                "member__first_name",
                "member__last_name",
                "account__account_number",
                "staff__first_name",
                "staff__last_name",
                "payment_method",
            ],
            codes={"SAV": "pk", "MEM": "member_id", "ACC": "account_id", "STF": "staff_id"},
        )

    page_obj = Paginator(savings, 10).get_page(request.GET.get("page"))

    context = {
        "object_list": page_obj.object_list,
        "page_obj": page_obj,
        "q": q,
        "search_hint": "Search member, account, staff or SAV-001",
        "page_title": "Savings",
        "add_label": "Add saving",
        "add_url": reverse("saving_add"),
    }
    return render(request, "savings/saving_list.html", context)


# CREATE: show the empty form (GET) or save it (POST)
@login_required
def saving_create(request):
    if request.method == "POST":
        form = SavingForm(request.POST)
        if form.is_valid():
            saving = form.save()
            messages.success(request, f"{saving.code} saved")
            return HttpResponse(status=204)  # modal.js reloads the page on 204
        context = {"form": form, "modal_title": "Add saving"}
        return render(request, "partials/_modal_form.html", context, status=400)
    else:
        form = SavingForm()

    context = {"form": form, "modal_title": "Add saving"}
    return render(request, "partials/_modal_form.html", context)


# UPDATE: show the form filled with the saving (GET) or save the changes (POST)
@login_required
def saving_update(request, pk):
    saving = get_object_or_404(Saving, pk=pk)

    if request.method == "POST":
        form = SavingForm(request.POST, instance=saving)
        if form.is_valid():
            saving = form.save()
            messages.success(request, f"{saving.code} saved")
            return HttpResponse(status=204)
        context = {"form": form, "modal_title": f"Edit {saving.code}"}
        return render(request, "partials/_modal_form.html", context, status=400)
    else:
        form = SavingForm(instance=saving)

    context = {"form": form, "modal_title": f"Edit {saving.code}"}
    return render(request, "partials/_modal_form.html", context)


# DELETE: ask for confirmation (GET) or delete (POST)
@login_required
def saving_delete(request, pk):
    saving = get_object_or_404(Saving, pk=pk)

    if request.method == "POST":
        code = saving.code
        saving.delete()
        messages.success(request, f"{code} deleted")
        return HttpResponse(status=204)

    context = {"object": saving}
    return render(request, "partials/_modal_delete.html", context)
