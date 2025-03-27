import requests
from decouple import config
from accounts.serializers import FirebaseTokenSerializer, LeadConnectorAuthSerializer, IdentityToolkitAuthSerializer
from accounts.models import FirebaseToken, LeadConnectorAuth, IdentityToolkitAuth, CallReport, FacebookCampaign, Appointment, GoogleCampaignTotal, GHLAuthCredentials, Opportunity


def token_generation_step1():

    print("token generation step 1 triggered")
    url = "https://securetoken.googleapis.com/v1/token?key=AIzaSyB_w3vXmsI7WeQtrIOkjR6xTRVN5uOieiE"
    id_token = IdentityToolkitAuth.objects.first()

    headers = {
        "authority": "securetoken.googleapis.com",
        "accept": "*/*",
        "accept-language": "en-GB,en-US;q=0.9,en;q=0.8",
        "access-control-request-headers": "x-client-version,x-firebase-client,x-firebase-gmpid",
        "access-control-request-method": "POST",
        "origin": "https://app.gohighlevel.com",
        "referer": "https://app.gohighlevel.com/",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "cross-site",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    data = {
       "refresh_token": getattr(id_token, "refresh_token", config("TOKEN")),
        "grant_type": "refresh_token"
    }

    response = requests.post(url, headers=headers, data=data)
    if response.status_code == 200:
        response_data = response.json()
        user_id = response_data.get("user_id")
        project_id = response_data.get("project_id")

        token_instance = FirebaseToken.objects.filter(user_id=user_id, project_id=project_id).first()
        print("token instance: ", token_instance)
        if token_instance:
            serializer = FirebaseTokenSerializer(token_instance, data=response_data, partial=True)
        else:
            serializer = FirebaseTokenSerializer(data=response_data)

        if serializer.is_valid():
            serializer.save()
            print("Data saved/updated successfully!")
            return fetch_and_store_leadconnector_token()
        else:
            print("Validation errors:", serializer.errors)
    else:
        print("API call failed")






def fetch_and_store_leadconnector_token():

    firebase_token =  FirebaseToken.objects.first()
    url = "https://services.leadconnectorhq.com/oauth/2/login/signin/refresh?version=2&location_id=FQyDM99cDn25E5lBGbOm"

    headers = {
        "authority": "services.leadconnectorhq.com",
        "accept": "application/json, text/plain, */*",
        "accept-language": "en-IN,en-US;q=0.9,en;q=0.8,ml;q=0.7",
        "authorization": f"Bearer {firebase_token.access_token}",
        "baggage": "sentry-environment=production,sentry-release=51f978e816451676419adc7a1f15a689366afae4,sentry-public_key=c67431ff70d6440fb529c2705792425f,sentry-trace_id=4bbe54b1784442168fd300b0dec887e0",
        "channel": "APP",
        "content-type": "application/json;charset=UTF-8",
        "origin": "https://app.franchiseexpert.com",
        "referer": "https://app.franchiseexpert.com/",
        "sec-ch-ua": '"Google Chrome";v="119", "Chromium";v="119", "Not?A_Brand";v="24"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Linux"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "cross-site",
        "sentry-trace": "4bbe54b1784442168fd300b0dec887e0-94e9b3f71325b51e",
        "source": "WEB_USER",
        "token-id": firebase_token.access_token,
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "version": "2021-07-28",
    }

    response = requests.post(url, headers=headers, json={})

    if response.status_code == 200:
        response_data = response.json()
        response_data["trace_id"] = response_data.pop("traceId", None)

        print("responseData: ", response_data)
        LeadConnectorAuth.objects.all().delete()

        serializer = LeadConnectorAuthSerializer(data=response_data)

        if serializer.is_valid():
            serializer.save()
            print("Data saved/updated successfully!")
            return fetch_and_store_final_token()
        else:
            print("Validation errors:", serializer.errors)
    elif response.status_code == 401:
        token_generation_step1()
    else:
        print(f"API call failed with status code {response.status_code}")



def fetch_and_store_final_token():

    lead_connector_token = LeadConnectorAuth.objects.first()

    url = "https://identitytoolkit.googleapis.com/v1/accounts:signInWithCustomToken?key=AIzaSyB_w3vXmsI7WeQtrIOkjR6xTRVN5uOieiE"

    # Headers
    headers = {
        "authority": "identitytoolkit.googleapis.com",
        "accept": "*/*",
        "accept-language": "en-GB,en-US;q=0.9,en;q=0.8",
        "content-type": "application/json",
        "origin": "https://app.gohighlevel.com",
        "sec-ch-ua": '"Wavebox";v="119", "Chromium";v="119", "Not?A_Brand";v="24"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"macOS"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "cross-site",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "x-client-data": "CMeCywE=",
        "x-client-version": "Chrome/JsCore/9.15.0/FirebaseCore-web",
        "x-firebase-gmpid": "1:439472444885:android:c48022009a58ffc7",
    }

    data = {
        "token": lead_connector_token.token,
        "returnSecureToken": True
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        response_data = response.json()

        serializer_data = {
            "kind": response_data.get("kind"),
            "id_token": response_data.get("idToken"),
            "refresh_token": response_data.get("refreshToken"),
            "expires_in": int(response_data.get("expiresIn", 0)),
            "is_new_user": response_data.get("isNewUser", False),
        }

        IdentityToolkitAuth.objects.all().delete()

        serializer = IdentityToolkitAuthSerializer(data=serializer_data)
        if serializer.is_valid():
            serializer.save()
            print("✅ Data saved successfully!")
            return True
        else:
            print("❌ Serializer errors:", serializer.errors)
    elif response.status_code == 401:
        token_generation_step1()
            
    else:
        print(f"❌ API request failed with status code {response.status_code}: {response.text}")





import pytz
import datetime
from django.utils.dateparse import parse_datetime


def fetch_calls_for_last_days(retry_count=0):
    """
    Fetch call reports for today and yesterday (or tomorrow if required) dynamically.
    If data exists in the database, update it instead of inserting duplicates.
    """

    MAX_RETRIES = 1
    # Get authentication token
    token = IdentityToolkitAuth.objects.first()
    if not token:
        print("Error: No valid authentication token found.")
        token_generation_step1()
        fetch_calls_for_last_days()
        return

    # Get today's date in UTC

    utc_now = datetime.datetime.utcnow().replace(tzinfo=pytz.UTC)

    # Fetch data for today and yesterday only
    for i in range(0,2):
        start_date = (utc_now - datetime.timedelta(days=i + 1)).isoformat()
        end_date = (utc_now - datetime.timedelta(days=i)).isoformat()

        payload = {
            "callStatus": [],
            "campaign": [],
            "deviceType": [],
            "direction": None,
            "duration": None,
            "endDate": end_date,
            "firstTime": False,
            "keyword": [],
            "landingPage": [],
            "limit": 50,
            "locationId": "Xtj525Qgufukym5vtwbZ",
            "qualifiedLead": False,
            "referrer": [],
            "selectedPool": "all",
            "skip": 0,
            "source": [],
            "sourceType": [],
            "startDate": start_date,
            "userId": ""
        }

        print("start date : -----------------", start_date)
        print("end date : -----------------", end_date)

        headers = {
            "Token-id": f"{token.id_token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Source": "WEB_USER",
            "Channel": "APP",
            "Version": "2021-04-15"
        }

        all_calls = []
        BASE_URL = "https://backend.leadconnectorhq.com/reporting/calls/get-all-phone-calls-new"

        while True:
            response = requests.post(BASE_URL, json=payload, headers=headers)

            if response.status_code != 201:
                print(f"Error: {response.status_code}, {response.text}")
                break
                
            elif response.status_code == 401:
                if retry_count < MAX_RETRIES:
                        print(f"401 Unauthorized. Retrying... (Attempt {retry_count + 1})")
                        if token_generation_step1():
                            fetch_calls_for_last_days(retry_count + 1)
                            return

            data = response.json()
            print("data: ", response.json())
            calls = data.get("rows", [])

            if not calls:
                break

            all_calls.extend(calls)
            payload["skip"] += payload["limit"]

        update_or_store_calls(all_calls)


def update_or_store_calls(calls):

    if not calls:
        return

    call_objects = []

    for call in calls:
        
        call_objects.append(CallReport(
            id=call.get("id"),
            account_sid=call.get("accountSid"),
            assigned_to=call.get("assignedTo"),
            call_sid=call.get("callSid"),
            call_status=call.get("callStatus"),
            called=call.get("called"),
            called_city=call.get("calledCity"),
            called_country=call.get("calledCountry"),
            called_state=call.get("calledState"),
            called_zip=call.get("calledZip"),
            caller=call.get("caller"),
            caller_city=call.get("callerCity"),
            caller_country=call.get("callerCountry"),
            caller_state=call.get("callerState"),
            caller_zip=call.get("callerZip"),
            contact_id=call.get("contactId"),
            date_added=parse_datetime(call.get("dateAdded")) if call.get("dateAdded") else None,
            date_updated=parse_datetime(call.get("dateUpdated")) if call.get("dateUpdated") else None,
            deleted=call.get("deleted", False),
            direction=call.get("direction"),
            from_number=call.get("from"),
            from_city=call.get("fromCity"),
            from_country=call.get("fromCountry"),
            from_state=call.get("fromState"),
            from_zip=call.get("fromZip"),
            location_id=call.get("locationId"),
            message_id=call.get("messageId"),
            to_number=call.get("to"),
            to_city=call.get("toCity"),
            to_country=call.get("toCountry"),
            to_state=call.get("toState"),
            to_zip=call.get("toZip"),
            user_id=call.get("userId"),
            updated_at=parse_datetime(call.get("updatedAt")) if call.get("updatedAt") else None,
            duration=call.get("duration", 0),
            first_time=call.get("firstTime", False),
            recording_url=call.get("recordingUrl")
        ))


    CallReport.objects.bulk_create(call_objects, ignore_conflicts=True)
    print(f"Stored {len(call_objects)} call records in the database.")









def fetch_campaigns_facebook():


    url = "https://python-backend-dot-highlevel-backend.appspot.com/1.1/reporting/f/Xtj525Qgufukym5vtwbZ/campaigns"
    
    headers = {
        "accept": "application/json, text/plain, */*",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "en-GB,en-US;q=0.9,en;q=0.8",
        "authorization": "Bearer 59b0a2e7-bea0-4880-9bb0-c1aaffc67600",
        "origin": "https://app.gohighlevel.com",
        "referer": "https://app.gohighlevel.com/",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36"
    }

    today = datetime.date.today()

    for i in range(2):
        start_date = today - datetime.timedelta(days=i + 1)
        end_date = today - datetime.timedelta(days=i)

        params = {
            "start": start_date.strftime("%Y-%m-%d"),
            "end": end_date.strftime("%Y-%m-%d"),
            "sample": "true"
        }

        response = requests.get(url, headers=headers, params=params)

        if response.status_code == 200:
            data = response.json()

            # Store campaigns in the database
            for campaign_data in data.get("campaigns", []):
                campaign, created = FacebookCampaign.objects.update_or_create(
                    campaign_id=campaign_data["campaign_id"],
                    defaults={
                        "account_currency": campaign_data.get("account_currency"),
                        "campaign_name": campaign_data.get("campaign_name"),
                        "impressions": int(campaign_data.get("impressions", 0)),
                        "clicks": campaign_data.get("clicks", 0),
                        "cpc": campaign_data.get("cpc", 0.0),
                        "ctr": campaign_data.get("ctr", 0.0),
                        "spend": campaign_data.get("spend", 0.0),
                        "date_start": campaign_data.get("date_start"),
                        "date_stop": campaign_data.get("date_stop"),
                        "account_id": campaign_data.get("account_id"),
                        "conversions": campaign_data.get("conversions", 0),
                        "cost_per_conversion": campaign_data.get("costPerConversion", 0.0),
                    }
                )
                print("facebook campaigns data created successfully")



            
        else:
            print(f"Failed to fetch data for {start_date}: {response.status_code} - {response.text}")





def fetch_and_store_google_campaigns():
    url = "https://python-backend-dot-highlevel-backend.appspot.com/1.1/reporting/g/Xtj525Qgufukym5vtwbZ/campaigns"
    headers = {
        "Authorization": "Bearer 59b0a2e7-bea0-4880-9bb0-c1aaffc67600",
        "Accept": "application/json",
    }
    import datetime
    today = datetime.date.today()
    yesterday = today - datetime.timedelta(days=1)

    for current_date in [yesterday, today]:
        params = {"start": current_date, "end": current_date, "sample": "false"}
        response = requests.get(url, headers=headers, params=params)

        if response.status_code == 200:
            data = response.json().get("total", {})
            if not data:
                print(f"No campaign data found for {current_date}")
                continue

            # Check if data for yesterday already exists
            
            obj, created = GoogleCampaignTotal.objects.update_or_create(
                date=current_date,
                defaults={
                    "all_conversions": data.get('allConversions', 0),
                    "avg_cpc": data.get('avgCpc', 0),
                    "clicks": data.get('clicks', 0),
                    "conversion_rate": data.get('conversionRate', 0),
                    "conversions": data.get('conversions', 0),
                    "cost": data.get('cost', 0),
                    "cost_per_conversion": data.get('costPerConversion', 0),
                    "impressions": data.get('impressions', 0),
                    "interactions": data.get('interactions', 0),
                    "view_through_conversions": data.get('viewThroughConversions', 0),
                }
            )
            print("obj:", obj)
            print("created: ", created)
            print("Google Campaign Data Stored Successfully for", current_date)
        else:
            print(f"Error: {response.status_code} - {response.text}")

    print("Last days data fetched & stored successfully!")
    return 




import requests
from datetime import datetime, timedelta
import pytz

def fetch_ghl_appointments(
    access_token, 
    location_id, 
    start_date, 
    end_date, 
    page=1, 
    limit=50, 
    timezone_str='America/Edmonton'
):
    """
    Fetch appointments from GoHighLevel for a specific date range.
    """
    # Set timezone
    timezone = pytz.timezone(timezone_str)
    
    # Convert dates to milliseconds for GHL API
    start_ms = int(start_date.timestamp() * 1000)
    end_ms = int(end_date.timestamp() * 1000)

    print("start ms :",start_ms)
    print("end ms: ", end_ms)

    columns = [
        {"title": "Name of contact", "key": "contactName", "isSelected": True, "isSortable": False, "isArray": False},
        {"title": "Status", "key": "appointmentStatus", "isSelected": True, "isSortable": False, "isArray": False},
        {"title": "Title", "key": "title", "isSelected": True, "isSortable": False, "isArray": False},
        {"title": "Requested Time", "key": "startTime", "isSelected": True, "isSortable": True, "isArray": False},
        {"title": "Created On", "key": "dateAdded", "isSelected": True, "isSortable": True, "isArray": False},
        {"title": "Calendar Name", "key": "calendarName", "isSelected": True, "isSortable": False, "isArray": False},
        {"title": "Appointment Owner", "key": "assignedTo", "isSelected": True, "isSortable": False, "isArray": False},
        {"title": "Mode", "key": "reportingSource", "isSelected": True, "isSortable": False, "isArray": False}
    ]
    
    # Prepare payload
    payload = {
            "chartType": "table",
            "options": {
                "aggregations": {
                    "count": "id"
                },
                "filters": {
                    "operator": "and",
                    "fields": [
                        {
                            "field": "dateAdded",
                            "operator": "time_series",
                            "value": [start_ms, end_ms]
                        }
                    ]
                },
                "tableProperties": {
                    "columns": columns,
                    "order": "desc",
                    "orderBy": "dateAdded",
                    "limit": 50,
                    "page": 1
                },
                "timezone": "America/Edmonton"
            }
        }
    
    # Prepare headers
    headers = {
        "Token-id": f"{access_token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Source": "WEB_USER",
        "Channel": "APP",
        "Version": "2021-04-15"
    }
    
    # Make the API request
    try:
        response = requests.post(
            f'https://backend.leadconnectorhq.com/reporting/dashboards/automations/appointments?locationId={location_id}',
            json=payload,
            headers=headers
        )

        # print("response:", response.json())
        
        # Raise an exception for bad responses
        response.raise_for_status()
        
        # Return the response JSON
        return response.json()
    
    except requests.RequestException as e:
        print(f"Error fetching appointments: {e}")
        return None
    






# Utility to demonstrate usage (remove in actual implementation)
def appoinment_fetch_usage():
    token_generation_step1()
    token = IdentityToolkitAuth.objects.first()
    ACCESS_TOKEN = token.id_token
    LOCATION_ID = 'Xtj525Qgufukym5vtwbZ'
                            
    print('tokenL', ACCESS_TOKEN)
    # Fetch today's appointments
    today_appointments = get_last_days_appointments(ACCESS_TOKEN, LOCATION_ID)
    print("today appoinment:", today_appointments)

    
def get_last_days_appointments(access_token, location_id):
    """
    Fetch appointments for the last 365 days, day by day.
    """
    # timezone = pytz.timezone('America/Edmonton')
    all_appointments = []

    timezone = datetime.now().astimezone().tzinfo
    
    # Get yesterday's date
    yesterday = datetime.now(timezone).date() - timedelta(days=1)
    
    # Create start of yesterday (00:00:00)
    start_date = datetime.combine(yesterday, datetime.min.time()).replace(tzinfo=timezone)
    
    # Create end of yesterday (23:59:59)
    end_date = datetime.combine(yesterday, datetime.max.time()).replace(tzinfo=timezone)
    
    print(f"Fetching data for: {yesterday}")
    print(f"Start date: {start_date}")
    print(f"End date: {end_date}")
    
    # Fetch appointments for yesterday
    daily_appointments = fetch_ghl_appointments(access_token, location_id, start_date, end_date)
    # print("Daily appointments: ", daily_appointments)
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%b %d %Y")

    # Filter data based on yesterday's dateAdded
    filtered_data = [entry for entry in daily_appointments["data"] if entry["dateAdded"].startswith(yesterday)]
    print("filtered data", filtered_data)
    if daily_appointments:
        save_appointments_to_db(filtered_data)
        return daily_appointments.get("data", [])

    return []

from django.db import transaction
from accounts.models import UserAppointment
def save_appointments_to_db(appointments):
    """
    Save all fetched appointments to the database without updating existing ones.
    """
    if not appointments:
        print("No appointments to save.")
        return

    new_appointments = []

    for appointment in appointments:
        new_appointments.append(
            UserAppointment(
                appointment_id = appointment.get("id"),
                contact_name=appointment.get("contactName"),
                appointment_status=appointment.get("appointmentStatus"),
                title=appointment.get("title"),
                start_time=appointment.get("startTime"),
                date_added=appointment.get("dateAdded"),
                calendar_name=appointment.get("calendarName"),
                assigned_to=appointment.get("assignedTo"),
                contact_id=appointment.get("contactId"),
                sort=appointment.get("sort"),
                source=appointment.get("source"),
                created_by=appointment.get("createdBy"),
                mode=appointment.get("mode"),
                phone=appointment.get("phone"),
                email=appointment.get("email"),
                appointment_owner=appointment.get("appointmentOwner"),
            )
        )

    with transaction.atomic():  # Ensures all records are inserted together
        UserAppointment.objects.bulk_create(new_appointments)

    print(f"Inserted {len(new_appointments)} new appointments into the database.")



def fetch_opportunities():
    # Calculate yesterday's date in the format MM-DD-YYYY
    token = GHLAuthCredentials.objects.first()
    yesterday = (datetime.utcnow() - timedelta(days=1)).strftime("%m-%d-%Y")

    url = f"https://services.leadconnectorhq.com/opportunities/search?location_id=Xtj525Qgufukym5vtwbZ&date={yesterday}"

    # Authorization Token (Ensure it's valid)
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {token.access_token}",
        "Version": "2021-07-28"
    }

    print("date: ", yesterday)
    # Make the GET request
    response = requests.get(url, headers=headers)

    # Check response status
    if response.status_code == 200:
        data = response.json()
        opportunities = data.get("opportunities", [])
        print("len(; ):", len(opportunities))

        for opp in opportunities:
            opportunity_id = opp.get("id")
            created_at = opp.get("createdAt")
            updated_at = opp.get("updatedAt")
            
            # Convert timestamps to datetime format
            date_created = datetime.strptime(created_at, "%Y-%m-%dT%H:%M:%S.%fZ") if created_at else None
            updated_on = datetime.strptime(updated_at, "%Y-%m-%dT%H:%M:%S.%fZ") if updated_at else None
            
            # Extract related contact details
            contact = opp.get("contact", {})

            # Extract fields
            defaults = {
                "contact_id": opp.get("contactId"),
                "date_created": date_created,
                "email": contact.get("email"),
                "full_name": contact.get("name"),
                "opportunity_name": opp.get("name"),
                "phone": contact.get("phone"),
                "pipeline_name": None,
                "pipeline_stage": opp.get("pipelineStageId"),
                "lead_value": opp.get("monetaryValue"),
                "source": opp.get("source"),
                "assigned": opp.get("assignedTo"),
                "updated_on": updated_on,
                "lost_reason_id": opp.get("lostReasonId"),
                "followers": str(opp.get("followers", [])),
                "tags": str(contact.get("tags", [])),
                "engagement_score": 0,  # Engagement score not in JSON, adjust if available
                "status": opp.get("status"),
                "sq_ft": None,  # Not available in JSON
                "pipeline_stage_id": opp.get("pipelineStageId"),
                "pipeline_id": opp.get("pipelineId"),
                "days_since_last_stage_change": None,
                "days_since_last_status_change": None,  # Not available in JSON
                "days_since_last_updated": None  # Not available in JSON
            }

            obj, created = Opportunity.objects.update_or_create(
                opportunity_id=opportunity_id,
                defaults=defaults
            )

            if created:
                print(f"Created new opportunity: {opportunity_id}")
            else:
                print(f"Updated existing opportunity: {opportunity_id}")

        #     return response.json()
    else:
        return {"error": f"Failed to fetch data: {response.status_code}, {response.text}"}

# Example usage:
# opportunities = fetch_opportunities()
# print(opportunities)