from django.contrib import admin

from .models import Member


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ("code", "first_name", "last_name", "contact", "email", "gender")
    list_filter = ("gender",)
    search_fields = ("first_name", "last_name", "contact", "email")
