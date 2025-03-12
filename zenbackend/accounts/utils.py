import requests
from decouple import config
from accounts.serializers import FirebaseTokenSerializer, LeadConnectorAuthSerializer, IdentityToolkitAuthSerializer
from accounts.models import FirebaseToken, LeadConnectorAuth, IdentityToolkitAuth, CallReport, FacebookCampaign, Appointment, GoogleCampaign


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
                print("Token generation failed. Aborting request.")
                return

            
        else:
            print(f"Failed to fetch data for {start_date}: {response.status_code} - {response.text}")








def fetch_latest_appointments(retry_count=0):
    from datetime import datetime, timedelta
    import time

    MAX_RETRIES = 1


    """
    Fetches all appointments for the past year by handling pagination
    and saves them to the database.
    """
    # API endpoint

    token = IdentityToolkitAuth.objects.first()
    if not token:
        token_generation_step1()
        fetch_latest_appointments()
        return
    url = "https://backend.leadconnectorhq.com/reporting/dashboards/automations/appointments"

    headers = {
        "Token-id": f"{token.id_token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Source": "WEB_USER",
        "Channel": "APP",
        "Version": "2021-04-15"
    }
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=1)
    
    # Convert to millisecond timestamps
    start_timestamp = int(start_date.timestamp() * 1000)
    end_timestamp = int(end_date.timestamp() * 1000)
    
    params = {
        "locationId": "Xtj525Qgufukym5vtwbZ"
    }
    
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
    
    total_appointments = 0
    total_pages = 0
    
    current_page = 1
    has_more_data = True
    
    while has_more_data:
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
                            "value": [start_timestamp, end_timestamp]
                        }
                    ]
                },
                "tableProperties": {
                    "columns": columns,
                    "order": "desc",
                    "orderBy": "dateAdded",
                    "limit": 50,
                    "page": current_page
                },
                "timezone": "America/Edmonton"
            }
        }
        
        try:
            response = requests.post(url, params=params, headers=headers, json=payload)
            if response.status_code == 201 or response.status_code == 200:
                data = response.json()
                
                if 'data' in data:
                    appointments = data['data']
                    appointments_count = len(appointments)
                    
                    if appointments_count == 0:
                        has_more_data = False
                    else:
                        save_appointments_from_api_data(appointments)
                        
                        total_appointments += appointments_count
                        total_pages += 1
                        
                        current_page += 1
                        
                        time.sleep(0.5)
                else:
                    has_more_data = False
            elif response.status_code == 401:
                if retry_count < MAX_RETRIES:
                        print(f"401 Unauthorized. Retrying... (Attempt {retry_count + 1})")
                        if token_generation_step1():
                            fetch_latest_appointments(retry_count + 1)
                            return

            else:
                # Request failed
                print(f"Request failed with status code: {response.status_code}")
                print(f"Response: {response.text}")
                has_more_data = False
                
        except Exception as e:
            print(f"Error fetching appointments data: {str(e)}")
            has_more_data = False
    
    return {
        "total_appointments": total_appointments,
        "total_pages": total_pages
    }

def save_appointments_from_api_data(data):

    from datetime import datetime

    for item in data:
        # Parse the timestamp from the sort field
        sort_timestamp = item['sort'][0] if 'sort' in item and len(item['sort']) > 0 else None
        sort_id = item['sort'][1] if 'sort' in item and len(item['sort']) > 1 else None
        
        try:
            from django.utils.timezone import make_aware

            start_time = make_aware(datetime.strptime(item.get('startTime', ''), '%b %d %Y %I:%M %p')) if item.get('startTime') else None
            date_added = make_aware(datetime.strptime(item.get('dateAdded', ''), '%b %d %Y %I:%M %p')) if item.get('dateAdded') else None

            
            Appointment.objects.update_or_create(
                id=item['id'],
                defaults={
                    'contact_name': item.get('contactName', ''),
                    'appointment_status': item.get('appointmentStatus', ''),
                    'title': item.get('title', ''),
                    'start_time': start_time,
                    'date_added': date_added,
                    'calendar_name': item.get('calendarName', ''),
                    'assigned_to': item.get('assignedTo', ''),
                    'contact_id': item.get('contactId', ''),
                    'sort_timestamp': sort_timestamp,
                    'sort_id': sort_id,
                    'source': item.get('source', ''),
                    'created_by': item.get('createdBy', ''),
                    'mode': item.get('mode', '') or item.get('reportingSource', ''),
                    'phone': item.get('phone', ''),
                    'email': item.get('email', ''),
                    'appointment_owner': item.get('appointmentOwner', '') or item.get('assignedTo', '')
                }
            )
        except Exception as e:
            print(f"Error saving appointment {item.get('id', 'unknown')}: {str(e)}")
            continue
    print("appointments created successfully")






def scheduled_appointment_sync():
    """
    Function to be scheduled daily to sync appointment data
    """
    try:
        result = fetch_latest_appointments()
        print(f"Successfully fetched {result['total_appointments']} appointments from {result['total_pages']} pages")
        return True
    except Exception as e:
        print(f"Error in scheduled appointment sync: {str(e)}")
        return False
    





def fetch_and_store_google_campaigns():
    url = "https://python-backend-dot-highlevel-backend.appspot.com/1.1/reporting/g/Xtj525Qgufukym5vtwbZ/campaigns"
    headers = {
        "Authorization": "Bearer 59b0a2e7-bea0-4880-9bb0-c1aaffc67600",
        "Accept": "application/json",
    }
    import datetime
    today = datetime.date.today()
    start_date = today - datetime.timedelta(days=1)

    for i in range(2):
        print(i)
        current_date = start_date + datetime.timedelta(days=i)
        formatted_date = current_date.strftime("%Y-%m-%d")

        params = {"start": formatted_date, "end": formatted_date, "sample": "false"}
        response = requests.get(url, headers=headers, params=params)

        if response.status_code == 200:
            data = response.json()
            for campaign_data in data.get("campaigns", []):
                campaign = campaign_data["campaign"]
                metrics = campaign_data["metrics"]

                GoogleCampaign.objects.update_or_create(
                    campaign_id=campaign["id"],
                    date=current_date,
                    defaults={
                        "campaign_name": campaign["name"],
                        "currency_code": campaign_data["customer"]["currencyCode"],
                        "status": campaign["status"],
                        "impressions": int(metrics["impressions"]),
                        "clicks": int(metrics.get("clicks",0)),
                        "interactions": int(metrics.get("interactions",0)),
                        "conversions": float(metrics.get("conversions",0)),
                        "cost_micros": int(metrics.get("costMicros",0)),
                        "cost_per_conversion": float(metrics.get("costPerConversion", 0)),
                        "ctr": float(metrics.get("ctr",0)),
                        "avg_cpc": float(metrics.get("averageCpc",0)),
                        "conversion_rate": float(metrics.get("conversionsFromInteractionsRate",0)),
                        "view_through_conversions": int(metrics.get("viewThroughConversions",0)),
                    }
                )
            print("google campaigns data created")


    print("Last days data fetched & stored successfully!")
    return 