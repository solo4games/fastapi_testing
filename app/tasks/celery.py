from celery import Celery

from app.config import settings


celery_app = Celery('tasks',
                    broker=settings.BROKER_URL,
                    backend="rpc://",
                    include=['app.tasks.tasks'])