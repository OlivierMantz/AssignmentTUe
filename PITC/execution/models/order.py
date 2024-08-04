from django.db import models
from .customer import Customer
from .account_manager import AccountManager
from .job import Job

class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='orders')
    account_manager = models.ForeignKey(AccountManager, on_delete=models.SET_NULL, null=True, related_name='managed_orders')
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='orders')
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order {self.id} by {self.customer}"