from django.db import models

class Report(models.Model):
    # metadata
    title = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Report settings
    quarter_from = models.CharField(max_length=2, choices=[('Q1', 'Q1'), ('Q2', 'Q2'), ('Q3', 'Q3'), ('Q4', 'Q4')])
    year_from = models.IntegerField()
    quarter_to = models.CharField(max_length=2, choices=[('Q1', 'Q1'), ('Q2', 'Q2'), ('Q3', 'Q3'), ('Q4', 'Q4')])
    year_to = models.IntegerField()

    # PDF file
    pdf_file = models.FileField(upload_to='reports/', null=True, blank=True)

    def __str__(self):
        return f"{self.title} - {self.year_from} Q{self.quarter_from} to {self.year_to} Q{self.quarter_to}"

    class Meta:
        app_label = 'stat_analysis'