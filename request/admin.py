from .models import Request
from django.contrib import admin


@admin.register(Request)
class RequestAdmin(admin.ModelAdmin):
    list_display = ['id', 'status', 'address', 'create_date', 'time', 'user', 'service']
    search_fields = ['id', 'status', 'create_date', 'time', 'user', 'service']