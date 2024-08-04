import datetime
from django.apps import apps
from django.db.models import Avg, Count, Sum
from execution.models import Job
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()
Order = apps.get_model('execution', 'Order')

job_stats_model = apps.get_model("stat_analysis", "JobReportResult")
order_stats_model = apps.get_model("stat_analysis", "OrderReportResult")
user_stats_model = apps.get_model("stat_analysis", "UserReportResult")
report_model = apps.get_model("stat_analysis", "Report")

def calculate_job_stats(quarter_from, year_from, quarter_to, year_to):
    start_date, end_date = get_date_range(quarter_from, year_from, quarter_to, year_to)

    jobs = Job.objects.filter(starting_date__gte=start_date, end_date__lte=end_date)
    total_jobs = jobs.count()
    
    avg_completion_time_regular = jobs.filter(job_type='regular').aggregate(Avg('completion_time'))['completion_time__avg'] or 0
    avg_completion_time_wafer_run = jobs.filter(job_type='wafer_run').aggregate(Avg('completion_time'))['completion_time__avg'] or 0
    
    jobs_by_status = jobs.values('state').annotate(count=Count('state'))
    jobs_created = next((item['count'] for item in jobs_by_status if item['state'] == 'created'), 0)
    jobs_active = next((item['count'] for item in jobs_by_status if item['state'] == 'active'), 0)
    jobs_completed = next((item['count'] for item in jobs_by_status if item['state'] == 'completed'), 0)

    report = get_or_create_report(quarter_from, year_from, quarter_to, year_to)

    job_stats, _ = job_stats_model.objects.update_or_create(
        report=report,
        defaults={
            'total_jobs': total_jobs,
            'avg_completion_time_regular': avg_completion_time_regular,
            'avg_completion_time_wafer_run': avg_completion_time_wafer_run,
            'jobs_created': jobs_created,
            'jobs_active': jobs_active,
            'jobs_completed': jobs_completed
        }
    )

    return job_stats

def calculate_order_stats(quarter_from, year_from, quarter_to, year_to):
    start_date, end_date = get_date_range(quarter_from, year_from, quarter_to, year_to)

    orders = Order.objects.filter(created_at__gte=start_date, created_at__lte=end_date)
    total_orders = orders.count()
    total_revenue = orders.aggregate(Sum('job__price'))['job__price__sum'] or 0
    average_order_value = total_revenue / total_orders if total_orders > 0 else 0

    report = get_or_create_report(quarter_from, year_from, quarter_to, year_to)

    order_stats, _ = order_stats_model.objects.update_or_create(
        report=report,
        defaults={
            'total_orders': total_orders,
            'total_revenue': total_revenue,
            'average_order_value': average_order_value
        }
    )

    return order_stats

def calculate_user_stats(quarter_from, year_from, quarter_to, year_to):
    start_date, end_date = get_date_range(quarter_from, year_from, quarter_to, year_to)

    total_users = User.objects.filter(date_joined__lte=end_date).count()
    new_users = User.objects.filter(date_joined__gte=start_date, date_joined__lte=end_date).count()

    report = get_or_create_report(quarter_from, year_from, quarter_to, year_to)

    user_stats, _ = user_stats_model.objects.update_or_create(
        report=report,
        defaults={
            'total_users': total_users,
            'new_users': new_users
        }
    )

    return user_stats

def get_or_create_report(quarter_from, year_from, quarter_to, year_to):
    # Use timezone.now() for timezone-aware datetime
    return report_model.objects.get_or_create(
        quarter_from=quarter_from,
        year_from=year_from,
        quarter_to=quarter_to,
        year_to=year_to,
        defaults={
            'title': f'Report {year_from}Q{quarter_from} - {year_to}Q{quarter_to}',
            'created_at': timezone.now(),  # Ensure timezone-aware datetime
        }
    )[0]

def get_date_range(quarter_from, year_from, quarter_to, year_to):
    start_date_from, _ = get_quarter_dates(quarter_from, year_from)
    _, end_date_to = get_quarter_dates(quarter_to, year_to)
    return start_date_from, end_date_to

def get_quarter_dates(quarter, year):
    if quarter == 'Q1':
        start_date = datetime.date(year, 1, 1)
        end_date = datetime.date(year, 3, 31)
    elif quarter == 'Q2':
        start_date = datetime.date(year, 4, 1)
        end_date = datetime.date(year, 6, 30)
    elif quarter == 'Q3':
        start_date = datetime.date(year, 7, 1)
        end_date = datetime.date(year, 9, 30)
    elif quarter == 'Q4':
        start_date = datetime.date(year, 10, 1)
        end_date = datetime.date(year, 12, 31)
    else:
        raise ValueError("Invalid quarter. Please use 'Q1', 'Q2', 'Q3', or 'Q4'.")
    return start_date, end_date