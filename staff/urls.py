from django.urls import path

from . import views

urlpatterns = [
    path("staff/", views.staff_list, name="staff_list"),
    path("staff/add/", views.staff_create, name="staff_add"),
    path("staff/<int:pk>/edit/", views.staff_update, name="staff_edit"),
    path("staff/<int:pk>/delete/", views.staff_delete, name="staff_delete"),
]
