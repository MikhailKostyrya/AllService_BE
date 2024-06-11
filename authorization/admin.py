from django.contrib import admin

from authorization.models import User, ExecutorData


admin.site.register(ExecutorData)
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'second_name', 'email', 'contact', 'is_staff', 'is_executor']
    search_fields = ['first_name', 'second_name', 'email', 'contact', 'is_staff', 'is_executor']