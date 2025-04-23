# your_app_name/tasks.py
import requests
from celery import shared_task
from accounts.models import GHLAuthCredentials, Contact, UserAppointment, Opportunity, CallReport
from accounts.services import get_ghl_contact, get_ghl_appointment, get_ghl_opportunity,fetch_calendar_data
from decouple import config
from accounts.helpers import create_or_update_contact, update_opportunity, create_opportunity
from accounts.utils import fetch_and_store_google_campaigns,fetch_campaigns_facebook, fetch_calls_for_last_days,appoinment_fetch_usage,fetch_opportunities, fetch_contacts

@shared_task
def make_api_call():
    fetch_and_store_google_campaigns()
    fetch_opportunities()
    appoinment_fetch_usage()
    # fetch_campaigns_facebook()
    fetch_calls_for_last_days()
    # fetch_contacts()
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



@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    autoretry_for=(Exception,),
    retry_backoff=True,
)
def handle_webhook_event(self,data, event_type):
    access_token = GHLAuthCredentials.objects.first().access_token
    if event_type in ["ContactCreate", "ContactUpdate"]:
        contact_data = get_ghl_contact(data.get("id"), access_token)
        contact = contact_data.get("contact")
        if contact:
            create_or_update_contact(contact)
        
    if event_type == "ContactDelete":
        contact = Contact.objects.filter(contact_id=data.get("id")).first()
        if contact:
            contact_id = contact.contact_id

            Opportunity.objects.filter(contact_id=contact_id).delete()
            CallReport.objects.filter(contact_id=contact_id).delete()
            UserAppointment.objects.filter(contact_id=contact_id).delete()
            contact.delete()

            print("Contact deleted successfully")
        else:
            print("Contact not found")

    
    if event_type in ["AppointmentCreate", "AppointmentUpdate"]:
        appointment = data.get("appointment")
            
        UserAppointment.objects.update_or_create(
            appointment_id=appointment.get("id"),
            defaults={
                "contact_name": appointment.get("title"),
                "appointment_status": appointment.get("appointmentStatus"),
                "title": appointment.get("title"),
                "start_time": appointment.get("startTime"),
                "date_added": appointment.get("dateAdded"),
                "assigned_to": appointment.get("assignedUserId"),
                "contact_id": appointment.get("contactId"),
                "source": appointment.get("source"),
                "sort": appointment.get("users", []),
                "created_by": data.get("appId"),
                "mode": appointment.get("groupId"),
                "calendar_name": fetch_calendar_data(appointment.get("calendarId"))
            }
        )
        print("appointment is created or updated")

    if event_type == "AppointmentDelete":

        appointment_id = data.get("appointment", {}).get("id")
        if appointment_id:
            UserAppointment.objects.filter(contact_id=appointment_id).delete()
            print("Appointment is deleted")
        else:
            print("Appointment ID missing in data")


    if event_type in ["OpportunityCreate"]:
        opportunity_data = get_ghl_opportunity(data.get("id"), access_token)
        opportunity = opportunity_data.get("opportunity")
        if opportunity:
            create_opportunity(opportunity)

    if event_type == "OpportunityUpdate":
        opportunity_data = get_ghl_opportunity(data.get("id"), access_token)
        opportunity = opportunity_data.get("opportunity")
        if opportunity:
            update_opportunity(opportunity)


    if event_type == "OpportunityDelete":
        
        opportunity_id = data.get("opportunity", {}).get("id")
        if opportunity_id:
            opportunity = Opportunity.objects.filter(opportunity_id=opportunity_id).first()
            if opportunity:
                opportunity.delete()
                print("Opportunity is deleted")
            else:
                print("Opportunity not found")
        else:
            print("Opportunity ID missing in data")



    
