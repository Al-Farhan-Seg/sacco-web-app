from django.contrib import admin

from .models import Staff


@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = ("code", "first_name", "last_name", "position", "role", "contact")
    list_filter = ("role", "gender")
    search_fields = ("first_name", "last_name", "position", "contact")
