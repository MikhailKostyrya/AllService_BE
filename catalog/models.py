from django.db import models

from users.models import ExecutorData


class Category(models.Model):
    category_name = models.CharField(max_length=200, null=False)

    def str(self):
        return self.category_name


class Service(models.Model):
    name = models.CharField(max_length=200, null=False)
    content = models.TextField(null=False)
    timetable = models.CharField(max_length=200, null=False)
    address = models.CharField(max_length=200, blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=False)
    executor = models.ForeignKey(ExecutorData, on_delete=models.CASCADE, null=False)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=False)

    def str(self):
        return self.name
