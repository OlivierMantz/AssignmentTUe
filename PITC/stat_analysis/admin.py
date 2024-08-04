from django.contrib import admin
from .models import Report, JobReportResult, OrderReportResult, UserReportResult

class JobReportResultInline(admin.StackedInline):
    model = JobReportResult

class OrderReportResultInline(admin.StackedInline):
    model = OrderReportResult

class UserReportResultInline(admin.StackedInline):
    model = UserReportResult

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at', 'year_from', 'quarter_from', 'year_to', 'quarter_to')
    list_filter = ('year_from', 'year_to', 'created_at')
    search_fields = ('title',)
    inlines = [JobReportResultInline, OrderReportResultInline, UserReportResultInline]

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for instance in instances:
            if not instance.pk:
                from .stat_utils import calculate_job_statistics, calculate_order_statistics, calculate_user_statistics
                
                if isinstance(instance, JobReportResult):
                    stats = calculate_job_statistics(form.instance.year_from, form.instance.quarter_from, form.instance.year_to, form.instance.quarter_to)
                    for key, value in stats.items():
                        setattr(instance, key, value)
                elif isinstance(instance, OrderReportResult):
                    stats = calculate_order_statistics(form.instance.year_from, form.instance.quarter_from, form.instance.year_to, form.instance.quarter_to)
                    for key, value in stats.items():
                        setattr(instance, key, value)
                elif isinstance(instance, UserReportResult):
                    stats = calculate_user_statistics(form.instance.year_from, form.instance.quarter_from, form.instance.year_to, form.instance.quarter_to)
                    for key, value in stats.items():
                        setattr(instance, key, value)
            
            instance.save()
        formset.save_m2m()