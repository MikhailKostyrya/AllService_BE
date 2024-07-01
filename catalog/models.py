from django.db import models
from imageutils.fields import CustomImageField
from city.models import City
from users.models import ExecutorData


class Category(models.Model):
    category_name = models.CharField(max_length=200, null=False)
    photo = CustomImageField(upload_to='static/category', null=True, blank=True)

    def str(self):
        return self.category_name


class ServiceManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(deleted=False)


class Service(models.Model):
    name = models.CharField(max_length=200, null=False)
    content = models.TextField(null=False)
    timetable = models.JSONField(null=False, blank=True, default=dict)
    city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True, blank=True) 
    address = models.CharField(max_length=200, blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=False)
    executor = models.ForeignKey(ExecutorData, on_delete=models.CASCADE, null=False)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=False)
    photo = models.ImageField(upload_to='static/service', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    deleted = models.BooleanField(default=False)

    objects = ServiceManager()

    def str(self):
        return self.name
