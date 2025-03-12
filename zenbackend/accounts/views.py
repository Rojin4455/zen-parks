from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
from accounts.models import Opportunity, Budget

@csrf_exempt
def webhook_handler_for_opportunity(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
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
                    "opportunity_name": data.get("opportunity_name", None),
                    "status": data.get("status", None),
                    "lead_value": data.get("lead_value", None),
                    "source": data.get("source", None),
                    "pipeline_stage": data.get("pipleline_stage", None),
                    "pipeline_id": data.get("pipeline_id", None),
                    "pipeline_name": data.get("pipeline_name", None),
                    "location_name": data.get("location", {}).get("name", None),
                    "location_id": data.get("location", {}).get("id", None),
                    "sq_ft": data.get("customData", {}).get("Sq. Ft.", None)
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
