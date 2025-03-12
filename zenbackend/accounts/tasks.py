# your_app_name/tasks.py
import requests
from celery import shared_task
from accounts.utils import fetch_and_store_google_campaigns, scheduled_appointment_sync, fetch_campaigns_facebook, fetch_calls_for_last_days

@shared_task
def make_api_call():
    fetch_and_store_google_campaigns()
    scheduled_appointment_sync()
    fetch_campaigns_facebook()
    fetch_calls_for_last_days()

    return 
    
