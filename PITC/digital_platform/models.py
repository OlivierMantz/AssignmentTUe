from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver
import uuid

class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ('ACCOUNT_MANAGER', 'Account Manager'),
        ('CUSTOMER', 'Customer')
    )
    
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES)

class ServiceProvider(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

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

class Customer(models.Model):
    user = models.OneToOneField(User, primary_key=True, on_delete=models.CASCADE, related_name='customer')
    assigned_account_manager = models.ForeignKey(AccountManager, on_delete=models.SET_NULL, null=True, related_name='managed_customers')

    def __str__(self):
        return f"Customer: {self.user.username}"

class Job(models.Model):
    JOB_TYPE_CHOICES = [
        ('regular', 'Regular'),
        ('wafer_run', 'Wafer Run'),
    ]
    STATE_CHOICES = [
        ('created', 'Created'),
        ('active', 'Active'),
        ('completed', 'Completed'),
    ]

    job_id = models.CharField(max_length=10, unique=True, primary_key=True, editable=False)
    job_name = models.CharField(max_length=200)
    state = models.CharField(max_length=100, choices=STATE_CHOICES)
    job_type = models.CharField(max_length=20, choices=JOB_TYPE_CHOICES)
    starting_date = models.DateTimeField()
    end_date = models.DateTimeField()
    completion_time = models.FloatField(help_text="Time in days which were spent to complete the job.")
    service_provider = models.ForeignKey(ServiceProvider, on_delete=models.CASCADE, related_name='jobs')
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def save(self, *args, **kwargs):
        if not self.job_id:
            self.job_id = str(uuid.uuid4().hex)[:10]
        super().save(*args, **kwargs)

    def __str__(self):
        return self.job_name

class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='orders')
    account_manager = models.ForeignKey(AccountManager, on_delete=models.SET_NULL, null=True, related_name='managed_orders')
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='orders')
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order {self.id} by {self.customer}"

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        if instance.user_type == 'ACCOUNT_MANAGER':
            AccountManager.objects.create(user=instance)
        elif instance.user_type == 'CUSTOMER':
            Customer.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if instance.user_type == 'ACCOUNT_MANAGER':
        AccountManager.objects.get_or_create(user=instance)
    elif instance.user_type == 'CUSTOMER':
        Customer.objects.get_or_create(user=instance)