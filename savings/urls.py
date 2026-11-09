from django.urls import path

from . import views

urlpatterns = [
    path("savings/", views.saving_list, name="saving_list"),
    path("savings/add/", views.saving_create, name="saving_add"),
    path("savings/<int:pk>/edit/", views.saving_update, name="saving_edit"),
    path("savings/<int:pk>/delete/", views.saving_delete, name="saving_delete"),
]
