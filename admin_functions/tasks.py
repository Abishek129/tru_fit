from celery import shared_task
from django.utils import timezone
from .models import Clinet_Coach

@shared_task
def deactivate_expired_client_coaches():
    today = timezone.localdate()
    expired = Clinet_Coach.objects.filter(active=True, end_date__lt=today)
    count = expired.update(active=False)
    return f"{count} client-coach relations deactivated"
