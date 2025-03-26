from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
from accounts.models import Opportunity, Budget

@csrf_exempt
def webhook_handler_for_opportunity(request):
    if request.method == "POST":
        print("request.post triggered")
        try:
            data = json.loads(request.body)
            print("data: ", data)
            opportunity_id = data.get("id")
            
            opportunity, created = Opportunity.objects.update_or_create(
            opportunity_id=opportunity_id,
            defaults={
                "contact_id": data.get("contact_id", None),
                "full_name": data.get("full_name", None),
                "email": data.get("email", None),
                "phone": data.get("phone", None),
                "tags": data.get("tags", None),
                "date_created": data.get("date_created", None),
                "updated_on": data.get("updated_on", None),
                "opportunity_name": data.get("opportunity_name", None),
                "status": data.get("status", None),
                "lead_value": data.get("lead_value", None),
                "source": data.get("source", None),
                "pipeline_stage": data.get("pipeline_stage", None),
                "pipeline_stage_id": data.get("pipeline_stage_id", None),
                "pipeline_id": data.get("pipeline_id", None),
                "pipeline_name": data.get("pipeline_name", None),
                "assigned": data.get("assigned", None),
                "lost_reason_id": data.get("lost_reason_id", None),
                "lost_reason_name": data.get("lost_reason_name", None),
                "followers": data.get("followers", None),
                "notes": data.get("notes", None),
                "engagement_score": data.get("engagement_score", None),
                "days_since_last_stage_change": data.get("days_since_last_stage_change", None),
                "days_since_last_status_change": data.get("days_since_last_status_change", None),
                "days_since_last_updated": data.get("days_since_last_updated", None),
                "sq_ft": data.get("customData", {}).get("Sq. Ft.", None),
            }
            )
            
            message = "Opportunity updated successfully" if not created else "Opportunity created successfully"
            return JsonResponse({"message": message, "opportunity_id": opportunity.id}, status=201)
        
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON data"}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    
    return JsonResponse({"error": "Invalid request method"}, status=405)




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
