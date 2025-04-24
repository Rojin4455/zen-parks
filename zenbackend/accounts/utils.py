import requests
from decouple import config
from accounts.serializers import FirebaseTokenSerializer, LeadConnectorAuthSerializer, IdentityToolkitAuthSerializer
from accounts.models import FirebaseToken, LeadConnectorAuth, IdentityToolkitAuth, CallReport, FacebookCampaign, Appointment, GoogleCampaignTotal, GHLAuthCredentials, Opportunity, Contact
from accounts.helpers import get_pipeline_stages, create_or_update_contact

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
    print("Error: No valid authentication token found.")
    token_generation_step1()
    token = IdentityToolkitAuth.objects.first()

    from datetime import datetime, timedelta

    def generate_date_range(days_ago_start=30, days_ago_end=0):
        # Get today's date
        today = datetime.now()
        
        # Calculate end date (days_ago_end at 18:29:59.999)
        end_date = (today - timedelta(days=days_ago_end)).replace(hour=18, minute=29, second=59, microsecond=999000)
        
        # Calculate start date (days_ago_start at 18:30:00.000)
        start_date = (today - timedelta(days=days_ago_start)).replace(hour=18, minute=30, second=0, microsecond=0)
        
        # Format dates as required
        formatted_end_date = end_date.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
        formatted_start_date = start_date.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
        
        return formatted_start_date, formatted_end_date
    
    for i in range(3):  # Adjust range as needed (2 for today and yesterday)
        # Both start and end dates shift back by i days each iteration
        days_back_end = i
        days_back_start = i + 2  # Start date is always 2 days before end date
        
        start_date, end_date = generate_date_range(days_back_start, days_back_end)
        
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

        print(f"Fetching data for period {i+1}:")
        print(f"Start Date: {start_date}")
        print(f"End Date: {end_date}")

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

    existing_call_ids = set(CallReport.objects.filter(id__in=[call.get("id") for call in calls]).values_list("id", flat=True))

    new_call_objects = []
    update_call_objects = []

    for call in calls:
        call_obj = CallReport(
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
            recording_url=call.get("recordingUrl"),
        )

        if call.get("id") in existing_call_ids:
            update_call_objects.append(call_obj)  # Update existing calls
        else:
            new_call_objects.append(call_obj)  # Insert new calls

        # Perform bulk operations
    with transaction.atomic():
        if new_call_objects:
            CallReport.objects.bulk_create(new_call_objects, ignore_conflicts=True)
            print(f"Inserted {len(new_call_objects)} new call records.")

        if update_call_objects:
            CallReport.objects.bulk_update(update_call_objects, [
                "account_sid", "assigned_to", "call_sid", "call_status", "called", "called_city",
                "called_country", "called_state", "called_zip", "caller", "caller_city",
                "caller_country", "caller_state", "caller_zip", "contact_id", "date_added",
                "date_updated", "deleted", "direction", "from_number", "from_city", "from_country",
                "from_state", "from_zip", "location_id", "message_id", "to_number", "to_city",
                "to_country", "to_state", "to_zip", "user_id", "updated_at", "duration",
                "first_time", "recording_url"
            ])
            print(f"Updated {len(update_call_objects)} existing call records.")





def generate_date_range(days_ago_start=2, days_ago_end=0):
    import datetime

    # Get today's date
    today = datetime.datetime.now()
    
    # Calculate end date (days_ago_end at 18:29:59.999)
    end_date = (today - datetime.timedelta(days=days_ago_end)).replace(hour=18, minute=29, second=59, microsecond=999000)
    
    # Calculate start date (days_ago_start at 18:30:00.000)
    start_date = (today - datetime.timedelta(days=days_ago_start)).replace(hour=18, minute=30, second=0, microsecond=0)
    
    # Format dates as required
    formatted_end_date = end_date.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
    formatted_start_date = start_date.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
    
    return formatted_start_date, formatted_end_date

def run():
    # Number of iterations/days to go back
    days_to_check = 4
    
    for i in range(days_to_check):
        # Both start and end dates shift back by i days each iteration
        days_back_end = i
        days_back_start = i + 2  # Start date is always 2 days before end date
        
        start_date, end_date = generate_date_range(days_back_start, days_back_end)
        
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
        
        print(f"Iteration {i+1}:")
        print(f"Start Date: {start_date}")
        print(f"End Date: {end_date}")
        # Your API call here with the payload



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
    import datetime

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
    print(f"Today12: {today}, Yesterday12: {yesterday}")

    for i in range(2):
        today = datetime.date.today() - datetime.timedelta(days=i)
        yesterday = today - datetime.timedelta(days=1)
        print(f"Today: {today}, Yesterday: {yesterday}")

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



def get_timestamp_range(date_str):
    import pytz
    """
    Convert a date string like '2025-03-04' to start and end timestamps in ms
    matching the website's behavior (Mountain Time).
    """
    # Parse the date string
    # year, month, day = map(int, date_str.split('-'))
    date_obj = date_str.date()
    
    # Set up Mountain Time timezone
    mountain_tz = pytz.timezone('America/Edmonton')
    
    # Create start of day in Mountain Time
    start_date = mountain_tz.localize(datetime.combine(date_obj, datetime.min.time()))
    
    # Create end of day in Mountain Time
    end_date = mountain_tz.localize(datetime.combine(date_obj, datetime.max.time()))
    
    # Convert to milliseconds timestamp
    start_ms = int(start_date.timestamp() * 1000)
    end_ms = int(end_date.timestamp() * 1000)
    
    return start_ms, end_ms



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

    start_ms, end_ms = get_timestamp_range(start_date)
    print(f"For date {start_date}:")
    print(f"Start ms: {start_ms}")
    print(f"End ms: {end_ms}")

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
    print("date ddeede: ", start_date)
    print("value ms: ", start_ms, end_ms)
    
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
    today_appointments = get_appointments_date_range2(ACCESS_TOKEN, LOCATION_ID)
    print("today appoinment:", today_appointments)

    
# def get_last_days_appointments(access_token, location_id):
#     """
#     Fetch appointments for the last 365 days, day by day.
#     """
#     # timezone = pytz.timezone('America/Edmonton')
#     all_appointments = []

#     timezone = datetime.now().astimezone().tzinfo
    
#     # Get yesterday's date
#     yesterday = datetime.now(timezone).date() - timedelta(days=1)
    
#     # Create start of yesterday (00:00:00)
#     start_date = datetime.combine(yesterday, datetime.min.time()).replace(tzinfo=timezone)
    
#     # Create end of yesterday (23:59:59)
#     end_date = datetime.combine(yesterday, datetime.max.time()).replace(tzinfo=timezone)
    
#     print(f"Fetching data for: {yesterday}")
#     print(f"Start date: {start_date}")
#     print(f"End date: {end_date}")
    
#     # Fetch appointments for yesterday
#     daily_appointments = fetch_ghl_appointments(access_token, location_id, start_date, end_date)
#     # print("Daily appointments: ", daily_appointments)
#     yesterday = (datetime.now() - timedelta(days=1)).strftime("%b %d %Y")

#     # Filter data based on yesterday's dateAdded
#     filtered_data = [entry for entry in daily_appointments["data"] if entry["dateAdded"].startswith(yesterday)]
#     print("filtered data", filtered_data)
#     if daily_appointments:
#         save_appointments_to_db(filtered_data)
#         return daily_appointments.get("data", [])

#     return []

from django.db import transaction
from accounts.models import UserAppointment
def save_appointments_to_db(appointments):
    if not appointments:
        print("No appointments to save.")
        return

    appointment_ids = [appointment["id"] for appointment in appointments]
    
    # Fetch existing appointments in bulk
    existing_appointments = {ua.appointment_id: ua for ua in UserAppointment.objects.filter(appointment_id__in=appointment_ids)}

    new_appointments = []
    updated_appointments = []

    for appointment in appointments:
        obj = existing_appointments.get(appointment["id"])

        if obj:
            # Update existing appointment fields
            obj.contact_name = appointment.get("contactName")
            obj.appointment_status = appointment.get("appointmentStatus")
            obj.title = appointment.get("title")
            obj.start_time = appointment.get("startTime")
            obj.date_added = appointment.get("dateAdded")
            obj.calendar_name = appointment.get("calendarName")
            obj.assigned_to = appointment.get("assignedTo")
            obj.contact_id = appointment.get("contactId")
            obj.sort = appointment.get("sort")
            obj.source = appointment.get("source")
            obj.created_by = appointment.get("createdBy")
            obj.mode = appointment.get("mode")
            obj.phone = appointment.get("phone")
            obj.email = appointment.get("email")
            obj.appointment_owner = appointment.get("appointmentOwner")
            updated_appointments.append(obj)
        else:
            # Create new appointment object
            new_appointments.append(UserAppointment(
                appointment_id=appointment.get("id"),
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
            ))

    with transaction.atomic():
        # Bulk create new appointments
        if new_appointments:
            UserAppointment.objects.bulk_create(new_appointments, batch_size=1000)
        
        # Bulk update existing appointments
        if updated_appointments:
            UserAppointment.objects.bulk_update(updated_appointments, [
                "contact_name", "appointment_status", "title", "start_time", "date_added",
                "calendar_name", "assigned_to", "contact_id", "sort", "source",
                "created_by", "mode", "phone", "email", "appointment_owner"
            ], batch_size=1000)

    print(f"Inserted {len(new_appointments)} new appointments, updated {len(updated_appointments)} existing appointments.")


def fetch_opportunities(limit=100):
    from datetime import datetime, timedelta
    end_date = datetime.today().strftime("%m-%d-%Y")

    # Get the date 30 days ago
    start_date = (datetime.today() - timedelta(days=30)).strftime("%m-%d-%Y")
    print("start date: _ ", start_date)
    print("end date: ", end_date)
    location_id = "Xtj525Qgufukym5vtwbZ"
    token = GHLAuthCredentials.objects.first()

    if not token:
        print("Error: No authentication token found.")
        return None

    url = "https://services.leadconnectorhq.com/opportunities/search"
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {token.access_token}",
        "Version": "2021-07-28"
    }
    page = 1
    all_opportunities = []
    offset = 0  # Start from the first page

    while True:
        params = {
            "location_id": location_id,
            "status": "all",
            "order": "added_desc",
            "date": start_date,
            "endDate": end_date,
            "limit": limit,
            "page": page
        }

        response = requests.get(url, headers=headers, params=params)

        if response.status_code != 200:
            print(f"Error: {response.status_code} - {response.text}")
            break  # Stop the loop if there's an error

        data = response.json()
        opportunities = data.get("opportunities", [])

        if not opportunities:
            break  # Stop when no more opportunities are returned

        all_opportunities.extend(opportunities)
        page += 1

        print(f"Fetched {len(opportunities)} opportunities, total so far: {len(all_opportunities)}")

    print(f"Total opportunities fetched: {len(all_opportunities)}")
    create_or_update_opportunity(all_opportunities)
    return





def create_or_update_opportunity(opportunity_data):
    existing_opportunities = {
        opp.opportunity_id: opp for opp in Opportunity.objects.filter(
            opportunity_id__in=[data.get("id") for data in opportunity_data]
        )
    }

    new_opportunities = []
    updated_opportunities = []

    for data in opportunity_data:
        opportunity_id = data.get("id")
        opportunity = existing_opportunities.get(opportunity_id)
        source = data.get("source")
        source = source.get("source", "No Data") if isinstance(source, dict) else (source or "No Data")
        pipeline_stage_name = "Unknown Stage"

        for stage in get_pipeline_stages()["stages"]:
            if stage["id"] == data.get("pipelineStageId"):
                pipeline_stage_name = stage["name"]
                break

        opportunity_data_dict = {
            "opportunity_id": opportunity_id,
            "full_name": data.get("contact", {}).get("name", "No Data"),
            "lead_value": data.get("monetaryValue"),
            "pipeline_id": data.get("pipelineId"),
            "pipeline_stage_id": data.get("pipelineStageId", "No Data"),
            "assigned": data.get("assignedTo", "No Data"),
            "status": data.get("status"),
            "source": source,
            "days_since_last_status_change": data.get("lastStatusChangeAt"),
            "days_since_last_stage_change": data.get("lastStageChangeAt"),
            "date_created": parse_datetime(data.get("createdAt")),
            "updated_on": parse_datetime(data.get("updatedAt")),
            "contact_id": data.get("contactId"),
            "lost_reason_id": data.get("lostReasonId", "No Data"),
            "followers": ", ".join(data.get("followers", [])),
            "email": data.get("contact", {}).get("email", "No Data"),
            "phone": data.get("contact", {}).get("phone", "No Data"),
            "tags":", ".join(data.get("contact", {}).get("tags", [])),
            "pipeline_stage":pipeline_stage_name,
            "pipeline_name":"The Parks - Lead Stages"
        }

        if opportunity:
            # Update existing record
            for field, value in opportunity_data_dict.items():
                setattr(opportunity, field, value)
            updated_opportunities.append(opportunity)
        else:
            # Create new record
            new_opportunities.append(Opportunity(**opportunity_data_dict))

    # Bulk insert new records
    if new_opportunities:
        Opportunity.objects.bulk_create(new_opportunities)
        print(f"Created {len(new_opportunities)} new opportunities.")

    # Bulk update existing records
    if updated_opportunities:
        Opportunity.objects.bulk_update(
            updated_opportunities, 
            [
                "full_name", "lead_value", "pipeline_id", "pipeline_stage_id", "assigned", 
                "status", "source", "days_since_last_status_change", "days_since_last_stage_change", 
                "date_created", "updated_on", "contact_id", "lost_reason_id", "followers", 
                "email", "phone", "tags"
            ]
        )
        print(f"Updated {len(updated_opportunities)} existing opportunities.")




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
    

import pandas as pd
from accounts.models import Opportunity  # Update this with your actual app name
from django.utils.dateparse import parse_datetime

def import_and_create_oppor(file):


    # Load the Excel file
    file_path = file  # Change this to your actual file path
    df = pd.read_excel(file_path, engine="openpyxl")
    df = pd.read_excel(file_path, sheet_name="Accounts Opportunity", dtype=str)


    # Mapping column names from the sheet to Django model fields
    column_mapping = {
        "Opportunity Name": "opportunity_name",
        "Contact Name": "full_name",
        "phone": "phone",
        "email": "email",
        "pipeline": "pipeline_name",
        "stage": "pipeline_stage",
        "Lead Value": "lead_value",
        "source": "source",
        "assigned": "assigned",
        "Created on": "date_created",
        "Updated on": "updated_on",
        "lost reason ID": "lost_reason_id",
        "lost reason name": "lost_reason_name",
        "Followers": "followers",
        "Notes": "notes",
        "tags": "tags",
        "Engagement Score": "engagement_score",
        "status": "status",
        "Sq. Ft.": "sq_ft",
        "Opportunity ID": "opportunity_id",
        "Contact ID": "contact_id",
        "Pipeline Stage ID": "pipeline_stage_id",
        "Pipeline ID": "pipeline_id",
        "Days Since Last Stage Change Date": "days_since_last_stage_change",
        "Days Since Last Status Change Date": "days_since_last_status_change",
        "Days Since Last Updated": "days_since_last_updated",
    }

    # Rename DataFrame columns
    df = df.rename(columns=column_mapping)

    # Fill empty values with "No Data" except for numeric fields
    for col in df.columns:
        if df[col].dtype == object:  # Only apply to string fields
            df[col] = df[col].fillna("No Data")
        else:
            df[col] = df[col].fillna(0)  # Fill numeric fields with 0

    # Convert date fields
    date_fields = ["date_created", "updated_on"]
    for field in date_fields:
        df[field] = df[field].apply(lambda x: parse_datetime(str(x)) if pd.notnull(x) else None)

    # Iterate over DataFrame and update or create records
    print("kennnnn:",df)
    new_opportunities = []
    for _, row in df.iterrows():
        opportunity_id = row["opportunity_id"]
        if opportunity_id and opportunity_id != "No Data":  # Ensure ID is valid
            new_opportunities.append(Opportunity(**row.to_dict()))

            # obj, created = Opportunity.objects.update_or_create(
            #     opportunity_id=opportunity_id,  # Lookup field
            #     defaults=row.to_dict(),  # Update/Create with row data
            # )

    if new_opportunities:
        Opportunity.objects.bulk_create(new_opportunities)
        print(f"Inserted {len(new_opportunities)} new opportunities.")
    else:
        print("No new opportunities to insert.")

    print("Data import complete.")



def fetch_contacts(limit=100):
    location_id = "Xtj525Qgufukym5vtwbZ"
    token = GHLAuthCredentials.objects.first()

    if not token:
        print("Error: No authentication token found.")
        return

    url = f"https://services.leadconnectorhq.com/contacts/?locationId={location_id}&limit={limit}"
    
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {token.access_token}",
        "Version": "2021-07-28"
    }
    
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print(f"Error: {response.status_code} - {response.text}")
        return

    data = response.json()
    contacts_data = data.get("contacts", [])

    if not contacts_data:
        print("No contacts found.")
        return

    contacts_to_create = []
    existing_contacts = {c.contact_id: c for c in Contact.objects.filter(contact_id__in=[c["id"] for c in contacts_data])}

    for contact in contacts_data:
        create_or_update_contact(contact)
        # contact_id = contact.get("id")
        # if not contact_id:
        #     continue

        # Convert dateAdded to datetime
    #     date_added = contact.get("dateAdded")
    #     created = datetime.strptime(date_added, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=pytz.UTC) if date_added else None

    #     contact_obj = existing_contacts.get(contact_id)

    #     if contact_obj:
    #         # Update existing contact
    #         contact_obj.first_name = contact.get("firstName")
    #         contact_obj.last_name = contact.get("lastName")
    #         contact_obj.business_name = contact.get("companyName")
    #         contact_obj.company_name = contact.get("companyName")
    #         contact_obj.phone = contact.get("phone")
    #         contact_obj.email = contact.get("email")
    #         contact_obj.created = created
    #         contact_obj.tags = ",".join(contact.get("tags", []))  # Convert list to string
    #         contact_obj.utm_source = contact.get("utm_source")
    #         contact_obj.utm_medium = contact.get("utm_medium")
    #         contact_obj.utm_campaign = contact.get("utm_campaign")
    #         contact_obj.utm_content = contact.get("utm_content")
    #         contact_obj.utm_term = contact.get("utm_term")
    #         contact_obj.utm_traffic_type = contact.get("utm_traffic_type")
    #         contact_obj.save()
    #         print(f"Updated Contact: {contact_obj.contact_id}")

    #     else:
    #         # Create new contact
    #         contacts_to_create.append(Contact(
    #             contact_id=contact_id,
    #             first_name=contact.get("firstName"),
    #             last_name=contact.get("lastName"),
    #             business_name=contact.get("companyName"),
    #             company_name=contact.get("companyName"),
    #             phone=contact.get("phone"),
    #             email=contact.get("email"),
    #             created=created,
    #             tags=",".join(contact.get("tags", [])),  # Convert list to string
    #             utm_source=contact.get("utm_source"),
    #             utm_medium=contact.get("utm_medium"),
    #             utm_campaign=contact.get("utm_campaign"),
    #             utm_content=contact.get("utm_content"),
    #             utm_term=contact.get("utm_term"),
    #             utm_traffic_type=contact.get("utm_traffic_type"),
    #         ))

    # # Bulk create new contacts
    # if contacts_to_create:
    #     Contact.objects.bulk_create(contacts_to_create)
    #     print(f"Created {len(contacts_to_create)} new contacts.")




# from django.utils.timezone import make_aware

import pandas as pd
# from your_app.models import Contact  # Replace with your actual model import

def safe_get(value):
    return value if pd.notna(value) else None

# def import_contacts_from_excel(file_path):
#     df = pd.read_excel(file_path, dtype=str)
    
#     contacts_to_create = []
#     existing_contact_ids = set(Contact.objects.values_list('contact_id', flat=True))

#     # First pass - collect contact IDs
#     contact_ids_in_file = []
#     for _, row in df.iterrows():
#         contact_id_val = safe_get(row.get('Contact Id'))
#         if contact_id_val:
#             contact_ids_in_file.append(contact_id_val)

#     # Delete contacts not in the Excel file
#     Contact.objects.exclude(contact_id__in=contact_ids_in_file).delete()

#     contact_updates = {}

#     for _, row in df.iterrows():
#         contact_id_val = safe_get(row.get('Contact Id'))
#         if not contact_id_val:
#             continue  # Skip rows without a contact ID

#         contact_data = {
#             'first_name': safe_get(row.get('First Name')),
#             'last_name': safe_get(row.get('Last Name')),
#             'business_name': safe_get(row.get('Business Name')),
#             'company_name': safe_get(row.get('Company Name')),
#             'phone': safe_get(row.get('Phone')),
#             'email': safe_get(row.get('Email')),
#             'created': safe_get(row.get('Created')),
#             'tags': safe_get(row.get('Tags')),
#             'utm_source': safe_get(row.get('utm_source')),
#             'utm_medium': safe_get(row.get('utm_medium')),
#             'utm_campaign': safe_get(row.get('utm_campaign')),
#             'utm_content': safe_get(row.get('utm_content')),
#             'utm_term': safe_get(row.get('utm_term')),
#             'utm_traffic_type': safe_get(row.get('utm_traffic_type')),
#         }

#         if contact_id_val in existing_contact_ids:
#             contact_updates[contact_id_val] = contact_data
#         else:
#             contacts_to_create.append(Contact(contact_id=contact_id_val, **contact_data))

#     # Bulk create new contacts
#     if contacts_to_create:
#         Contact.objects.bulk_create(contacts_to_create, batch_size=500)
#         print(f"Created {len(contacts_to_create)} new contacts")

#     # Bulk update existing contacts
#     if contact_updates:
#         contacts_to_update = list(Contact.objects.filter(contact_id__in=contact_updates.keys()))
#         for contact in contacts_to_update:
#             data = contact_updates[contact.contact_id]
#             for field, value in data.items():
#                 setattr(contact, field, value)

#         update_fields = list(contact_data.keys())
#         Contact.objects.bulk_update(contacts_to_update, update_fields, batch_size=500)
#         print(f"Updated {len(contacts_to_update)} existing contacts")

#     print("Contacts import completed successfully.")



def safe_get(value):
    return "No Data" if pd.isna(value) or value == "" else value


def get_appointments_date_range2(access_token, location_id, start_date=None, end_date=None):

    timezone = datetime.now().astimezone().tzinfo
    all_appointments = []
    from dateutil.relativedelta import relativedelta

    
    # Default to March 1st of current year if start_date not provided
    if start_date is None:
        start_date = (datetime.now().date() - relativedelta(months=1)) 
    # Default to yesterday if end_date not provided
    if end_date is None:
        end_date = datetime.now(timezone).date() - timedelta(days=0)
    
    # Loop through each day in the date range
    current_date = start_date
    while current_date <= end_date:
        # Create start of current day (00:00:00)
        day_start = datetime.combine(current_date, datetime.min.time()).replace(tzinfo=timezone)
        
        # Create end of current day (23:59:59)
        day_end = datetime.combine(current_date, datetime.max.time()).replace(tzinfo=timezone)
        
        print(f"Fetching data for: {current_date}")
        print(f"Start date: {day_start}")
        print(f"End date: {day_end}")
        
        # Fetch appointments for the current day
        daily_appointments = fetch_ghl_appointments(access_token, location_id, day_start, day_end)
        
        formatted_date = current_date.strftime("%b %d %Y")
        
        # Filter data based on the current date's dateAdded
        if daily_appointments and "data" in daily_appointments:
            filtered_data = [entry for entry in daily_appointments["data"] if entry["dateAdded"].startswith(formatted_date)]
            print(f"Found {len(filtered_data)} appointments for {formatted_date}")
            
            if filtered_data:
                save_appointments_to_db(filtered_data)
                all_appointments.extend(filtered_data)
        
        # Move to the next day
        current_date += timedelta(days=1)
    
    return all_appointments



def update_appointments():
    # Get all existing appointment IDs from your database
    existing_appointments = list(UserAppointment.objects.filter(appointment_id="5lexvd0x5AtDcMF7rDgb").values_list("appointment_id", flat=True))
    
    # Get the access token from your credentials table
    auth_credentials = GHLAuthCredentials.objects.first()
    if not auth_credentials:
        print("No authentication credentials found")
        return
    
    access_token = auth_credentials.access_token
    headers = {
        'Accept': 'application/json',
        'Authorization': f'Bearer {access_token}',
        'Version': '2021-04-15'
    }
    
    appointments_to_update = []
    processed_count = 0
    batch_size = 100  # Adjust based on your needs
    
    # Process appointments in batches
    for appointment_id in existing_appointments:
        try:
            # Fetch appointment data from API
            response = requests.get(
                f"https://services.leadconnectorhq.com/calendars/events/appointments/{appointment_id}",
                headers=headers
            )
            
            if response.status_code == 200:
                appointment_data = response.json().get('appointment', {})
                
                # Get existing appointment from database
                appointment = UserAppointment.objects.get(appointment_id=appointment_id)
                
                # Update appointment fields based on API response
                appointment.contact_name = appointment_data.get('title', '')
                appointment.appointment_status = appointment_data.get('appointmentStatus', '')
                appointment.title = appointment_data.get('title', '')
                appointment.start_time = appointment_data.get('startTime', '')
                appointment.date_added = appointment_data.get('dateAdded', '')
                appointment.contact_id = appointment_data.get('contactId', '')
                appointment.assigned_to = appointment_data.get('assignedUserId', '')
                
                # Add to bulk update list
                appointments_to_update.append(appointment)
                processed_count += 1
                
                # Perform bulk update when batch size is reached
                if processed_count % batch_size == 0:
                    with transaction.atomic():
                        UserAppointment.objects.bulk_update(
                            appointments_to_update,
                            ['contact_name', 'appointment_status', 'title', 'start_time', 
                             'date_added', 'contact_id', 'assigned_to']
                        )
                    print(f"Updated {processed_count} appointments")
                    appointments_to_update = []
                    
            else:
                print(f"Failed to fetch appointment {appointment_id}: {response.status_code}")
                
        except Exception as e:
            print(f"Error processing appointment {appointment_id}: {str(e)}")
    
    # Update any remaining appointments
    if appointments_to_update:
        with transaction.atomic():
            UserAppointment.objects.bulk_update(
                appointments_to_update,
                ['contact_name', 'appointment_status', 'title', 'start_time', 
                 'date_added', 'contact_id', 'assigned_to']
            )
        print(f"Updated remaining {len(appointments_to_update)} appointments")
    
    print(f"Total appointments processed: {processed_count}")
    return processed_count











from accounts.services import fetch_calendar_data
from django.core.exceptions import ObjectDoesNotExist

def update_appo(appointment):
    appointment_id = appointment.get("id")

    try:
        # Try to get the existing object
        existing = UserAppointment.objects.get(appointment_id=appointment_id)
        calendar_name = existing.calendar_name or fetch_calendar_data(appointment.get("calendarId"))
    except ObjectDoesNotExist:
        # If not found, fetch the calendar name
        calendar_name = fetch_calendar_data(appointment.get("calendarId"))

    # Then update or create the record
    UserAppointment.objects.update_or_create(
        appointment_id=appointment_id,
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
            # "created_by": data.get("appId"),
            "mode": appointment.get("groupId"),
            "calendar_name": calendar_name,
        }
    )
    print("appointment is created or updated")


def get_appointment_details():
    token = GHLAuthCredentials.objects.first()
    appointments = UserAppointment.objects.all()
    error_app = []
    
    for appointment in appointments:
        url = f"https://services.leadconnectorhq.com/calendars/events/appointments/{appointment.appointment_id}"
        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {token.access_token}",
            "Version": "2021-04-15"
        }

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            update_appo(response.json()["appointment"])
        except requests.exceptions.HTTPError as err:
            print(f"HTTP error occurred: {err}")
            error_app.append(appointment.id)
            
        except Exception as e:
            error_app.append(appointment.id)

            print(f"An error occurred: {e}")

    print("error appointmens list: ", error_app)    
