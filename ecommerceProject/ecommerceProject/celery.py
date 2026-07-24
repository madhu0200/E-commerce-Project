import os
from celery import Celery

# Set default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerceProject.settings')

app = Celery('ecommerceProject')

# Read config from Django settings using a 'CELERY_' prefix
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover asynchronous tasks in registered app files (tasks.py)
app.autodiscover_tasks()