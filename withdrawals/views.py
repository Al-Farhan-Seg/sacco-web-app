from django.views.generic import CreateView, DeleteView, UpdateView

from core.crud import ListPage, ModalDeleteMixin, ModalFormMixin

from .forms import WithdrawalForm
from .models import Withdrawal


class WithdrawalList(ListPage):
    model = Withdrawal
    page_title = "Withdrawals"
    add_label = "Add withdrawal"
    url_name = "withdrawal"

    def get_queryset(self):
        return super().get_queryset().select_related("member")


class WithdrawalCreate(ModalFormMixin, CreateView):
    model = Withdrawal
    form_class = WithdrawalForm


class WithdrawalUpdate(ModalFormMixin, UpdateView):
    model = Withdrawal
    form_class = WithdrawalForm


class WithdrawalDelete(ModalDeleteMixin, DeleteView):
    model = Withdrawal
