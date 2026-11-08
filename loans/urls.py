from core.crud import crud_urls

from .views import (
    LoanCreate,
    LoanDelete,
    LoanList,
    LoanUpdate,
    PaymentCreate,
    PaymentDelete,
    PaymentList,
    PaymentUpdate,
)

urlpatterns = crud_urls(
    "loans", "loan", LoanList, LoanCreate, LoanUpdate, LoanDelete
) + crud_urls(
    "loan-payments",
    "payment",
    PaymentList,
    PaymentCreate,
    PaymentUpdate,
    PaymentDelete,
)
