from django.views.generic import CreateView, DeleteView, UpdateView

from core.crud import ListPage, ModalDeleteMixin, ModalFormMixin

from .forms import LoanForm, LoanPaymentForm
from .models import Loan, LoanPayment


class LoanList(ListPage):
    model = Loan
    page_title = "Loans"
    add_label = "Add loan"
    url_name = "loan"
    search_fields = [
        "member__first_name",
        "member__last_name",
        "staff__first_name",
        "staff__last_name",
        "payment_period",
    ]
    search_codes = {"LN": "pk", "MEM": "member_id", "STF": "staff_id"}
    search_hint = "Search member, staff or LN-001"

    def get_queryset(self):
        return super().get_queryset().select_related("member", "staff")


class LoanCreate(ModalFormMixin, CreateView):
    model = Loan
    form_class = LoanForm


class LoanUpdate(ModalFormMixin, UpdateView):
    model = Loan
    form_class = LoanForm


class LoanDelete(ModalDeleteMixin, DeleteView):
    model = Loan
    delete_note = "its payments"


class PaymentList(ListPage):
    model = LoanPayment
    template_name = "loans/payment_list.html"
    page_title = "Loan payments"
    add_label = "Add loan payment"
    url_name = "payment"
    search_fields = [
        "loan__member__first_name",
        "loan__member__last_name",
    ]
    search_codes = {"PAY": "pk", "LN": "loan_id"}
    search_hint = "Search member, loan or PAY-001"

    def get_queryset(self):
        return super().get_queryset().select_related("loan__member")


class PaymentCreate(ModalFormMixin, CreateView):
    model = LoanPayment
    form_class = LoanPaymentForm


class PaymentUpdate(ModalFormMixin, UpdateView):
    model = LoanPayment
    form_class = LoanPaymentForm


class PaymentDelete(ModalDeleteMixin, DeleteView):
    model = LoanPayment
