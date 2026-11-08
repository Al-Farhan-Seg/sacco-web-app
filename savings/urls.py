from core.crud import crud_urls

from .views import SavingCreate, SavingDelete, SavingList, SavingUpdate

urlpatterns = crud_urls(
    "savings", "saving", SavingList, SavingCreate, SavingUpdate, SavingDelete
)
