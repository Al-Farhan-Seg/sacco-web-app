from django.views.generic import CreateView, DeleteView, UpdateView

from core.crud import ListPage, ModalDeleteMixin, ModalFormMixin

from .forms import AccountForm
from .models import Account


class AccountList(ListPage):
    model = Account
    page_title = "Accounts"
    add_label = "Add account"
    url_name = "account"

    def get_queryset(self):
        return super().get_queryset().select_related("member")


class AccountCreate(ModalFormMixin, CreateView):
    model = Account
    form_class = AccountForm


class AccountUpdate(ModalFormMixin, UpdateView):
    model = Account
    form_class = AccountForm


class AccountDelete(ModalDeleteMixin, DeleteView):
    model = Account
    delete_note = "its savings"
