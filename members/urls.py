from core.crud import crud_urls

from .views import MemberCreate, MemberDelete, MemberList, MemberUpdate

urlpatterns = crud_urls(
    "members", "member", MemberList, MemberCreate, MemberUpdate, MemberDelete
)
