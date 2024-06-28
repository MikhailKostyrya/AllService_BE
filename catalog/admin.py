from django.contrib import admin

from catalog.models import Category, Service



@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'content', 'timetable', 'city', 'address', 'price', 'executor_id', 'category_id']
    search_fields = ['name', 'content', 'city', 'address', 'price', 'category_id']


@admin.register(Category)
class UserAdmin(admin.ModelAdmin):
    list_display = ['id', 'category_name']
    search_fields = ['id', 'category_name']
