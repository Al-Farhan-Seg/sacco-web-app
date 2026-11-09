from django.views.generic import CreateView, DeleteView, UpdateView

from core.crud import ListPage, ModalDeleteMixin, ModalFormMixin

from .forms import SavingForm
from .models import Saving


class SavingList(ListPage):
    model = Saving
    page_title = "Savings"
    add_label = "Add saving"
    url_name = "saving"
    search_fields = [
        "member__first_name",
        "member__last_name",
        "account__account_number",
        "staff__first_name",
        "staff__last_name",
        "payment_method",
    ]
    search_codes = {"SAV": "pk", "MEM": "member_id", "ACC": "account_id", "STF": "staff_id"}
    search_hint = "Search member, account, staff or SAV-001"

    def get_queryset(self):
        return super().get_queryset().select_related("member", "account", "staff")


class SavingCreate(ModalFormMixin, CreateView):
    model = Saving
    form_class = SavingForm


class SavingUpdate(ModalFormMixin, UpdateView):
    model = Saving
    form_class = SavingForm


class SavingDelete(ModalDeleteMixin, DeleteView):
    model = Saving
