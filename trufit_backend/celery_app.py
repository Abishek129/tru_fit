import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "trufit_backend.settings")

app = Celery("trufit_backend")

# Load config from Django settings with CELERY_ prefix
app.config_from_object("django.conf:settings", namespace="CELERY")

# Auto-discover tasks.py in all installed apps
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f"Request: {self.request!r}")
