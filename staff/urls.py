from core.crud import crud_urls

from .views import StaffCreate, StaffDelete, StaffList, StaffUpdate

urlpatterns = crud_urls(
    "staff", "staff", StaffList, StaffCreate, StaffUpdate, StaffDelete
)
