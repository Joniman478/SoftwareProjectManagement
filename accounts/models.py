from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models


class CustomUserManager(BaseUserManager):
    def create_user(self, email, first_name, last_name, password=None, **extra_fields):
        if not email:
            raise ValueError('The email field must be set')

        email = self.normalize_email(email)
        user = self.model(email=email, first_name=first_name, last_name=last_name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, first_name, last_name, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('account_status', 'active')

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, first_name, last_name, password, **extra_fields)


class Account(AbstractBaseUser, PermissionsMixin):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, unique=True)

    class Role(models.TextChoices):
        ADMIN = 'SYSTEM_ADMIN', 'System administrator'
        IMPORTER = 'IMPORTER', 'Importer'
        CUSTOMS = 'CUSTOMS_OFFICER', 'Customs Officer'
        SHIPPING = 'POST_SHIPPING', 'Post/Shipping Office'
        FORWARDER = 'FREIGHT_FORWARDER', 'Freight Forwarder'
        STAKEHOLDER = 'STAKEHOLDER', 'General Stakeholder'

    role = models.CharField(max_length=30, choices=Role.choices, default=Role.STAKEHOLDER)
    account_status = models.CharField(max_length=20, default='active')
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    last_login = models.DateTimeField(blank=True, null=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    def __str__(self):
        return self.email

    @property
    def is_importer(self):
        return self.role == self.Role.IMPORTER

    @property
    def is_customs(self):
        return self.role == self.Role.CUSTOMS

    @property
    def is_shipping(self):
        return self.role == self.Role.SHIPPING

    @property
    def is_forwarder(self):
        return self.role == self.Role.FORWARDER

    @property
    def is_stakeholder(self):
        return self.role == self.Role.STAKEHOLDER
