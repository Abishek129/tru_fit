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


@shared_task
def send_lead_mails(name, email):
    subject = "Thanks for Contacting Tru Fit"

    message = f"""
Hi {name},
Thank you for reaching out to Tru Fit! 
Our support team will be in touch within 1–2 business days to understand your goals and answer any questions you have.
In the meantime, feel free to browse our website to learn more about what we do. You can check out our Coaches page to explore the different professionals you might work with, and visit our About page to get to know our company’s story and values.
Also, don't forget to follow us on Instagram for practical fitness advice, updates, and a look at our client transformations: https://www.instagram.com/betrufit
We look forward to becoming a part of your fitness journey!
Warm regards,
Team Tru Fit

"""

    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email],
    )
