from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
from django.shortcuts import redirect
from accounts.models import Opportunity, Budget, GHLAuthCredentials, UserAppointment, GHLAuthCredentials
from decouple import config
import requests
from accounts.services import get_ghl_contact
from django.utils.dateparse import parse_datetime
from accounts.tasks import handle_webhook_event


@csrf_exempt
def webhook_handler_for_opportunity(request):
    if request.method != "POST":
        return JsonResponse({"message": "Method not allowed"}, status=405)

    try:
        data = json.loads(request.body)
        print("date:----- ", data)
        event_type = data.get("type")
        handle_webhook_event.delay(data, event_type)
        return JsonResponse({"message":"Webhook received"}, status=200)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)




@csrf_exempt
def budget_webhook_handler(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)            
            budget, created = Budget.objects.update_or_create(
                budget_date=data.get("Budget Date"),
                defaults={
                    "budgeted_sq_ft": data.get("Budgeted Sq. Ft.", None),
                    "budgeted_revenue": data.get("Budgeted Revenue", None),
                    "location_name": data.get("location", {}).get("name", None),
                    "location_id": data.get("location", {}).get("id", None),
                }
            )
            
            message = "Budget updated successfully" if not created else "Budget created successfully"
            return JsonResponse({"message": message, "budget_id": budget.id}, status=201)
        
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON data"}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    
    return JsonResponse({"error": "Invalid request method"}, status=405)

import pandas as pd
from accounts.models import Contact
from django.utils.dateparse import parse_datetime


def import_contacts_from_excel(file_path):
    df = pd.read_excel(file_path, engine='openpyxl')
    for _, row in df.iterrows():
        Contact.objects.update_or_create(
            contact_id=row['Contact Id'],
            defaults={
                'first_name': row['First Name'] if row['First Name'] else None,
                'last_name': row['Last Name'] if row['Last Name'] else None,
                'business_name': row['Business Name'] if row['Business Name'] else None,
                'company_name': row['Company Name'] if row['Company Name'] else None,
                'phone': str(int(row['Phone'])) if str(row['Phone']).isdigit() else None,
                'email': row['Email'] if row['Email'] else None,
                'created': parse_datetime(str(row['Created'])) if row['Created'] else None,
                'tags': row['Tags'] if row['Tags'] else None,
                'utm_source': row['utm_source'] if row['utm_source'] else None,
                'utm_medium': row['utm_medium'] if row['utm_medium'] else None,
                'utm_campaign': row['utm_campaign'] if row['utm_campaign'] else None,
                'utm_content': row['utm_content'] if row['utm_content'] else None,
                'utm_term': row['utm_term'] if row['utm_term'] else None,
                'utm_traffic_type': row['utm_traffic_type'] if row['utm_traffic_type'] else None,
            }
        )


    




    print("Contacts imported successfully!")

def import_opportunities_from_excel(file_path):
    df = pd.read_excel(file_path, engine='openpyxl')

    for _, row in df.iterrows():
        Opportunity.objects.update_or_create(
            
            opportunity_id=row.get('Opportunity ID', ''),
            defaults={
                'date_created': parse_datetime(row['date_created']) if pd.notna(row['date_created']) else None,
                'email': row.get('email', ''),
                'full_name': row.get('full_name', ''),
                'opportunity_name': row.get('opportunity_name', ''),
                'phone': row.get('phone', ''),
                'pipeline_name': row.get('pipeline_name', ''),
                'pipeline_stage': row.get('pipeline_stage', ''),
                'lead_value': int(row['Lead Value']) if pd.notna(row['Lead Value']) else None,
                'source': row.get('source', ''),
                'assigned': row.get('assigned', ''),
                'updated_on': parse_datetime(row['Updated on']) if pd.notna(row['Updated on']) else None,
                'lost_reason_id': row.get('lost reason ID', ''),
                'lost_reason_name': row.get('lost reason name', ''),
                'followers': row.get('Followers', ''),
                'notes': row.get('Notes', ''),
                'tags': row.get('tags', ''),
                'engagement_score': int(row['Engagement Score']) if pd.notna(row['Engagement Score']) else None,
                'status': row.get('status', ''),
                'sq_ft': row.get('Sq. Ft.', ''),
                'contact_id':row.get('contact_id', ''),
                'pipeline_stage_id': row.get('Pipeline Stage ID', ''),
                'pipeline_id': row.get('Pipeline ID', ''),
                'days_since_last_stage_change': row.get('Days Since Last Stage Change Date', ''),
                'days_since_last_status_change': row.get('Days Since Last Status Change Date', ''),
                'days_since_last_updated': row.get('Days Since Last Updated', ''),
            }
        )

    print("Opportunities imported successfully!")


GHL_CLIENT_ID = config("GHL_CLIENT_ID")
GHL_CLIENT_SECRET = config("GHL_CLIENT_SECRET")
GHL_REDIRECTED_URI = config("GHL_REDIRECTED_URI")
TOKEN_URL = "https://services.leadconnectorhq.com/oauth/token"
SCOPE = "contacts.readonly%20contacts.write%20calendars/events.readonly%20calendars/groups.readonly%20calendars/resources.readonly%20calendars/resources.write%20calendars.readonly%20calendars.write%20opportunities.readonly%20opportunities.write%20calendars/groups.write%20calendars/events.write"

def auth_connect(request):
    auth_url = ("https://marketplace.leadconnectorhq.com/oauth/chooselocation?response_type=code&"
                f"redirect_uri={GHL_REDIRECTED_URI}&"
                f"client_id={GHL_CLIENT_ID}&"
                f"scope={SCOPE}"
                )
    return redirect(auth_url)



def callback(request):
    
    code = request.GET.get('code')

    if not code:
        return JsonResponse({"error": "Authorization code not received from OAuth"}, status=400)

    return redirect(f'http://localhost:8000/accounts/auth/tokens?code={code}')


def tokens(request):
    authorization_code = request.GET.get("code")

    if not authorization_code:
        return JsonResponse({"error": "Authorization code not found"}, status=400)

    data = {
        "grant_type": "authorization_code",
        "client_id": GHL_CLIENT_ID,
        "client_secret": GHL_CLIENT_SECRET,
        "redirect_uri": 'http://localhost:8000/accounts/oauth/callback/',
        "code": authorization_code,
    }

    response = requests.post(TOKEN_URL, data=data)

    try:
        response_data = response.json()
        if not response_data:
            return

        obj, created = GHLAuthCredentials.objects.update_or_create(
            location_id= response_data.get("locationId"),
            defaults={
                "access_token": response_data.get("access_token"),
                "refresh_token": response_data.get("refresh_token"),
                "expires_in": response_data.get("expires_in"),
                "scope": response_data.get("scope"),
                "user_type": response_data.get("userType"),
                "company_id": response_data.get("companyId"),
                "user_id":response_data.get("userId"),

            }
        )
        return JsonResponse({
            "message": "Authentication successful",
            "access_token": response_data.get('access_token'),
            "token_stored": True
        })
        
    except requests.exceptions.JSONDecodeError:
        return JsonResponse({
            "error": "Invalid JSON response from API",
            "status_code": response.status_code,
            "response_text": response.text[:500]
        }, status=500)