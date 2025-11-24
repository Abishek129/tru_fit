import os
from celery import Celery
from celery.schedules import crontab
from datetime import timedelta


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "trufit_backend.settings")

app = Celery("trufit_backend")

# Read CELERY_* from Django settings
app.config_from_object("django.conf:settings", namespace="CELERY")

# Autodiscover tasks.py across installed apps
app.autodiscover_tasks()

# Timezone (matches your need)
app.conf.timezone = "Asia/Kolkata"

# Run the task 3 times a day at 00:10, 08:10, 16:10
app.conf.beat_schedule = {
    "deactivate-expired-3x-daily": {
        "task": "admin_functions.tasks.deactivate_expired_client_coaches",
        "schedule": crontab(minute=10, hour="0,8,16"),
    },
    "delete-inactive-daily": {
        "task": "admin_functions.tasks.delete_inactive_client_coaches", 
        "schedule": crontab(minute=0, hour=18),  
        }
    ,
    "test-task-every-30-seconds": {
        "task": "admin_functions.tasks.run_simple_task",
        "schedule": timedelta(seconds=30),
    },

        
}
