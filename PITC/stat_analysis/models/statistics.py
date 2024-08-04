from django.db import models
from .report import Report

class JobReportResult(models.Model):
    report = models.OneToOneField(Report, on_delete=models.CASCADE)
    total_jobs = models.IntegerField()
    avg_completion_time_regular = models.FloatField()
    avg_completion_time_wafer_run = models.FloatField()
    jobs_created = models.IntegerField()
    jobs_active = models.IntegerField()
    jobs_completed = models.IntegerField()

class OrderReportResult(models.Model):
    report = models.OneToOneField(Report, on_delete=models.CASCADE)
    total_orders = models.IntegerField()
    total_revenue = models.DecimalField(max_digits=10, decimal_places=2)
    average_order_value = models.DecimalField(max_digits=10, decimal_places=2)

class UserReportResult(models.Model):
    report = models.OneToOneField(Report, on_delete=models.CASCADE)
    total_users = models.IntegerField()
    new_users = models.IntegerField()

    class Meta:
        app_label = 'stat_analysis'
