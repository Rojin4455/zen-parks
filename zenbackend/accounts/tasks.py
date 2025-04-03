# your_app_name/tasks.py
import requests
from celery import shared_task
from accounts.models import GHLAuthCredentials
from decouple import config
from accounts.utils import fetch_and_store_google_campaigns, fetch_campaigns_facebook, fetch_calls_for_last_days,appoinment_fetch_usage,fetch_opportunities, fetch_contacts

@shared_task
def make_api_call():
    fetch_and_store_google_campaigns()
    # scheduled_appointment_sync()
    fetch_opportunities()
    appoinment_fetch_usage()
    fetch_campaigns_facebook()
    fetch_calls_for_last_days()
    fetch_contacts()
    return
    


@shared_task
def make_api_for_ghl():
    
    credentials = GHLAuthCredentials.objects.first()
    
    print("credentials tokenL", credentials)
    refresh_token = credentials.refresh_token

    
    response = requests.post('https://services.leadconnectorhq.com/oauth/token', data={
        'grant_type': 'refresh_token',
        'client_id': config("GHL_CLIENT_ID"),
        'client_secret': config("GHL_CLIENT_SECRET"),
        'refresh_token': refresh_token
    })
    
    new_tokens = response.json()
    print("newtoken :", new_tokens)

    obj, created = GHLAuthCredentials.objects.update_or_create(
            location_id= new_tokens.get("locationId"),
            defaults={
                "access_token": new_tokens.get("access_token"),
                "refresh_token": new_tokens.get("refresh_token"),
                "expires_in": new_tokens.get("expires_in"),
                "scope": new_tokens.get("scope"),
                "user_type": new_tokens.get("userType"),
                "company_id": new_tokens.get("companyId"),
                "user_id":new_tokens.get("userId"),

            }
        )
