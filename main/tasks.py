from celery import shared_task
from .check_intercom import get_open_conversations


@shared_task
def start():
    get_open_conversations()
    print("Task Done")
