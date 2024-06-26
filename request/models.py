from django.db import models

from catalog.models import Service
from users.models import User


class Status(models.TextChoices):
    PENDING = 'Pending', 'Pending'
    APPROVED = 'Approved', 'Approved'
    REJECTED = 'Rejected', 'Rejected'
    COMPLETED = 'Completed', 'Completed'


class Request(models.Model):
    id = models.AutoField(primary_key=True)
    status = models.CharField(max_length=50, choices=Status.choices, default=Status.PENDING)
    address = models.CharField(max_length=255, null=False)
    create_date = models.DateTimeField(auto_now_add=True)
    time = models.DateTimeField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)

    def __str__(self):
        return f'Request {self.id}'
