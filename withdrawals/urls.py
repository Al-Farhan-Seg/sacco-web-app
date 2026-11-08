from core.crud import crud_urls

from .views import (
    WithdrawalCreate,
    WithdrawalDelete,
    WithdrawalList,
    WithdrawalUpdate,
)

urlpatterns = crud_urls(
    "withdrawals",
    "withdrawal",
    WithdrawalList,
    WithdrawalCreate,
    WithdrawalUpdate,
    WithdrawalDelete,
)
