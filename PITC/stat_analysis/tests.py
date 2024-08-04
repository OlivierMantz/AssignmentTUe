from django.test import TestCase
from django.utils import timezone
from django.apps import apps
from django.contrib.auth import get_user_model
from datetime import timedelta
from execution.models import Job, ServiceProvider, Order, AccountManager
from stat_analysis.models import Report, JobReportResult, OrderReportResult, UserReportResult
from stat_analysis.stat_utils import calculate_job_stats, calculate_order_stats, calculate_user_stats

User = get_user_model()
ServiceProvider = apps.get_model('execution', 'ServiceProvider')
Order = apps.get_model('execution', 'Order')
AccountManager = apps.get_model('execution', 'AccountManager')

class StatisticsTestCase(TestCase):
    def setUp(self):
        # Create users
        self.user = User.objects.create_user(username="testuser", password="testpass", user_type="CUSTOMER")
        self.manager_user = User.objects.create_user(username="manager", password="managerpass", user_type="ACCOUNT_MANAGER")
        
        # Get the automatically created AccountManager instance
        self.account_manager = self.manager_user.account_manager
        
        self.service_provider = ServiceProvider.objects.create(name="Test Provider")

        self.year = timezone.now().year
        self.quarter = f"Q{(timezone.now().month - 1) // 3 + 1}"

        # Create jobs
        Job.objects.create(job_name="Job 1", state="created", job_type="regular", starting_date=timezone.now(), end_date=timezone.now() + timedelta(days=5), completion_time=5, service_provider=self.service_provider, price=100)
        Job.objects.create(job_name="Job 2", state="active", job_type="wafer_run", starting_date=timezone.now(), end_date=timezone.now() + timedelta(days=10), completion_time=10, service_provider=self.service_provider, price=200)
        Job.objects.create(job_name="Job 3", state="completed", job_type="regular", starting_date=timezone.now(), end_date=timezone.now() + timedelta(days=7), completion_time=7, service_provider=self.service_provider, price=150)

        # Create orders
        for job in Job.objects.all():
            Order.objects.create(customer=self.user.customer, account_manager=self.account_manager, job=job, quantity=1)


    def test_job_statistics(self):
        stats = calculate_job_stats(self.quarter, self.year, self.quarter, self.year)
        self.assertEqual(stats.total_jobs, 3)
        self.assertEqual(stats.jobs_created, 1)
        self.assertEqual(stats.jobs_active, 1)
        self.assertEqual(stats.jobs_completed, 1)
        self.assertAlmostEqual(stats.avg_completion_time_regular, 6, places=2)
        self.assertAlmostEqual(stats.avg_completion_time_wafer_run, 10, places=2)

    def test_order_statistics(self):
        stats = calculate_order_stats(self.quarter, self.year, self.quarter, self.year)
        self.assertEqual(stats.total_orders, 3)
        self.assertEqual(stats.total_revenue, 450)
        self.assertAlmostEqual(stats.average_order_value, 150, places=2)

    def test_user_statistics(self):
        stats = calculate_user_stats(self.quarter, self.year, self.quarter, self.year)
        self.assertEqual(stats.total_users, 2)
        self.assertEqual(stats.new_users, 2)