from django.test import TestCase
from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status
from .models import User, ServiceProvider, AccountManager, Customer, Job, Order
from django.utils import timezone

class OrderCreationAndVisibilityTests(APITestCase):
    def setUp(self):
        # Create users
        self.user_manager1 = User.objects.create_user(username='manager1', password='12345', user_type='ACCOUNT_MANAGER')
        self.user_manager2 = User.objects.create_user(username='manager2', password='12345', user_type='ACCOUNT_MANAGER')
        self.user_customer1 = User.objects.create_user(username='customer1', password='12345', user_type='CUSTOMER')
        self.user_customer2 = User.objects.create_user(username='customer2', password='12345', user_type='CUSTOMER')

        # Get the automatically created AccountManager and Customer instances
        self.account_manager1 = self.user_manager1.account_manager
        self.account_manager2 = self.user_manager2.account_manager
        self.customer1 = self.user_customer1.customer
        self.customer2 = self.user_customer2.customer

        # Assign account managers to customers
        self.customer1.assigned_account_manager = self.account_manager1
        self.customer1.save()
        self.customer2.assigned_account_manager = self.account_manager2
        self.customer2.save()

        # Create service providers
        self.service_provider1 = ServiceProvider.objects.create(name='Provider 1', description='Description 1')
        self.service_provider2 = ServiceProvider.objects.create(name='Provider 2', description='Description 2')

        # Associate service providers with account managers
        self.account_manager1.managed_providers.add(self.service_provider1)
        self.account_manager2.managed_providers.add(self.service_provider2)

        # Create jobs
        self.job1 = Job.objects.create(
            job_name='Job 1',
            state='created',
            job_type='regular',
            starting_date=timezone.now(),
            end_date=timezone.now() + timezone.timedelta(days=1),
            completion_time=1.0,
            service_provider=self.service_provider1,
            price=100.00
        )
        self.job2 = Job.objects.create(
            job_name='Job 2',
            state='created',
            job_type='regular',
            starting_date=timezone.now(),
            end_date=timezone.now() + timezone.timedelta(days=1),
            completion_time=1.0,
            service_provider=self.service_provider2,
            price=150.00
        )

    def test_customer_order_with_valid_job_and_account_manager(self):
        url = reverse('order-list')
        data = {
            'customer': self.customer1.user.id,
            'account_manager': self.account_manager1.user.id,
            'job': self.job1.job_id,
            'quantity': 1
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Order.objects.count(), 1)

    def test_customer_order_with_invalid_account_manager(self):
        url = reverse('order-list')
        data = {
            'customer': self.customer1.user.id,
            'account_manager': self.account_manager2.user.id,  # This is not customer1's assigned account manager
            'job': self.job1.job_id,
            'quantity': 1
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Order.objects.count(), 0)

    def test_customer_order_with_unmanaged_service_provider(self):
        url = reverse('order-list')
        data = {
            'customer': self.customer1.user.id,
            'account_manager': self.account_manager1.user.id,
            'job': self.job2.job_id,  # This job is from a provider not managed by account_manager1
            'quantity': 1
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Order.objects.count(), 0)

    def test_account_manager_order_visibility(self):
        # Create orders for both customers
        order1 = Order.objects.create(customer=self.customer1, account_manager=self.account_manager1, job=self.job1, quantity=1)
        order2 = Order.objects.create(customer=self.customer2, account_manager=self.account_manager2, job=self.job2, quantity=1)

        # Test visibility for account_manager1
        url = reverse('order-list') + f'?account_manager_id={self.account_manager1.user.id}'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], order1.id)

        # Test visibility for account_manager2
        url = reverse('order-list') + f'?account_manager_id={self.account_manager2.user.id}'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], order2.id)

    def test_customer_order_visibility(self):
        # Create orders for both customers
        order1 = Order.objects.create(customer=self.customer1, account_manager=self.account_manager1, job=self.job1, quantity=1)
        order2 = Order.objects.create(customer=self.customer2, account_manager=self.account_manager2, job=self.job2, quantity=1)

        # Test visibility for customer1
        url = reverse('order-list') + f'?customer_id={self.customer1.user.id}'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], order1.id)

        # Test visibility for customer2
        url = reverse('order-list') + f'?customer_id={self.customer2.user.id}'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], order2.id)