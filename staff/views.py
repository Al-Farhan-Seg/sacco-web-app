from django.views.generic import CreateView, DeleteView, UpdateView

from core.crud import ListPage, ModalDeleteMixin, ModalFormMixin

from .forms import StaffForm
from .models import Staff


class StaffList(ListPage):
    model = Staff
    page_title = "Staff"
    add_label = "Add staff"
    url_name = "staff"


class StaffCreate(ModalFormMixin, CreateView):
    model = Staff
    form_class = StaffForm


class StaffUpdate(ModalFormMixin, UpdateView):
    model = Staff
    form_class = StaffForm


class StaffDelete(ModalDeleteMixin, DeleteView):
    model = Staff
    delete_note = "the savings and loans they recorded"
