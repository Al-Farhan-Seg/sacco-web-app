from core.crud import crud_urls

from .views import AccountCreate, AccountDelete, AccountList, AccountUpdate

urlpatterns = crud_urls(
    "accounts", "account", AccountList, AccountCreate, AccountUpdate, AccountDelete
)
