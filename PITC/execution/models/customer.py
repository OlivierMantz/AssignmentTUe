from django.db import models
from .user import User
from .account_manager import AccountManager

class Customer(models.Model):
    user = models.OneToOneField(User, primary_key=True, on_delete=models.CASCADE, related_name='customer')
    assigned_account_manager = models.ForeignKey(AccountManager, on_delete=models.SET_NULL, null=True, related_name='managed_customers')

    def __str__(self):
        return f"Customer: {self.user.username}"
