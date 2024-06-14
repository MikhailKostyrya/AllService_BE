from django.contrib import admin

from .models import User, ExecutorData


@admin.register(ExecutorData)
class UserAdmin(admin.ModelAdmin):
    list_display = ['id', 'inn', 'contact_executor']
    search_fields = ['id', 'inn', 'contact_executor']
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['id', 'first_name', 'second_name', 'email', 'contact', 'is_staff', 'is_executor']
    search_fields = ['first_name', 'second_name', 'email', 'contact', 'is_staff', 'is_executor']
