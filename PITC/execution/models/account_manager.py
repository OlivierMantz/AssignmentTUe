from django.db import models
from .user import User
from .service_provider import ServiceProvider

class AccountManager(models.Model):
    user = models.OneToOneField(User, primary_key=True, on_delete=models.CASCADE, related_name='account_manager')
    managed_providers = models.ManyToManyField(ServiceProvider, through='ServiceProviderAccountManager', related_name='account_managers')

    def __str__(self):
        return f"Account Manager: {self.user.username}"

class ServiceProviderAccountManager(models.Model):
    account_manager = models.ForeignKey(AccountManager, on_delete=models.CASCADE)
    service_provider = models.ForeignKey(ServiceProvider, on_delete=models.CASCADE)
    assigned_date = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ('account_manager', 'service_provider')
