from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ('ACCOUNT_MANAGER', 'Account Manager'),
        ('CUSTOMER', 'Customer')
    )
    
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES)

    def save(self, *args, **kwargs):
        creating = self._state.adding
        super().save(*args, **kwargs)
        if creating:
            if self.user_type == 'ACCOUNT_MANAGER':
                from .account_manager import AccountManager
                AccountManager.objects.create(user=self)
            elif self.user_type == 'CUSTOMER':
                from .customer import Customer
                Customer.objects.create(user=self)

