import os
from celery import Celery

# set the standard Django settings module for celery
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eshop.settings')
app = Celery('eshop')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
