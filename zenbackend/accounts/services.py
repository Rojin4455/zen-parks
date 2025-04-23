import requests
from accounts.models import GHLAuthCredentials
def get_ghl_contact(contactId, access_token):

    url = f"https://services.leadconnectorhq.com/contacts/{contactId}"
    
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {access_token}",
        "Version": "2021-07-28"
    }
    
    response = requests.get(url, headers=headers)

    
    if response.status_code == 200:
        return response.json()
    else:
        
        return {"error": response.status_code, "message": response.text}
    
def get_ghl_opportunity(oppertunity_id, access_token):
    url = f"https://services.leadconnectorhq.com/opportunities/{oppertunity_id}"
    
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {access_token}",
        "Version": "2021-07-28"
    }
    
    response = requests.get(url, headers=headers)

    print("response: ", response.json())
    
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": response.status_code, "message": response.text}
    

def get_ghl_appointment(oppertunity_id, access_token):
    url = f"https://services.leadconnectorhq.com/opportunities/{oppertunity_id}"
    
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {access_token}",
        "Version": "2021-07-28"
    }
    
    response = requests.get(url, headers=headers)

    print("response: ", response.json())
    
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": response.status_code, "message": response.text}
    



def fetch_calendar_data(appointment_id):
    access_token = GHLAuthCredentials.objects.first().access_token
    url = f"https://services.leadconnectorhq.com/calendars/{appointment_id}"
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {access_token}",
        "Version": "2021-04-15"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        if data['calendar']:
            return data['calendar'].get("name")
        else:
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error fetching calendar data: {e}")
        return None