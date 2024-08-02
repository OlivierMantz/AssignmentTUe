from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ('ACCOUNT_MANAGER', 'Account Manager'),
        ('CUSTOMER', 'Customer')
    )
    
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES)