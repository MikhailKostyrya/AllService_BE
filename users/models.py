from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.forms import ValidationError
from AllService_BE import settings


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Users must have an email address')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    first_name = models.CharField(max_length=255)
    second_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    photo = models.ImageField(upload_to='static/user', null=True, blank=True)
    contact = models.CharField(max_length=255) # change to number
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_executor = models.BooleanField(default=False)
    executor_data = models.OneToOneField('ExecutorData', on_delete=models.SET_NULL, null=True, unique=True, blank=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'second_name']

    def __str__(self):
        return self.email
    
    def clean(self):
        super().clean()
        if self.is_executor and not self.executor_data:
            raise ValidationError({
                'executor_data': 'This field is required when "Is executor" is checked.'
            })


class ExecutorData(models.Model):
    content = models.CharField(max_length=255)
    contact_executor = models.CharField(max_length=255)
    inn = models.CharField(max_length=255)
