from .models import Request
from django.contrib import admin


@admin.register(Request)
class RequestAdmin(admin.ModelAdmin):
    list_display = ['id', 'status', 'address', 'create_date', 'date_times', 'user', 'service', "price"]
    search_fields = ['id', 'status', 'create_date', 'date_times', 'user', 'service', "price"]