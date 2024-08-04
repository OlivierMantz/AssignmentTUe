from django.db import models
import uuid
from .service_provider import ServiceProvider

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
