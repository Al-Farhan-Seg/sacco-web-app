from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse

from core.search import search

from .forms import StaffForm
from .models import Staff


# READ: list the staff, with search and pages of 10
@login_required
def staff_list(request):
    staff = Staff.objects.order_by("-id")

    q = request.GET.get("q", "").strip()
    if q:
        staff = search(
            staff,
            q,
            fields=["first_name", "last_name", "position", "contact", "address", "role"],
            codes={"STF": "pk"},
        )

    page_obj = Paginator(staff, 10).get_page(request.GET.get("page"))

    context = {
        "object_list": page_obj.object_list,
        "page_obj": page_obj,
        "q": q,
        "search_hint": "Search name, position, contact or STF-001",
        "page_title": "Staff",
        "add_label": "Add staff",
        "add_url": reverse("staff_add"),
    }
    return render(request, "staff/staff_list.html", context)


# CREATE: show the empty form (GET) or save it (POST)
@login_required
def staff_create(request):
    if request.method == "POST":
        form = StaffForm(request.POST)
        if form.is_valid():
            member_of_staff = form.save()
            messages.success(request, f"{member_of_staff.code} saved")
            return HttpResponse(status=204)  # modal.js reloads the page on 204
        context = {"form": form, "modal_title": "Add staff"}
        return render(request, "partials/_modal_form.html", context, status=400)
    else:
        form = StaffForm()

    context = {"form": form, "modal_title": "Add staff"}
    return render(request, "partials/_modal_form.html", context)


# UPDATE: show the form filled with the staff record (GET) or save the changes (POST)
@login_required
def staff_update(request, pk):
    member_of_staff = get_object_or_404(Staff, pk=pk)

    if request.method == "POST":
        form = StaffForm(request.POST, instance=member_of_staff)
        if form.is_valid():
            member_of_staff = form.save()
            messages.success(request, f"{member_of_staff.code} saved")
            return HttpResponse(status=204)
        context = {"form": form, "modal_title": f"Edit {member_of_staff.code}"}
        return render(request, "partials/_modal_form.html", context, status=400)
    else:
        form = StaffForm(instance=member_of_staff)

    context = {"form": form, "modal_title": f"Edit {member_of_staff.code}"}
    return render(request, "partials/_modal_form.html", context)


# DELETE: ask for confirmation (GET) or delete (POST)
@login_required
def staff_delete(request, pk):
    member_of_staff = get_object_or_404(Staff, pk=pk)

    if request.method == "POST":
        code = member_of_staff.code
        member_of_staff.delete()
        messages.success(request, f"{code} deleted")
        return HttpResponse(status=204)

    context = {
        "object": member_of_staff,
        "delete_note": "the savings and loans they recorded",
    }
    return render(request, "partials/_modal_delete.html", context)
