from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ('ACCOUNT_MANAGER', 'Account Manager'),
        ('CUSTOMER', 'Customer')
    )
    
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES)

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        if instance.user_type == 'ACCOUNT_MANAGER':
            from .account_manager import AccountManager
            AccountManager.objects.create(user=instance)
        elif instance.user_type == 'CUSTOMER':
            from .customer import Customer
            Customer.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if instance.user_type == 'ACCOUNT_MANAGER':
        from .account_manager import AccountManager
        if hasattr(instance, 'account_manager'):
            instance.account_manager.save()
    elif instance.user_type == 'CUSTOMER':
        from .customer import Customer
        if hasattr(instance, 'customer'):
            instance.customer.save()