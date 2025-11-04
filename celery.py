from celery.schedules import crontab
from .celery_app import app  # import your Celery app

app.conf.timezone = "Asia/Kolkata"

app.conf.beat_schedule = {
    "deactivate-expired-3-times-daily": {
        "task": "admin_functions.tasks.deactivate_expired_client_coaches",
        "schedule": (
            crontab(hour=0, minute=10)   # 12:10 AM
            | crontab(hour=8, minute=10)  # 8:10 AM
            | crontab(hour=16, minute=10) # 4:10 PM
        ),
    },
}
