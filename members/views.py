from django.views.generic import CreateView, DeleteView, UpdateView

from core.crud import ListPage, ModalDeleteMixin, ModalFormMixin

from .forms import MemberForm
from .models import Member


class MemberList(ListPage):
    model = Member
    page_title = "Members"
    add_label = "Add member"
    url_name = "member"
    search_fields = ["first_name", "last_name", "contact", "address", "email"]
    search_codes = {"MEM": "pk"}
    search_hint = "Search name, contact, email, address or MEM-001"


class MemberCreate(ModalFormMixin, CreateView):
    model = Member
    form_class = MemberForm


class MemberUpdate(ModalFormMixin, UpdateView):
    model = Member
    form_class = MemberForm


class MemberDelete(ModalDeleteMixin, DeleteView):
    model = Member
    delete_note = "their accounts, savings, loans and withdrawals"
