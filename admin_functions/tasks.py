from celery import shared_task
from django.utils import timezone
from .models import Clinet_Coach

@shared_task
def deactivate_expired_client_coaches():
    today = timezone.localdate()
    expired = Clinet_Coach.objects.filter(active=True, end_date__lt=today)
    count = expired.update(active=False)
    return f"{count} client-coach relations deactivated"

@shared_task
def delete_inactive_client_coaches():
    inactive = Clinet_Coach.objects.filter(us_revenue=None, inr_revenue=None)
    count, _ = inactive.delete()
    return f"{count} inactive client-coach relations deleted"   

@shared_task
def simple_task():
    return "This is a simple test task."



import logging
logger = logging.getLogger(__name__)

logger = logging.getLogger("ws")

@shared_task
def run_simple_task():
    logger.info("Simple task is running.")
    return "Simple task completed."


from django.core.mail import send_mail

from django.conf import settings

@shared_task
def send_plan_mail(client_name, client_email, plan_name, coach, amount, currency):
    from django.core.mail import send_mail
    subject = "Your Plan Purchase Confirmation"
    message = f"Thank you {client_name} for purchasing the {plan_name} with {coach} for {amount} {currency}."
    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[client_email],    

    )
