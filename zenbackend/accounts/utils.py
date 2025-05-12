import requests
from decouple import config
from accounts.serializers import FirebaseTokenSerializer, LeadConnectorAuthSerializer, IdentityToolkitAuthSerializer
from accounts.models import FirebaseToken, LeadConnectorAuth, IdentityToolkitAuth, CallReport, FacebookCampaign, Appointment, GoogleCampaignTotal, GHLAuthCredentials, Opportunity, Contact, SMS, Email
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
        print("start_date, end_date",start_date, end_date)
        
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



def get_timestamp_range(date_str, days_before=3, days_after=2):
    import pytz
    """
    Convert a date string like '2025-03-04' to start and end timestamps in ms
    matching the website's behavior (Mountain Time).
    """
    # Parse the date string
    # year, month, day = map(int, date_str.split('-'))
    # Convert input to date object if it's a string
    if isinstance(date_str, str):
        date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
    elif isinstance(date_str, datetime):
        date_obj = date_str.date()
    else:
        raise TypeError("date_input must be a string or datetime object")

    # Mountain Time zone
    mountain_tz = pytz.timezone('America/Edmonton')

    # Calculate date range
    start_day = date_obj - timedelta(days=days_before)
    end_day = date_obj + timedelta(days=days_after)

    # Localize start and end of day
    start_dt = mountain_tz.localize(datetime.combine(start_day, datetime.min.time()))
    end_dt = mountain_tz.localize(datetime.combine(end_day, datetime.max.time()))

    # Convert to milliseconds
    start_ms = int(start_dt.timestamp() * 1000)
    end_ms = int(end_dt.timestamp() * 1000)

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
    existing_ids = set(
    UserAppointment.objects.filter(appointment_id__in=today_appointments)
    .values_list('appointment_id', flat=True)
    )

    # Find new appointment IDs (not in DB)
    new_appointments = [appt_id for appt_id in today_appointments if appt_id not in existing_ids]

    print("New appointments not in DB:", new_appointments)

    
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
    return appointment_ids
    
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
        start_date = (datetime.now().date() - relativedelta(months=7)) 
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
                ids = save_appointments_to_db(filtered_data)
                all_appointments.extend(ids)
        
        # Move to the next day
        current_date += timedelta(days=1)

    print(all_appointments)
    
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


staffs = {
    "Eric Cheng":"I5BcDkQF75DDv2jDIZK8",
    "GCG Support":"e46GQO3UHWmFUVrORPLY",
    "Jennifer Jolivette":"05qLOKE6RFNeG8sbwuWT",
    "Jesse Moeller":"V3W8ATQ3lQOXWj5TcXkj",
    "Lauren Barr":"8FKlyb6QMtJRKB271J9S",
    "Max S.":"rTfwSqCtENTOFNX8QZ2v",
    "Ruhul Amin":"BkE9BUb3xCvh5Ro9QrkG",
    "Russ Ward":"4TpQ6ROwiIGdvPbvqQfG",
    "Sherri Beauchamp":"R0wLHnLzfVe1a4ut67eu",
    "Theresa Syrota":"GCrVmLVF5CwSPyHE5Llr",
}



def generate_date_ranges_payload(selected_date_str, user_id):
    # Parse the input date (expected format: YYYY-MM-DD)
    ist = pytz.timezone("Asia/Kolkata")
    utc = pytz.utc
    selected_date = datetime.strptime(selected_date_str, "%Y-%m-%d")

    # Set to start of day in IST
    current_start_ist = ist.localize(selected_date)
    current_end_ist = current_start_ist + timedelta(days=1) - timedelta(milliseconds=1)

    # Compare range is one day before current range
    compare_start_ist = current_start_ist - timedelta(days=1)
    compare_end_ist = current_end_ist - timedelta(days=1)

    # Convert to UTC ISO format
    compare_range = {
        "startDate": compare_start_ist.astimezone(utc).isoformat(),
        "endDate": compare_end_ist.astimezone(utc).isoformat()
    }

    current_range = {
        "startDate": current_start_ist.astimezone(utc).isoformat(),
        "endDate": current_end_ist.astimezone(utc).isoformat()
    }

    return {
        "compareRange": compare_range,
        "currentRange": current_range,
        "isManual": True,
        "locationId": "Xtj525Qgufukym5vtwbZ",
        "userId": [user_id]
    }



def fetch_sms_last_days():
    url = "https://backend.leadconnectorhq.com/conversations-reporting/messages/aggregate/agent"
    token_generation_step1()

    token = IdentityToolkitAuth.objects.first()


    start_date = datetime.now() - timedelta(days=1)
    end_date = datetime.now()

    current_date = start_date
    while current_date <= end_date:
        token = IdentityToolkitAuth.objects.first()
        headers = {
            "Token-id": f"{token.id_token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Source": "WEB_USER",
            "Channel": "APP",
            "Version": "2021-04-15"
        }
        date_str = current_date.strftime("%Y-%m-%d")
        for name, uid in staffs.items():
            payload = generate_date_ranges_payload(date_str, uid)
            print("payload: ", payload)
            print("current date: ", date_str)


            response = requests.post(url, headers=headers, json=payload)
            if response.status_code in [200, 201]:
                data = response.json().get("results", {})

                # Prepare field mappings
                status_fields = {
                    "sent": ("sent_status", "sent_count", "sent_change_percentage"),
                    "delivered": ("delivered_status", "delivered_count", "delivered_change_percentage"),
                    "clicked": ("clicked_status", "clicked_count", "clicked_change_percentage"),
                    "failed": ("failed_status", "failed_count", "failed_change_percentage"),
                }

                update_data = {
                    "user_name": name,
                }

                for status_key, field_names in status_fields.items():
                    values = data.get(status_key, {})
                    update_data[field_names[0]] = status_key
                    update_data[field_names[1]] = values.get("count", 0)
                    update_data[field_names[2]] = values.get("changePercentage", 0)

                # Save one record per user per date
                SMS.objects.update_or_create(
                    user_id=uid,
                    date=date_str,
                    defaults=update_data
                )
            else:
                print(f"Failed for {name} on {date_str}: {response.status_code} - {response.text}")

        current_date += timedelta(days=1)




def fetch_email_last_days():
    url = "https://backend.leadconnectorhq.com/conversations-reporting/emails/aggregate/agent"
    token_generation_step1()

    token = IdentityToolkitAuth.objects.first()

    headers = {
        "Token-id": f"{token.id_token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Source": "WEB_USER",
        "Channel": "APP",
        "Version": "2021-04-15"
    }

    start_date = datetime.now() - timedelta(days=1)
    end_date = datetime.now()

    current_date = start_date
    while current_date <= end_date:
        token = IdentityToolkitAuth.objects.first()
        headers = {
            "Token-id": f"{token.id_token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Source": "WEB_USER",
            "Channel": "APP",
            "Version": "2021-04-15"
        }
        date_str = current_date.strftime("%Y-%m-%d")

        for name, uid in staffs.items():
            payload = generate_date_ranges_payload(date_str, uid)
            print("payload: ", payload)
            print("current date: ", date_str)

            response = requests.post(url, headers=headers, json=payload)
            if response.status_code in [200, 201]:
                data = response.json().get("results", {})

                # Field mapping based on your model
                status_fields = {
                    "clicked": ("clicked_status", "clicked_count", "clicked_change_percentage"),
                    "replied": ("replied_status", "replied_count", "replied_change_percentage"),
                    "count": ("count_status", "count_count", "count_change_percentage"),
                    "opened": ("opened_status", "opened_count", "opened_change_percentage"),
                }

                update_data = {
                    "user_name": name,
                }

                for status_key, field_names in status_fields.items():
                    values = data.get(status_key, {})
                    update_data[field_names[0]] = status_key
                    update_data[field_names[1]] = values.get("count", 0)
                    update_data[field_names[2]] = values.get("changePercentage", 0)

                # Save the combined record
                Email.objects.update_or_create(
                    user_id=uid,
                    date=date_str,
                    defaults=update_data
                )
            else:
                print(f"Failed for {name} on {date_str}: {response.status_code} - {response.text}")

        current_date += timedelta(days=1)


def funcc():
    today_appointments = ['gBQigleGwsmrYC2HEZYm', '2XeHD387I6F6UPcQyI4V', '6H8MRA8Mmgw1z0wkLy5h', 'Bs8tkWlvoe6odyBXJcmy', 'SPcjkqMucAeagZoT5oAw', '0H2R7YflSliMmNUR0TH6', '07jMC6DRX6VKlNFq5PB6', 'ai9N0TKgmGappKsO4PvX', '7bPNns2OTQUr6hUgPA36', 'g2iL08liM1CTpRPce3UG', 'Gp4Rb0TwDHmOvDfPxaWN', 'dmxRIS9I9Eg4mVbfzCiu', 'Q4tMS5qeY2A3V2JIfoPt', 'WCWwHX3SNDW3PjPtvgOr', 'U7bcX20BIbKtPfhFUJok', 'GLeUOB9RNpDLXHtpxr0q', 'vHKOwYve8URFOD42yqRW', 'CHglk4q7mrslq6JEOYZX', 'EVJfuDsH0HXmOtvXwk0C', 'LDoFNzZVvVr0vCvskNQf', 'VafNJQhvRWnA0UA4QePJ', 'N5QxLVxXrx8SwRNbPegB', 'yxEsrPptbHH0GF1bKLc4', 'vmXmXHuULrF7zfBhcyyn', 'vhWoSW4GIzzubL5FCWtc', 'EQ2AoFoFsikPgZ3gaZD3', 'h29bzl5qqGGnPzuAMjAw', 'g822OHCGQKSnOBUnPfhs', 'HeZs7N3OgnkMuMZMPfby', 'NB7H1YgRsToT7WgokJZK', 'jFecoxhfNTTurSW9GtW9', 'WqPyNtpl9HYP0LPk4B3Y', '6Zp0LFxawVFScWbU5c1z', '4eP8CGvSkkAIrAoeFidW', 't26tquiTPObYtphytLby', '4su68QYXfuCnQxC6Gpyl', 'e5BBE4amRZnrBJuiQ8MJ', 'rxCwMcGWxvP15P5NI36p', 'b6VSQBzHc7FGqJo4sn56', 'vJezioFsPGq7dj3bVhj6', 'tf476ptEA7tkK8lvuInk', 'S9HFhUQ1yP9unk5GLwmL', 'P9ICXxfDcTEvKeELtrlx', 'VXEmCMNQUf8nH0mgqg4m', 'YLZ3l8FJkKgS2HXEUu5Y', 'Jp3ZN7WZEAQ9DvRVjgEy', '7K52G13X4J9JjRa8IGG5', 'LSpeA3YPgucHQcpKSHvz', 'inNs6AwPPNWYSdTwTYLV', 'Mp3u9gqHdL7HkzVopcgs', '8l8hz5p13iGtw7Wb14wq', '0I0wWOJvuVPULWvOhWhF', 'ZjXOCbw0OuogLjXeHQ5Z', '3rerAwunZ4NRYdAdDlQU', 'GjMSOXyPEI1JEaEh1JuB', 'Jk7BPCRKSCrhdG2ulK9Z', 'EIiNQ8oTPHmlzIVDOh8a', 'JBCyCnPBW6LKQ8iFmCPH', 'sU0kHN0piZ6LfTupMyPB', 'amKvXNtDTyaN9gmeoTFb', 'NjyUn8zgvo32urcTzjEX', '9BPb4kWIhP3RDPoLEL5y', 'UEZlc2SvpOI520Nclm5i', 'MeFulY7zeoAhYqqRhAgp', 'dGqp9inHv93604sNSxdB', 'Zu2GXlLMJ7Ad31CIOET9', 'IuuRd8OPbvZ60uRW7wTV', 'Ivf3AfTQ6baLoxiAPXFq', 'hRN3xoq6xRWPDPK3IUmX', 'aePvTKPUPeapCD7cajtO', 'DhhM3O5AylrwDaN3Y94u', 'zjoQVY1JrVXV9dGozlxK', 'WfNLI4c7nicMZUnMkw8f', '7P5VX32pyQdn1fDO6Vcc', 'QwCjgU7OXhtD1yFcscah', 'lt7HvmsO78xWXCTldSAf', 'f5W3e5flDQ7h9SzcW78M', 'mdDeXalpq4gKW295699n', 'Mw6W32goLBL23fki1rwM', 'Fzge8kxM9p4bgXfnxQHh', 'jVsVPuNAvqeW1SYkt7VL', 'BXcgKk9j5WYCM4QuTK1X', 'IvuXr7ooOCfXgRotz9C1', 'K8GAKm8nsSoJRWzyPwqv', 'hso352QpZPiWiUG3qvVl', 'WsFjt5hn5QSfPUq5oJ5c', 'ITQG1fbjgszqW1h69vYE', 'tnSr4NcjuGUpwlLr0zWZ', 'Ttj9afPpzCRsXHXmkrvT', 'hqC559jSu566BhcYPnqT', 'wSp9v2IupxRkzu1HRtQE', 'UpfEwpWLk1TP8JBUz8fz', 'GRfCYntfTQHVVIjklORs', 'q2fXjoIlXjwpEx3k8GYd', 'E49pL6znEZJdUbAwBq2W', 'r6p4iT7Bj3XaMca68P9m', 'or5kZWonhso7U4hEF5PE', 'AbtiMMLcs5SpFOZmiwpr', 'oZPLpptyR4ojTwFa8KqB', 'JMvhSZBs5bgbKnzaJDkz', 'KBut9MUOytcOFFZqoFKQ', '3a3gMa4ggXeDZzx9TaN4', 'SqZReRc9bXWRX8YDNWO6', 'hUEsw6ALlgvaNLrMRvnK', 'x7XTK8lvarkByp0gEoaH', '1dhsd4wWoDYST2WiDnGN', 'aXCj1D3hHJpbYNk4v3kE', 'SV0AeJQ3DszA3jHirr21', 'JKSxeXDfUWwNoWlFEpZP', '1UCAZq5r66FkDsSAuhi9', 'FUbsBBlvVe2DizUYbNLE', '0mLcAAHHbfmaDzLcOyNN', 'UlBbHd8RJ8aNUidPqTdq', 'F3UrSsBrOd8EyeGYFIiE', 'qsw3tMKtezoeERfxMGSn', '2YSDsq9ZgN9ETol3TeLL', 'U7ykjOjbEPNf29ZAhqBg', 'xo7csIvNyNfakh6wJJKM', 'Jb5DVdr2yreZs2ZN0u0Q', 'pK67rDK7uVoUZhbQBZrh', '8P5KsOkSk0pnbvcBwHis', 'Zmu3Nx9nAUPSV9mKibSQ', 'W0nFW8uZYBdgtEvQucU5', 'KL5uE99yeTFN5WMciPEN', '1zFe7gQ6SmmMURyZJqDV', 'ngJL8JmP9jQyfMYMC5L5', 'kAXyiY4fyIfDDktfAj74', 'eQbtoPDzfOm3hqjOpy6z', 'Wd7ue1NxK0FAiQsxXpAw', 'dmiwLBCRWUt4VYbF87hN', 'DXi767JN9IixRuFCWOqG', '24SwtxtV6cZ8EQzm5h8Q', 'yGbj7XMRpjpGtpPXcHcM', '7M3deNUNH5ollDlUtieJ', 'xutptdX7XiYPw6hJKFnl', 'oXbl4148iRL9HzXz884p', 'zGELFJQ9BNA5T4v5Px9z', 'U5MGhz6yWJuHXh8VK6TD', 'WEp9bCUbTN8NAGriD3Hp', '866NQ24iOk6wo3hZpL1E', 'o37MLRGi9LY48IpqgRDQ', 'EyfOodxZRAeAINcPJ6cR', 'vaSzcwiJCNafcClu7DeL', '4SChBObMpxkuhSUmhD9x', 'bNECYbjJmAhGMJyVbqlj', 'PckVoR4TqYzGD7D7pBs9', 'EVbI7UQqLqmFhbeH2Jks', 'Vbb7q6KPa5hDw6uDTx3N', 'TGJxIPvvAbi58M6YTtmG', 'DK6Is37UXqqsqqbz14CH', 'Q1FPKMx2gMPRtwJ9PloB', 'GHUnFZurPhNkOioZwWsD', 'owMiPquxwseaiNQctmox', 't46bHXKEXUTlybNXW79f', 'EKEDhZ7oC6co0nNZpxUz', 'SCPykKAekci1LdFCBxvf', 'cg7slmKiqc00HiiB0liH', 'SnFa3YikEkBtd2pDq6dx', 'f5GpMlYSSMmuGqBJ77vn', 'pTMyuOmTqt8hsQ1VtnHw', 'LgBelcx83sMSRyZFd7BP', 'WkZJrQpmCRDSFfOiUCBk', 'hFYyNTi1ABGsnMzCRRkC', 'HwBn1fTcIBx42vUWfXES', 'iBBD2tEPSA8MYc0J5lKC', '69XAyL6HlCgChe5WF6kf', 'Op4qtE8JqPW6VPCZttsz', 'XeIXdz2PLmvsO7tl7SuE', 'bhGduYIIiSFD9UeiSaud', 'bt2nwz5e9yvx8BTqsoqX', 'SuT0ruDSGfVdz43HqLJ3', 'ApjWQbfCAK9bbH8RHwP3', '1rHGVi6wBvfoDBRBDLCy', 'x5tdDbbf3MkWT0LfzEhB', 'd7TYlcQZ7DcluCDRq6ET', 'dvomtATnBNIkKyXlT2rH', 'cBFXPXNUVRM4IrnbEomR', 'qca6Oh3Q4UkDKrmd0wBb', 'B8pi1sKbDcVy8GYIdpXm', 'Mx7q0Zs5hSAg7DUhW9kp', 'xPxREQFxRwUcBtitTwE7', 'kIPj1windi0WGzne1yzb', 'd6fgsboPSEjs98O0LXd2', 'SQSdORWTEIEyjEN6dKBY', 'IhEeqzS79FVcpYhoocx5', 'Ljn6UOPv4F05qyBTGmhv', 'gh96qyhVaxTdX9gjNrb3', 'RXPAvyt0slt9lzVOuYdj', 't65WxcO6AHhpiLXvBa6u', 'FrArh1XfwSuafwmSoMo4', 'H600DicDFYzN3XqERPA1', 'j0JuEly0DKlbl8k8geuE', 'VrfQeIoXChYspHDFlr8M', 'jgIl5Xc0yUWTAKKrEDrh', '0fdMh27ELPwTbCvAUuGF', 'dYgrXidfiKHIg9U5AhqP', 'ZbI1m5TFYcmCpNItu0dn', 'aTlo5LViMlBW9FrMIA9z', 'oV9ZPIU2StZmqiFYfXjC', 'RIAiJ09OidAkedllkaKL', 'QNKrLOqLl0HlhJhFJGUV', '8f2OifcBd2zctKrVPcUF', 'rgzFfxJf9YhH6WlKUx6U', 'SgDMjlFthtQa0gY68Ftn', '2KHkulLkygUU1dqWVvCs', 'wWoweF41GuJPhOx2oc11', 'ERipEvhT7HH7Enx1w5B6', 'lqNXqPcL8jVnPRRMORDG', 'pq5LVCieOaEnL36PogR6', 'R4X57jLsK2nSk24r7Te2', 'Ge54IDuYAmYJSgEyF7Pw', '9pkCdiCGc88PheD930LJ', 'O4QM8wRGGNYuLYnzUL4i', 'QBCAkzYGHZPzX8zgBlIt', 'EyoxND3ce56NwWyrUMsr', 'Vl9Rlmz2ERhLyBY8pMQC', 'GqQnzMmy2rEejKEsyAWo', 'A9s6r1Sc9xDdEgJEluwV', 'mk6vITVCmwsLSbHxyKcO', 'IHBwLouucYnGKz1Q9JL7', 'Bx17Y5gvPavWtREvKWYZ', 'OwGn5MenmfI1M8bazvvb', '2C65wF4Kq7EHhhIH4URY', 'HFpHus1776zTtWZayKex', 'egloxo8P4pj4SL1DBTcq', '5nuqMSDcO2EKFX2gPOCq', '4KTFchaC2RugtGQUsEST', 'UciezwYgAVo5OdONitri', 'Ikr3k8OX2Qor3kZ5ziCd', 'TXZkDQGny718oVU9Rh95', 'Jh5j2dY9BA8KNym9NWRK', 'e9WphB9xKXsBuAInJSkn', 'LTgcbVKb0YZVeL0GXiR6', 'P5MzGqQMmJVyCXiolOii', 'D9ROeHDCLPHDXyQ9PoZ5', '28a8PtI76w3cdgmfeENs', '1Umc0ZwhLfsuqfz1Oil2', 'KDACFaBDtj6y3NZ59Lit', '86YmKVxhv03WzgzdjGbu', '3FCAqFHUq6fBxEgEZjOF', 'n5H1Dg4K9vUNMnGPKnCQ', 'eyjbXRVzHI65IsH6BhpZ', 'Nvt5zBn7ttM0SIqfjr5D', '56cdvTHu3EqUzulb15TR', 'fDUjNKRCUG2TUUDsBpLX', 'P3H16jaGVzQC0brWRMza', '85QL9bnFzoj9TS6UrQEs', 'Db7B9jyR8pqClnhy21yq', '0vGvUVUS4MH9JGmOTqSY', '0ewhPmHPM1wirm7cFBsS', 'PADCrANwLbq0GZ6wncIg', 'C7n2rll8ysnUbO7a02x3', 'g8sIuQuYKm0DYE09yjiv', 'sdriwnfb0UuMSKQrRkSh', 'ehZzAQ2gfUXMiln9lGv4', 'dbofdb5P8R1ZnG5UcTZj', 'QuodrFo7UjHiQk5lnO6X', 'RoWUx80kOUoRTCZkoUM6', 'uSpslLKvUgFhgIgifRkz', 'cxKPKMJ4r01nEpOzRmXQ', '9zSY0jWDKWYOwaL8FNbD', 'svggWfJSWBlShiObPi6V', 'kwvbok7qy3nCnq7yfDH0', 'M5Ua8JyLYyIbb0QlDv3k', 'NL3X9JwsOgvWLOXYdr0t', 'DmNc0zrPrD4CVugZdwDx', 'zw4UbvBCdsd9XKy6e6sY', 'BMe3nx0WU13yCwOwvgsU', 'mZX8YYie9qB9hk5Qak6w', 'pjGsU27xCyNQBWDyCYg9', 'nt0NCFU9bAOl0XS1FQtS', 'C2bXnWfReCcN8RU7LeFC', 'AT54wnTPTK1YQpv9Izd1', 'udVrHRDK96kZOOGyCvru', 'm1kLpy2wD2KVWKxzBGm8', 'USwjpFF9xDRU4A5ax20Z', '1BuPModiOSUTkMnF6nhP', 'SpYFYXDMn26p1DPrmCV9', 'ceIjS2zjxSwXsjIlE7xN', 'kUaKBXkDsc334KB5LNl8', 'pWq2DuFrsjs0UehOZA1a', 'XuUDwD2vhbhnK933QcFE', 'taJTdcJ7IAoEbY3fii6i', 'uB3QJExmt4clnJERcDv7', 'c7MMlZ3uh49wPMb0lGiW', '8yM4EtyfMFRX6PO0sk2g', 's9VaWRAOHpX2WCDuhJbU', 'EECOMZYCRcoEKhrd3n9n', '08zWtZHnEuTJnmGGp72u', 'VgENkNxhBrGtpHpcenRX', 'fD7GAAKEoyQfXZLVo71x', 'LESSDwfBAU1Oa2Q9dFhR', 'FEBcW6myeQk014ZdfXJb', 'ZFtCOmuWHoWzoNbk6cSD', 'yP4Wet4uMiuqodaxRGzK', 'tDzpJ6fdW2rhAysDAg7u', 'u5mgFLzu7sQzVg7HNto0', 'JomASepnkB5YCPENFMRC', 'jziQHZBJcYsV0jB6m9wl', 't9ecksFBiOXvtqSEZJr7', 'pJa9C8GW7M8VAVuucr30', 'BqiKDljNrXBSup4mYnwQ', 'mXfllLSGVwWIcSDiiQ3u', 'KZ193i32iGgAD83wwncg', 'Xh0TW1czegQr6feog1LH', 'ogre0dZbT6rZgHEvMiKI', '8bLctlD0znJ7h9zqQirf', 'oY2lHmZsIHQJBmxkhXlB', '8UL9mp4YsSJjmfzZ1IhK', 'taMYx3JpcTOtel2b8SOi', 'K9gy0xwEOH5eTikWvUnK', 'aZPGyuqvOKUYjPBXWoFo', 'Rhmv4F6DYbX6a3SH84ZH', 'mcuEmQpTubaZyk4JrQZ1', '5m1eEMCinPBVjBi5vXFp', 'x8K0Sjl69vP24EGqJoEQ', 'ypCdXRelMXPsOr0EO7zJ', 'YmhiDYOomXP1WoDNjuyy', 'bjiwK65zxZIBUU6RIL1o', 'ioBkL3xwJZyW6ShRYDTM', '8QlwLNFpKSZPdd3XlvkD', 'CLCzGa2Qd4VPBk6GHzRY', 'QcALSX64YxLJ2ZO7hi7x', 'cKWwQ2f3sIzf6vkMeQFc', 'ANh7HRQjtFHU51VmnI5W', 'H3pTqY75XZt452522uQC', 'kC2MhIoxnZWBr6T4o16r', 'Jt45GFBKREWfSOcATCu9', 'KsJh8YkHeYEP7bV5uNah', 'yyLHRm6jMJgrEEncMTiO', 'Afeas0hQxG2vRibXJRkC', 'PM0oVDl5QpHuJGMbmd7U', 'DIV6HLqIchYJsoVMuWyI', 'HAIi3wvLZgAZkAmO1QUj', 'aJD45DyrKSkFhY8vUZfO', 'qtw75Kl8XBh36EmAhPcJ', 'XVZUBvrghqZMYB53g3Ie', 'WEhl3KkvjMZttnA4oVCJ', 'Kef6pFtDJnHkudYEj7u4', '9dc11wh6lcIE9jX08CQa', 'h9We6nh0JZr5AysQZNxQ', '4N69PovSMKMFmZ82gGng', 'V8mImbnGO9C4rzsHODVI', 'ssmJwMrMQ4Ivu521ulfm', 'tXmYBYfkgDpTNZol3bha', 'RUXGyKLXzHPItyllOLI9', '1jlEV1tIRE0LINMCBOU0', '2cjsR8Zsh0ar5UTChD0t', 'kBd4kbtvtga5S08xdbGX', 'Xj6uEbqZWaM3HsTDodaW', '5lexvd0x5AtDcMF7rDgb', 'kPlBc8YzJVbrwaO9yvUI', 'ofS3e9EmcfeiHHuJlGKX', 'fsvdCRiF9UJP1dcN5tlH', 'qrTz95cKmvGsje8upxhP', 'cDoXteaZnaU3YQW9vrq6', 'ETVrHgwqSxHHa2CkWw9j', 'SgKj5hAhs2o5Azxyu2ej', 'hOsRoOXqAdo7tqCkcUUP', 'rUXVUf3tXb1mbfqSuxlI', 'DTV5nyIAW4RZW3zO6Hyq', 'w39Pxqh7EFWxreTUhfeD', 'oQoELdohGfxPnxUkZpx2', 'gQXndLxvuqUao1P2YVr8', 'xYsmraPPmcZT4MqacaT7', 'FhDYaUhsHkBm7n5sy09c', 'yVJJK8DIngLO0Eu0lC3r', '4QcWNbclAAaXRZcrkZUo', 'biBB3JG7JCVbzaA3jZgH', 'NePRs1NNl75FkHGy7PRW', 'lAXfzu8e1BH0sHT9RYaU', '3laR70DUVY3XEFreh97k', 'H2uIcOinbXQ28HuFJjTr', '6SSOb6tk8hjzZ98rpY2K', 'iWzGPuC4U9dWfUSskKTl', 'iHvBfvs4S2nPa8hky8tJ', 'z33uLbXiYQUvEg4hci1v', 'IgANt0Gg98f0lwXDtiu3', 'CXLCUxQ8yZoWVSC81gOc', 'GSBPH7EJTgJ4GQCgUecR', 'hlfaNXsuhb54LIWDn2g6', '6guHneoELHip8ftARViw', '3iBNgazwLJ0Y4hkQh5P4', 'jCs7scOyKQp3pAKq0WDV', 'IRBuDGcHOgEkdXFOUugB', 'ESiyy3uhC1EI931xL1xl', 'twxrAIDccAihWioiWcUb', 'l8YpSxWWYUMcRjDBOwJT', 'foPEZsfw1PPFzwt7kBTr', '5kj7O4aBuVEdSKJKLOX5', 'RbPlyT72iZ4I1lNArOn3', 'lYHByBiUvQTKUJXo4Nor', 't5DZREqGMvpuGe10I0ld', 'jVcZpqXuBCwLg0osfX5y', 'zVMt8SqK08ZX2u9LvK2f', 'Q5ptcp2Vi91FXKb7bfon', 'X1546thPrum1AN2R5vsc', 'aTGRAb99PMTn64cK8ZRT', 'XYT17WvrtAKchjo4TvRC', 'bPY5FMhC5N0xNcj6WoMg', 'kgkKUcwT1uCUzJTp7QLB', 'o6EvNpj2iVE4nGWnN6H7', '3J5MwaVb2anK8otPrGDQ', '5a7sRKXiWhvF6MgE65aD', 'n7ofHirnfEueuVfSpuHh', 'FPBGH60wk82SWdeAXYqr', 'tHQMuFSsgZOcESZu4eyM', 'YGvAbLufaTVeuPRm5anI', 'CQbpfR8h9MsbCv1yiUYm', 'bvFIwZXmRUa1gzcmpXxk', 'moY8p1y9wFp3JBmNwF78', 'ojC5azlVJVaCzxrfcQd7', 'K7sv3pQxQwa4HCVaTIbv', '2xapBso1yMYKwybjOnSs', 'TyVvCsZkkiTGIMJXFlVX', 'lYtmof5MBObV8UyUQbZ3', 'DajbkxiiaMaWrz9IZTUx', 'X37FAQkbdIfJxbMxMZFZ', '3twVmX54wxuYVnrzSqS8', 'tWGTNfJd8dAyqhjUYOqi', 'hMmFfEcATqAs6HWihILj', 'TO0uOiUaju9nhUhxNuHU', '2WL0RlnpudsEF23A1Gbu', '1ff1U9QpTWD6cCOutsUz', 'ejDjDyI5iFxHqVbD3iaT', 'flH61FjRJk9ivYkRr6OZ', 'iI2uGAsecnDg6ItJ7lWs', 'igi9EOplyX1am6G4SjYO', 'N640p7LRbQBaIbsSKIfU', 'Dj2ufpcOweAUaMmkU3IY', 'kpP2TjaTMfZXO2qvmvJ1', 'OOdk2dJkKSSUSMXdps98', 'L1iY4MCKvcr1PQhSu3h4', 'ZKayXtEHjdt0DBtzl7E4', 'bKWwl4iBoFqubbuvbLLZ', '5utV7sKjzLhL5MnSy397', '1ImjThz1S5yXyioXMiO9', '9cIh8ZEshJvGS4A9P7LW', 'y4Yu932TyjU4bZADgrdy', 'wv4GxrXMHG6jc3akURXJ', 'UeeAaDyE3XFP5zWcZiJn', 'u3Ymb9k3QiZ7TED8RI6h', 'g72JUWdqH2Il7OCLOV52', 'owVtN9hR0vXpjYJLOHv4', 'gj0PN0kYFBfqDelKzrRA', 'CVILEr0ZOodXTIT7DT3Y', 'FLoQ50enDt9tPyoK8B51', 'P6XcejtNfMbQPOj1B4Hv', 'FJZdWMSgOwbjYq82jl1w', 'iqrlKnprKQ2rXCmaPXVO', 'ykBKbP7HHRf1m6NDgK3t', 'GDuODJIQp2pglU2n7bBA', 'MKNfwoTFOoEloRejjyWZ', 'ucroxAWT6OvB5chb4tDp', 'R6bkvmen4rmRn5T8ZYDx', 'yTIoJs7nkI7tycs9Ezer', 'rbpwxZX2nhaoh8mQ4tTT', 'bdJ8Pv7mcvMvOcihv1hA', 'ZJjOc5DgJQYs5KkTMkzY', '6qZ5VD2PtS65GKWLjxSv', 'FYj66OWxyzwMRcezJETO', '0vWg3Ppqdh5eBxrdPlE4', 'hybFU1DI2FYpVuwzYKFe', 't38JuOkyvtoeAPuvX7KZ', 'gsIPoSXhAL9OGAw5dgky', 'w1qcn4BPlzyxZKBSV7WH', 'aPu0JUmlDSAP44glwHmN', 'L3q6Xq4RFX9MxVyYZS6W', 'uweovBlVC0Re3JYyFM7h', 'omXrC2YSTHjbnlWj5BSN', 'QAtPJwFdnmjWTs1twJRD', 'rarAgYO3gv3nw3VnSFW8', 'FWT4TlpYPrKbPqfLqEXI', 'z1HlRyotra4GczlQCxrr', 'SRRQdqCMFRlrpCDmtYsg', '3Ucj2SVBgsLlFMtnS5Aw', '8ZSaDIs5vZL2FsMRwsu4', 'DoCTvBww1SZh2gstBB1i', 'YuttjZFMdFxim9Kdvm4Z', 'gYEyBfTDXCH6qJSzLS8P', 'VfgwBdyP7GcEoLaKkmWf', 'Sx5mvq0smizP9mxrePIB', 'sfDPCMcAioytlOwgFjgd', 'Luf6TmkJXBAHk8H9Job3', 'obS0ekdE4TYq0V3QBe7Y', 'xBUQbKd4e24lrfdXFTUp', 'B07P3SYSijw2oGp5rqHk', 'd3IbxjBIcivhfpqEJ3Wk', 'Hp43BhfZZ1h8lRplVhQl', 'xPXHbwhTKUBCJr4QiyRQ']


    ff = ['gBQigleGwsmrYC2HEZYm', '2XeHD387I6F6UPcQyI4V', '6H8MRA8Mmgw1z0wkLy5h', 'Bs8tkWlvoe6odyBXJcmy', 'SPcjkqMucAeagZoT5oAw', '0H2R7YflSliMmNUR0TH6', '07jMC6DRX6VKlNFq5PB6', 'ai9N0TKgmGappKsO4PvX', '7bPNns2OTQUr6hUgPA36', 'g2iL08liM1CTpRPce3UG', 'Gp4Rb0TwDHmOvDfPxaWN', 'dmxRIS9I9Eg4mVbfzCiu', 'Q4tMS5qeY2A3V2JIfoPt', 'WCWwHX3SNDW3PjPtvgOr', 'U7bcX20BIbKtPfhFUJok', 'GLeUOB9RNpDLXHtpxr0q', 'vHKOwYve8URFOD42yqRW', 'CHglk4q7mrslq6JEOYZX', 'EVJfuDsH0HXmOtvXwk0C', 'LDoFNzZVvVr0vCvskNQf', 'VafNJQhvRWnA0UA4QePJ', 'N5QxLVxXrx8SwRNbPegB', 'yxEsrPptbHH0GF1bKLc4', 'vmXmXHuULrF7zfBhcyyn', 'vhWoSW4GIzzubL5FCWtc', 'EQ2AoFoFsikPgZ3gaZD3', 'h29bzl5qqGGnPzuAMjAw', 'g822OHCGQKSnOBUnPfhs', 'HeZs7N3OgnkMuMZMPfby', 'NB7H1YgRsToT7WgokJZK', 'jFecoxhfNTTurSW9GtW9', 'WqPyNtpl9HYP0LPk4B3Y', '6Zp0LFxawVFScWbU5c1z', '4eP8CGvSkkAIrAoeFidW', 't26tquiTPObYtphytLby', '4su68QYXfuCnQxC6Gpyl', 'e5BBE4amRZnrBJuiQ8MJ', 'rxCwMcGWxvP15P5NI36p', 'b6VSQBzHc7FGqJo4sn56', 'vJezioFsPGq7dj3bVhj6', 'tf476ptEA7tkK8lvuInk', 'S9HFhUQ1yP9unk5GLwmL', 'P9ICXxfDcTEvKeELtrlx', 'VXEmCMNQUf8nH0mgqg4m', 'YLZ3l8FJkKgS2HXEUu5Y', 'Jp3ZN7WZEAQ9DvRVjgEy', '7K52G13X4J9JjRa8IGG5', 'LSpeA3YPgucHQcpKSHvz', 'inNs6AwPPNWYSdTwTYLV', 'Mp3u9gqHdL7HkzVopcgs', '8l8hz5p13iGtw7Wb14wq', '0I0wWOJvuVPULWvOhWhF', 'ZjXOCbw0OuogLjXeHQ5Z', '3rerAwunZ4NRYdAdDlQU', 'GjMSOXyPEI1JEaEh1JuB', 'Jk7BPCRKSCrhdG2ulK9Z', 'EIiNQ8oTPHmlzIVDOh8a', 'JBCyCnPBW6LKQ8iFmCPH', 'sU0kHN0piZ6LfTupMyPB', 'amKvXNtDTyaN9gmeoTFb', 'NjyUn8zgvo32urcTzjEX', '9BPb4kWIhP3RDPoLEL5y', 'UEZlc2SvpOI520Nclm5i', 'MeFulY7zeoAhYqqRhAgp', 'dGqp9inHv93604sNSxdB', 'Zu2GXlLMJ7Ad31CIOET9', 'IuuRd8OPbvZ60uRW7wTV', 'Ivf3AfTQ6baLoxiAPXFq', 'hRN3xoq6xRWPDPK3IUmX', 'aePvTKPUPeapCD7cajtO', 'DhhM3O5AylrwDaN3Y94u', 'zjoQVY1JrVXV9dGozlxK', 'WfNLI4c7nicMZUnMkw8f', '7P5VX32pyQdn1fDO6Vcc', 'QwCjgU7OXhtD1yFcscah', 'lt7HvmsO78xWXCTldSAf', 'f5W3e5flDQ7h9SzcW78M', 'mdDeXalpq4gKW295699n', 'Mw6W32goLBL23fki1rwM', 'Fzge8kxM9p4bgXfnxQHh', 'jVsVPuNAvqeW1SYkt7VL', 'BXcgKk9j5WYCM4QuTK1X', 'IvuXr7ooOCfXgRotz9C1', 'K8GAKm8nsSoJRWzyPwqv', 'hso352QpZPiWiUG3qvVl', 'WsFjt5hn5QSfPUq5oJ5c', 'ITQG1fbjgszqW1h69vYE', 'tnSr4NcjuGUpwlLr0zWZ', 'Ttj9afPpzCRsXHXmkrvT', 'hqC559jSu566BhcYPnqT', 'wSp9v2IupxRkzu1HRtQE', 'UpfEwpWLk1TP8JBUz8fz', 'GRfCYntfTQHVVIjklORs', 'q2fXjoIlXjwpEx3k8GYd', 'E49pL6znEZJdUbAwBq2W', 'r6p4iT7Bj3XaMca68P9m', 'or5kZWonhso7U4hEF5PE', 'AbtiMMLcs5SpFOZmiwpr', 'oZPLpptyR4ojTwFa8KqB', 'JMvhSZBs5bgbKnzaJDkz', 'KBut9MUOytcOFFZqoFKQ', '3a3gMa4ggXeDZzx9TaN4', 'SqZReRc9bXWRX8YDNWO6', 'hUEsw6ALlgvaNLrMRvnK', 'x7XTK8lvarkByp0gEoaH', '1dhsd4wWoDYST2WiDnGN', 'aXCj1D3hHJpbYNk4v3kE', 'SV0AeJQ3DszA3jHirr21', 'JKSxeXDfUWwNoWlFEpZP', '1UCAZq5r66FkDsSAuhi9', 'FUbsBBlvVe2DizUYbNLE', '0mLcAAHHbfmaDzLcOyNN', 'UlBbHd8RJ8aNUidPqTdq', 'F3UrSsBrOd8EyeGYFIiE', 'qsw3tMKtezoeERfxMGSn', '2YSDsq9ZgN9ETol3TeLL', 'U7ykjOjbEPNf29ZAhqBg', 'xo7csIvNyNfakh6wJJKM', 'Jb5DVdr2yreZs2ZN0u0Q', 'pK67rDK7uVoUZhbQBZrh', '8P5KsOkSk0pnbvcBwHis', 'Zmu3Nx9nAUPSV9mKibSQ', 'W0nFW8uZYBdgtEvQucU5', 'KL5uE99yeTFN5WMciPEN', '1zFe7gQ6SmmMURyZJqDV', 'ngJL8JmP9jQyfMYMC5L5', 'kAXyiY4fyIfDDktfAj74', 'eQbtoPDzfOm3hqjOpy6z', 'Wd7ue1NxK0FAiQsxXpAw', 'dmiwLBCRWUt4VYbF87hN', 'DXi767JN9IixRuFCWOqG', '24SwtxtV6cZ8EQzm5h8Q', 'yGbj7XMRpjpGtpPXcHcM', '7M3deNUNH5ollDlUtieJ', 'xutptdX7XiYPw6hJKFnl', 'oXbl4148iRL9HzXz884p', 'zGELFJQ9BNA5T4v5Px9z', 'U5MGhz6yWJuHXh8VK6TD', 'WEp9bCUbTN8NAGriD3Hp', '866NQ24iOk6wo3hZpL1E', 'o37MLRGi9LY48IpqgRDQ', 'EyfOodxZRAeAINcPJ6cR', 'vaSzcwiJCNafcClu7DeL', '4SChBObMpxkuhSUmhD9x', 'bNECYbjJmAhGMJyVbqlj', 'PckVoR4TqYzGD7D7pBs9', 'EVbI7UQqLqmFhbeH2Jks', 'Vbb7q6KPa5hDw6uDTx3N', 'TGJxIPvvAbi58M6YTtmG', 'DK6Is37UXqqsqqbz14CH', 'Q1FPKMx2gMPRtwJ9PloB', 'GHUnFZurPhNkOioZwWsD', 'owMiPquxwseaiNQctmox', 't46bHXKEXUTlybNXW79f', 'EKEDhZ7oC6co0nNZpxUz', 'SCPykKAekci1LdFCBxvf', 'cg7slmKiqc00HiiB0liH', 'SnFa3YikEkBtd2pDq6dx', 'f5GpMlYSSMmuGqBJ77vn', 'pTMyuOmTqt8hsQ1VtnHw', 'LgBelcx83sMSRyZFd7BP', 'WkZJrQpmCRDSFfOiUCBk', 'hFYyNTi1ABGsnMzCRRkC', 'HwBn1fTcIBx42vUWfXES', 'iBBD2tEPSA8MYc0J5lKC', '69XAyL6HlCgChe5WF6kf', 'Op4qtE8JqPW6VPCZttsz', 'XeIXdz2PLmvsO7tl7SuE', 'bhGduYIIiSFD9UeiSaud', 'bt2nwz5e9yvx8BTqsoqX', 'SuT0ruDSGfVdz43HqLJ3', 'ApjWQbfCAK9bbH8RHwP3', '1rHGVi6wBvfoDBRBDLCy', 'x5tdDbbf3MkWT0LfzEhB', 'd7TYlcQZ7DcluCDRq6ET', 'dvomtATnBNIkKyXlT2rH', 'cBFXPXNUVRM4IrnbEomR', 'qca6Oh3Q4UkDKrmd0wBb', 'B8pi1sKbDcVy8GYIdpXm', 'Mx7q0Zs5hSAg7DUhW9kp', 'xPxREQFxRwUcBtitTwE7', 'kIPj1windi0WGzne1yzb', 'd6fgsboPSEjs98O0LXd2', 'SQSdORWTEIEyjEN6dKBY', 'IhEeqzS79FVcpYhoocx5', 'Ljn6UOPv4F05qyBTGmhv', 'gh96qyhVaxTdX9gjNrb3', 'RXPAvyt0slt9lzVOuYdj', 't65WxcO6AHhpiLXvBa6u', 'FrArh1XfwSuafwmSoMo4', 'H600DicDFYzN3XqERPA1', 'j0JuEly0DKlbl8k8geuE', 'VrfQeIoXChYspHDFlr8M', 'jgIl5Xc0yUWTAKKrEDrh', '0fdMh27ELPwTbCvAUuGF', 'dYgrXidfiKHIg9U5AhqP', 'ZbI1m5TFYcmCpNItu0dn', 'aTlo5LViMlBW9FrMIA9z', 'oV9ZPIU2StZmqiFYfXjC', 'RIAiJ09OidAkedllkaKL', 'QNKrLOqLl0HlhJhFJGUV', '8f2OifcBd2zctKrVPcUF', 'rgzFfxJf9YhH6WlKUx6U', 'SgDMjlFthtQa0gY68Ftn', '2KHkulLkygUU1dqWVvCs', 'wWoweF41GuJPhOx2oc11', 'ERipEvhT7HH7Enx1w5B6', 'lqNXqPcL8jVnPRRMORDG', 'pq5LVCieOaEnL36PogR6', 'R4X57jLsK2nSk24r7Te2', 'Ge54IDuYAmYJSgEyF7Pw', '9pkCdiCGc88PheD930LJ', 'O4QM8wRGGNYuLYnzUL4i', 'QBCAkzYGHZPzX8zgBlIt', 'EyoxND3ce56NwWyrUMsr', 'Vl9Rlmz2ERhLyBY8pMQC', 'GqQnzMmy2rEejKEsyAWo', 'A9s6r1Sc9xDdEgJEluwV', 'mk6vITVCmwsLSbHxyKcO', 'IHBwLouucYnGKz1Q9JL7', 'Bx17Y5gvPavWtREvKWYZ', 'OwGn5MenmfI1M8bazvvb', '2C65wF4Kq7EHhhIH4URY', 'HFpHus1776zTtWZayKex', 'egloxo8P4pj4SL1DBTcq', '5nuqMSDcO2EKFX2gPOCq', '4KTFchaC2RugtGQUsEST', 'UciezwYgAVo5OdONitri', 'Ikr3k8OX2Qor3kZ5ziCd', 'TXZkDQGny718oVU9Rh95', 'Jh5j2dY9BA8KNym9NWRK', 'e9WphB9xKXsBuAInJSkn', 'LTgcbVKb0YZVeL0GXiR6', 'P5MzGqQMmJVyCXiolOii', 'D9ROeHDCLPHDXyQ9PoZ5', '28a8PtI76w3cdgmfeENs', '1Umc0ZwhLfsuqfz1Oil2', 'KDACFaBDtj6y3NZ59Lit', '86YmKVxhv03WzgzdjGbu', '3FCAqFHUq6fBxEgEZjOF', 'n5H1Dg4K9vUNMnGPKnCQ', 'eyjbXRVzHI65IsH6BhpZ', 'Nvt5zBn7ttM0SIqfjr5D', '56cdvTHu3EqUzulb15TR', 'fDUjNKRCUG2TUUDsBpLX', 'P3H16jaGVzQC0brWRMza', '85QL9bnFzoj9TS6UrQEs', 'Db7B9jyR8pqClnhy21yq', '0vGvUVUS4MH9JGmOTqSY', '0ewhPmHPM1wirm7cFBsS', 'PADCrANwLbq0GZ6wncIg', 'C7n2rll8ysnUbO7a02x3', 'g8sIuQuYKm0DYE09yjiv', 'sdriwnfb0UuMSKQrRkSh', 'ehZzAQ2gfUXMiln9lGv4', 'dbofdb5P8R1ZnG5UcTZj', 'QuodrFo7UjHiQk5lnO6X', 'RoWUx80kOUoRTCZkoUM6', 'uSpslLKvUgFhgIgifRkz', 'cxKPKMJ4r01nEpOzRmXQ', '9zSY0jWDKWYOwaL8FNbD', 'svggWfJSWBlShiObPi6V', 'kwvbok7qy3nCnq7yfDH0', 'M5Ua8JyLYyIbb0QlDv3k', 'NL3X9JwsOgvWLOXYdr0t', 'DmNc0zrPrD4CVugZdwDx', 'zw4UbvBCdsd9XKy6e6sY', 'BMe3nx0WU13yCwOwvgsU', 'mZX8YYie9qB9hk5Qak6w', 'pjGsU27xCyNQBWDyCYg9', 'nt0NCFU9bAOl0XS1FQtS', 'C2bXnWfReCcN8RU7LeFC', 'AT54wnTPTK1YQpv9Izd1', 'udVrHRDK96kZOOGyCvru', 'm1kLpy2wD2KVWKxzBGm8', 'USwjpFF9xDRU4A5ax20Z', '1BuPModiOSUTkMnF6nhP', 'SpYFYXDMn26p1DPrmCV9', 'ceIjS2zjxSwXsjIlE7xN', 'kUaKBXkDsc334KB5LNl8', 'pWq2DuFrsjs0UehOZA1a', 'XuUDwD2vhbhnK933QcFE', 'taJTdcJ7IAoEbY3fii6i', 'uB3QJExmt4clnJERcDv7', 'c7MMlZ3uh49wPMb0lGiW', '8yM4EtyfMFRX6PO0sk2g', 's9VaWRAOHpX2WCDuhJbU', 'EECOMZYCRcoEKhrd3n9n', '08zWtZHnEuTJnmGGp72u', 'VgENkNxhBrGtpHpcenRX', 'fD7GAAKEoyQfXZLVo71x', 'LESSDwfBAU1Oa2Q9dFhR', 'FEBcW6myeQk014ZdfXJb', 'ZFtCOmuWHoWzoNbk6cSD', 'yP4Wet4uMiuqodaxRGzK', 'tDzpJ6fdW2rhAysDAg7u', 'u5mgFLzu7sQzVg7HNto0', 'JomASepnkB5YCPENFMRC', 'jziQHZBJcYsV0jB6m9wl', 't9ecksFBiOXvtqSEZJr7', 'pJa9C8GW7M8VAVuucr30', 'BqiKDljNrXBSup4mYnwQ', 'mXfllLSGVwWIcSDiiQ3u', 'KZ193i32iGgAD83wwncg', 'Xh0TW1czegQr6feog1LH', 'ogre0dZbT6rZgHEvMiKI', '8bLctlD0znJ7h9zqQirf', 'oY2lHmZsIHQJBmxkhXlB', '8UL9mp4YsSJjmfzZ1IhK', 'taMYx3JpcTOtel2b8SOi', 'K9gy0xwEOH5eTikWvUnK', 'aZPGyuqvOKUYjPBXWoFo', 'Rhmv4F6DYbX6a3SH84ZH', 'mcuEmQpTubaZyk4JrQZ1', '5m1eEMCinPBVjBi5vXFp', 'x8K0Sjl69vP24EGqJoEQ', 'ypCdXRelMXPsOr0EO7zJ', 'YmhiDYOomXP1WoDNjuyy', 'bjiwK65zxZIBUU6RIL1o', 'ioBkL3xwJZyW6ShRYDTM', '8QlwLNFpKSZPdd3XlvkD', 'CLCzGa2Qd4VPBk6GHzRY', 'QcALSX64YxLJ2ZO7hi7x', 'cKWwQ2f3sIzf6vkMeQFc', 'ANh7HRQjtFHU51VmnI5W', 'H3pTqY75XZt452522uQC', 'kC2MhIoxnZWBr6T4o16r', 'Jt45GFBKREWfSOcATCu9', 'KsJh8YkHeYEP7bV5uNah', 'yyLHRm6jMJgrEEncMTiO', 'Afeas0hQxG2vRibXJRkC', 'PM0oVDl5QpHuJGMbmd7U', 'DIV6HLqIchYJsoVMuWyI', 'HAIi3wvLZgAZkAmO1QUj', 'aJD45DyrKSkFhY8vUZfO', 'qtw75Kl8XBh36EmAhPcJ', 'XVZUBvrghqZMYB53g3Ie', 'WEhl3KkvjMZttnA4oVCJ', 'Kef6pFtDJnHkudYEj7u4', '9dc11wh6lcIE9jX08CQa', 'h9We6nh0JZr5AysQZNxQ', '4N69PovSMKMFmZ82gGng', 'V8mImbnGO9C4rzsHODVI', 'ssmJwMrMQ4Ivu521ulfm', 'tXmYBYfkgDpTNZol3bha', 'RUXGyKLXzHPItyllOLI9', '1jlEV1tIRE0LINMCBOU0', '2cjsR8Zsh0ar5UTChD0t', 'kBd4kbtvtga5S08xdbGX', 'Xj6uEbqZWaM3HsTDodaW', '5lexvd0x5AtDcMF7rDgb', 'kPlBc8YzJVbrwaO9yvUI', 'ofS3e9EmcfeiHHuJlGKX', 'fsvdCRiF9UJP1dcN5tlH', 'qrTz95cKmvGsje8upxhP', 'cDoXteaZnaU3YQW9vrq6', 'ETVrHgwqSxHHa2CkWw9j', 'SgKj5hAhs2o5Azxyu2ej', 'hOsRoOXqAdo7tqCkcUUP', 'rUXVUf3tXb1mbfqSuxlI', 'DTV5nyIAW4RZW3zO6Hyq', 'w39Pxqh7EFWxreTUhfeD', 'oQoELdohGfxPnxUkZpx2', 'gQXndLxvuqUao1P2YVr8', 'xYsmraPPmcZT4MqacaT7', 'FhDYaUhsHkBm7n5sy09c', 'yVJJK8DIngLO0Eu0lC3r', '4QcWNbclAAaXRZcrkZUo', 'biBB3JG7JCVbzaA3jZgH', 'NePRs1NNl75FkHGy7PRW', 'lAXfzu8e1BH0sHT9RYaU', '3laR70DUVY3XEFreh97k', 'H2uIcOinbXQ28HuFJjTr', '6SSOb6tk8hjzZ98rpY2K', 'iWzGPuC4U9dWfUSskKTl', 'iHvBfvs4S2nPa8hky8tJ', 'z33uLbXiYQUvEg4hci1v', 'IgANt0Gg98f0lwXDtiu3', 'CXLCUxQ8yZoWVSC81gOc', 'GSBPH7EJTgJ4GQCgUecR', 'hlfaNXsuhb54LIWDn2g6', '6guHneoELHip8ftARViw', '3iBNgazwLJ0Y4hkQh5P4', 'jCs7scOyKQp3pAKq0WDV', 'IRBuDGcHOgEkdXFOUugB', 'ESiyy3uhC1EI931xL1xl', 'twxrAIDccAihWioiWcUb', 'l8YpSxWWYUMcRjDBOwJT', 'foPEZsfw1PPFzwt7kBTr', '5kj7O4aBuVEdSKJKLOX5', 'RbPlyT72iZ4I1lNArOn3', 'lYHByBiUvQTKUJXo4Nor', 't5DZREqGMvpuGe10I0ld', 'jVcZpqXuBCwLg0osfX5y', 'zVMt8SqK08ZX2u9LvK2f', 'Q5ptcp2Vi91FXKb7bfon', 'X1546thPrum1AN2R5vsc', 'aTGRAb99PMTn64cK8ZRT', 'XYT17WvrtAKchjo4TvRC', 'bPY5FMhC5N0xNcj6WoMg', 'kgkKUcwT1uCUzJTp7QLB', 'o6EvNpj2iVE4nGWnN6H7', '3J5MwaVb2anK8otPrGDQ', '5a7sRKXiWhvF6MgE65aD', 'n7ofHirnfEueuVfSpuHh', 'FPBGH60wk82SWdeAXYqr', 'tHQMuFSsgZOcESZu4eyM', 'YGvAbLufaTVeuPRm5anI', 'CQbpfR8h9MsbCv1yiUYm', 'bvFIwZXmRUa1gzcmpXxk', 'moY8p1y9wFp3JBmNwF78', 'ojC5azlVJVaCzxrfcQd7', 'K7sv3pQxQwa4HCVaTIbv', '2xapBso1yMYKwybjOnSs', 'TyVvCsZkkiTGIMJXFlVX', 'lYtmof5MBObV8UyUQbZ3', 'DajbkxiiaMaWrz9IZTUx', 'X37FAQkbdIfJxbMxMZFZ', '3twVmX54wxuYVnrzSqS8', 'tWGTNfJd8dAyqhjUYOqi', 'hMmFfEcATqAs6HWihILj', 'TO0uOiUaju9nhUhxNuHU', '2WL0RlnpudsEF23A1Gbu', '1ff1U9QpTWD6cCOutsUz', 'ejDjDyI5iFxHqVbD3iaT', 'flH61FjRJk9ivYkRr6OZ', 'iI2uGAsecnDg6ItJ7lWs', 'igi9EOplyX1am6G4SjYO', 'N640p7LRbQBaIbsSKIfU', 'Dj2ufpcOweAUaMmkU3IY', 'kpP2TjaTMfZXO2qvmvJ1', 'OOdk2dJkKSSUSMXdps98', 'L1iY4MCKvcr1PQhSu3h4', 'ZKayXtEHjdt0DBtzl7E4', 'bKWwl4iBoFqubbuvbLLZ', '5utV7sKjzLhL5MnSy397', '1ImjThz1S5yXyioXMiO9', '9cIh8ZEshJvGS4A9P7LW', 'y4Yu932TyjU4bZADgrdy', 'wv4GxrXMHG6jc3akURXJ', 'UeeAaDyE3XFP5zWcZiJn', 'u3Ymb9k3QiZ7TED8RI6h', 'g72JUWdqH2Il7OCLOV52', 'owVtN9hR0vXpjYJLOHv4', 'gj0PN0kYFBfqDelKzrRA', 'CVILEr0ZOodXTIT7DT3Y', 'FLoQ50enDt9tPyoK8B51', 'P6XcejtNfMbQPOj1B4Hv', 'FJZdWMSgOwbjYq82jl1w', 'iqrlKnprKQ2rXCmaPXVO', 'ykBKbP7HHRf1m6NDgK3t', 'GDuODJIQp2pglU2n7bBA', 'MKNfwoTFOoEloRejjyWZ', 'ucroxAWT6OvB5chb4tDp', 'R6bkvmen4rmRn5T8ZYDx', 'yTIoJs7nkI7tycs9Ezer', 'rbpwxZX2nhaoh8mQ4tTT', 'bdJ8Pv7mcvMvOcihv1hA', 'ZJjOc5DgJQYs5KkTMkzY', '6qZ5VD2PtS65GKWLjxSv', 'FYj66OWxyzwMRcezJETO', '0vWg3Ppqdh5eBxrdPlE4', 'hybFU1DI2FYpVuwzYKFe', 't38JuOkyvtoeAPuvX7KZ', 'gsIPoSXhAL9OGAw5dgky', 'w1qcn4BPlzyxZKBSV7WH', 'aPu0JUmlDSAP44glwHmN', 'L3q6Xq4RFX9MxVyYZS6W', 'uweovBlVC0Re3JYyFM7h', 'omXrC2YSTHjbnlWj5BSN', 'QAtPJwFdnmjWTs1twJRD', 'rarAgYO3gv3nw3VnSFW8', 'FWT4TlpYPrKbPqfLqEXI', 'z1HlRyotra4GczlQCxrr', 'SRRQdqCMFRlrpCDmtYsg', '3Ucj2SVBgsLlFMtnS5Aw', '8ZSaDIs5vZL2FsMRwsu4', 'DoCTvBww1SZh2gstBB1i', 'YuttjZFMdFxim9Kdvm4Z', 'gYEyBfTDXCH6qJSzLS8P', 'VfgwBdyP7GcEoLaKkmWf', 'Sx5mvq0smizP9mxrePIB', 'sfDPCMcAioytlOwgFjgd', 'Luf6TmkJXBAHk8H9Job3', 'obS0ekdE4TYq0V3QBe7Y', 'xBUQbKd4e24lrfdXFTUp', 'B07P3SYSijw2oGp5rqHk', 'd3IbxjBIcivhfpqEJ3Wk', 'Hp43BhfZZ1h8lRplVhQl', 'xPXHbwhTKUBCJr4QiyRQ']
    print(len(ff))
    existing_ids = set(
    UserAppointment.objects.filter(appointment_id__in=today_appointments)
    .values_list('appointment_id', flat=True)
    )

    # Find new appointment IDs (not in DB)
    new_appointments = [appt_id for appt_id in today_appointments if appt_id not in existing_ids]

    print("New appointments not in DB:", new_appointments)




def fetch_xlsx_appointment(filepath):
    try:
        df = pd.read_excel(filepath)
        
    except Exception as e:
        print(f"Error reading Excel file: {e}")
        return None
    
    arr = []
    dict1 = dict()
    for column, row in df.iterrows():
        # print(row['Appointment Id'])
        arr.append(row["Appointment Id"])
        if row["Outcome"] not in dict1:
            dict1[row["Outcome"]] = 1
        else:
            dict1[row["Outcome"]] += 1


    print(dict1)

    existing_ids = set(
        UserAppointment.objects.all()
        .values_list('appointment_id', flat=True)
    )

    missing_from_arr = existing_ids - set(arr)

    UserAppointment.objects.filter(appointment_id__in = missing_from_arr).delete()
    print(len(missing_from_arr))
    print(missing_from_arr)