from django.contrib import admin

from authorization.models import User, ExecutorData

admin.site.register(User)
admin.site.register(ExecutorData)
