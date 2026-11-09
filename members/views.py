from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse

from core.search import search

from .forms import MemberForm
from .models import Member


# READ: list the members, with search and pages of 10
@login_required
def member_list(request):
    members = Member.objects.order_by("-id")

    q = request.GET.get("q", "").strip()
    if q:
        members = search(
            members,
            q,
            fields=["first_name", "last_name", "contact", "address", "email"],
            codes={"MEM": "pk"},
        )

    page_obj = Paginator(members, 10).get_page(request.GET.get("page"))

    context = {
        "object_list": page_obj.object_list,
        "page_obj": page_obj,
        "q": q,
        "search_hint": "Search name, contact, email, address or MEM-001",
        "page_title": "Members",
        "add_label": "Add member",
        "add_url": reverse("member_add"),
    }
    return render(request, "members/member_list.html", context)


# CREATE: show the empty form (GET) or save it (POST)
@login_required
def member_create(request):
    if request.method == "POST":
        form = MemberForm(request.POST)
        if form.is_valid():
            member = form.save()
            messages.success(request, f"{member.code} saved")
            return HttpResponse(status=204)  # modal.js reloads the page on 204
        context = {"form": form, "modal_title": "Add member"}
        return render(request, "partials/_modal_form.html", context, status=400)
    else:
        form = MemberForm()

    context = {"form": form, "modal_title": "Add member"}
    return render(request, "partials/_modal_form.html", context)


# UPDATE: show the form filled with the member (GET) or save the changes (POST)
@login_required
def member_update(request, pk):
    member = get_object_or_404(Member, pk=pk)

    if request.method == "POST":
        form = MemberForm(request.POST, instance=member)
        if form.is_valid():
            member = form.save()
            messages.success(request, f"{member.code} saved")
            return HttpResponse(status=204)
        context = {"form": form, "modal_title": f"Edit {member.code}"}
        return render(request, "partials/_modal_form.html", context, status=400)
    else:
        form = MemberForm(instance=member)

    context = {"form": form, "modal_title": f"Edit {member.code}"}
    return render(request, "partials/_modal_form.html", context)


# DELETE: ask for confirmation (GET) or delete (POST)
@login_required
def member_delete(request, pk):
    member = get_object_or_404(Member, pk=pk)

    if request.method == "POST":
        code = member.code
        member.delete()
        messages.success(request, f"{code} deleted")
        return HttpResponse(status=204)

    context = {
        "object": member,
        "delete_note": "their accounts, savings, loans and withdrawals",
    }
    return render(request, "partials/_modal_delete.html", context)
