from accounts.models import Contact
from accounts.models import Opportunity
from django.utils.dateparse import parse_datetime


def create_or_update_contact(contact):
    custom_field_mapping = {
        "d8jLUuh4kGNu6iSGz3aE": "utm_source",
        "OrenZZfGUli2rL1CPlUN": "utm_traffic_type",
    }

    # Extract values from custom fields
    extracted_custom_fields = {}
    for field in contact.get("customFields", []):
        field_id = field.get("id")
        field_value = field.get("value")
        if field_id in custom_field_mapping:
            mapped_field = custom_field_mapping[field_id]
            extracted_custom_fields[mapped_field] = field_value


    Contact.objects.update_or_create(
            contact_id=contact.get("id"),
            defaults={
                "first_name": contact.get("firstName", "No Data"),
                "last_name": contact.get("lastName", "No Data"),
                "business_name": contact.get("companyName", "No Data"),
                "company_name": contact.get("companyName", "No Data"),
                "phone": contact.get("phone", "No Data"),
                "email": contact.get("email", "No Data"),
                "tags": ", ".join(contact.get("tags", [])),
                "utm_source": extracted_custom_fields.get("utm_source", "No Data"),
                "utm_medium": contact.get("attributionSource", {}).get("utmMedium", "No Data"),
                "utm_campaign": contact.get("attributionSource", {}).get("campaign", "No Data"),
                "utm_content": contact.get("attributionSource", {}).get("utmContent", "No Data"),
                "utm_term": contact.get("attributionSource", {}).get("medium", "No Data"),
                "utm_traffic_type": extracted_custom_fields.get("utm_traffic_type", "No Data"),
                "created": parse_datetime(contact.get("dateAdded")) if contact.get("dateAdded") else None,
            }
        )
    print("Contact created or updated successfully")



def create_opportunity(opportunity_data):

    source = opportunity_data.get("source")
    source = source.get("source", "No Data") if isinstance(source, dict) else (source or "No Data")
    opp_id = opportunity_data["id"]
    contact_id = opportunity_data["contactId"]
    full_name = opportunity_data.get("contact", {}).get("name", "No Data")
    email = opportunity_data.get("contact", {}).get("email", "No Data")
    phone = opportunity_data.get("contact", {}).get("phone", "No Data")
    tags = ", ".join(opportunity_data.get("contact", {}).get("tags", []))
    date_created = parse_datetime(opportunity_data.get("createdAt"))
    updated_on = parse_datetime(opportunity_data.get("updatedAt"))
    status = opportunity_data.get("status")
    lead_value = opportunity_data.get("monetaryValue")
    pipeline_stage_id = opportunity_data.get("pipelineStageId", "No Data")
    pipeline_id = opportunity_data.get("pipelineId", "No Data")
    assigned = opportunity_data.get("assignedTo", "No Data")
    opportunity_name = opportunity_data.get("name", "No Data")
    days_since_last_stage_change = opportunity_data.get("lastStageChangeAt")
    days_since_last_status_change = opportunity_data.get("lastStatusChangeAt")

    # Look up pipeline stage name
    pipeline_stage_name = "Unknown Stage"

    for stage in get_pipeline_stages()["stages"]:
        if stage["id"] == pipeline_stage_id:
            pipeline_stage_name = stage["name"]
            break

    # Create or update the opportunity in the database
    opportunity_obj = Opportunity.objects.create(
        opportunity_id=opp_id,
        contact_id=contact_id,
        full_name=full_name,
        email=email,
        phone=phone,
        tags=tags,
        date_created=date_created,
        pipeline_stage=pipeline_stage_name,
        pipeline_id=pipeline_id,
        pipeline_name="The Parks - Lead Stages",
        status=status,
        lead_value=lead_value,
        source=source,
        assigned=assigned,
        opportunity_name=opportunity_name,
        days_since_last_stage_change=days_since_last_stage_change,
        days_since_last_status_change=days_since_last_status_change,
        updated_on=updated_on,
        pipeline_stage_id=pipeline_stage_id,
    )

    print("Oppeortunity created successfully")

    return opportunity_obj



def update_opportunity(opportunity_data):
    source = opportunity_data.get("source")
    source = source.get("source", "No Data") if isinstance(source, dict) else (source or "No Data")

    opp_id = opportunity_data["id"]
    contact_id = opportunity_data["contactId"]
    full_name = opportunity_data.get("contact", {}).get("name", "No Data")
    email = opportunity_data.get("contact", {}).get("email", "No Data")
    phone = opportunity_data.get("contact", {}).get("phone", "No Data")
    tags = ", ".join(opportunity_data.get("contact", {}).get("tags", []))
    date_created = parse_datetime(opportunity_data.get("createdAt"))
    updated_on = parse_datetime(opportunity_data.get("updatedAt"))
    status = opportunity_data.get("status")
    lead_value = opportunity_data.get("monetaryValue")
    pipeline_stage_id = opportunity_data.get("pipelineStageId", "No Data")
    pipeline_id = opportunity_data.get("pipelineId", "No Data")
    assigned = opportunity_data.get("assignedTo", "No Data")
    opportunity_name = opportunity_data.get("name", "No Data")
    days_since_last_stage_change = opportunity_data.get("lastStageChangeAt")
    days_since_last_status_change = opportunity_data.get("lastStatusChangeAt")

    # Look up pipeline stage name
    pipeline_stage_name = "Unknown Stage"

    for stage in get_pipeline_stages()["stages"]:
        if stage["id"] == pipeline_stage_id:
            pipeline_stage_name = stage["name"]
            break

    # Create or update the opportunity in the database
    opportunity_obj = Opportunity.objects.filter(opportunity_id=opp_id).update(
    contact_id=contact_id,
    full_name=full_name,
    email=email,
    phone=phone,
    tags=tags,
    date_created=date_created,
    pipeline_stage=pipeline_stage_name,
    pipeline_id=pipeline_id,
    pipeline_name="The Parks - Lead Stages",
    status=status,
    lead_value=lead_value,
    source=source,
    assigned=assigned,
    opportunity_name=opportunity_name,
    days_since_last_stage_change=days_since_last_stage_change,
    days_since_last_status_change=days_since_last_status_change,
    updated_on=updated_on,
    pipeline_stage_id=pipeline_stage_id,
    )

    print("Oppeortunity udated successfully")

    return opportunity_obj




def get_pipeline_stages():
    
    pipeline_stages = { "stages": [
        {
          "id": "006ebfa2-6b99-4b65-9dfc-b0a71ded9af2",
          "name": "Initial Rental Interest",
        },
        {
          "id": "ffbcfd50-1e93-4a5a-a03b-5b62d6e918ba",
          "name": "Contact Made - Pending Scheduling",
        },
        {
          "id": "2bcc0452-6bec-447d-876f-50443ed8a061",
          "name": "Showing Booked",
        },
        {
          "id": "6ed1a81e-2e60-40cc-bdef-8f4ee3076136",
          "name": "Showing Complete",
        },
        {
          "id": "0aae281a-97e5-46ad-ab3e-e75298c91e0f",
          "name": "Pending Paperwork",
        },
        {
          "id": "639c5017-ecc0-4df8-b5d0-950689e4d03f",
          "name": "Negotiating",
        },
        {
          "id": "d40c4292-57c5-416f-a203-be8c2b14f8cd",
          "name": "Closed Won - New Tenant",
        },
        {
          "id": "c6ae532a-4254-4b0a-bade-b27e803b8f44",
          "name": "Closed Lost - ",
        }
      ]}
    
    return pipeline_stages




