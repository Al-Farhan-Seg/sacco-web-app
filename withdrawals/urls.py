from django.urls import path

from . import views

urlpatterns = [
    path("withdrawals/", views.withdrawal_list, name="withdrawal_list"),
    path("withdrawals/add/", views.withdrawal_create, name="withdrawal_add"),
    path("withdrawals/<int:pk>/edit/", views.withdrawal_update, name="withdrawal_edit"),
    path("withdrawals/<int:pk>/delete/", views.withdrawal_delete, name="withdrawal_delete"),
]
