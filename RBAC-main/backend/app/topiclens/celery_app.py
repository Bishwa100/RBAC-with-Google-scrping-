"""
Celery Configuration for RBAC + TopicLens
"""
from celery import Celery
from app.topiclens.config import topiclens_settings

# Create Celery app
celery_app = Celery(
    "topiclens",
    broker=topiclens_settings.celery_broker_url,
    backend=topiclens_settings.celery_result_backend,
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1 hour
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=50,
)

# Auto-discover tasks
celery_app.autodiscover_tasks(["app.topiclens"])
