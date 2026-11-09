from django.urls import path

from . import views

urlpatterns = [
    path("loans/", views.loan_list, name="loan_list"),
    path("loans/add/", views.loan_create, name="loan_add"),
    path("loans/<int:pk>/edit/", views.loan_update, name="loan_edit"),
    path("loans/<int:pk>/delete/", views.loan_delete, name="loan_delete"),
    path("loan-payments/", views.payment_list, name="payment_list"),
    path("loan-payments/add/", views.payment_create, name="payment_add"),
    path("loan-payments/<int:pk>/edit/", views.payment_update, name="payment_edit"),
    path("loan-payments/<int:pk>/delete/", views.payment_delete, name="payment_delete"),
]
