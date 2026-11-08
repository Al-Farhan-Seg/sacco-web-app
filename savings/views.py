from django.views.generic import CreateView, DeleteView, UpdateView

from core.crud import ListPage, ModalDeleteMixin, ModalFormMixin

from .forms import SavingForm
from .models import Saving


class SavingList(ListPage):
    model = Saving
    page_title = "Savings"
    add_label = "Add saving"
    url_name = "saving"

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
