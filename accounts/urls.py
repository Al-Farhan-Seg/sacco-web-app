from django.urls import path

from . import views

urlpatterns = [
    path("accounts/", views.account_list, name="account_list"),
    path("accounts/add/", views.account_create, name="account_add"),
    path("accounts/<int:pk>/edit/", views.account_update, name="account_edit"),
    path("accounts/<int:pk>/delete/", views.account_delete, name="account_delete"),
]
