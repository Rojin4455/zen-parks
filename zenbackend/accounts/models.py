from django.db import models

from django.db import models

class Appointment(models.Model):
    id = models.CharField(primary_key=True, max_length=100)
    contact_name = models.CharField(max_length=255)
    appointment_status = models.CharField(max_length=50)
    title = models.CharField(max_length=255)
    start_time = models.DateTimeField()
    date_added = models.DateTimeField()
    calendar_name = models.CharField(max_length=255)
    assigned_to = models.CharField(max_length=255)
    contact_id = models.CharField(max_length=100)
    sort_timestamp = models.BigIntegerField(null=True, blank=True)
    sort_id = models.CharField(max_length=100, null=True, blank=True)
    source = models.CharField(max_length=100, null=True, blank=True)
    created_by = models.CharField(max_length=255, null=True, blank=True)
    mode = models.CharField(max_length=50, null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    appointment_owner = models.CharField(max_length=255, null=True, blank=True)
    
    class Meta:
        db_table = 'appointments'
        ordering = ['-sort_timestamp']
    
    def __str__(self):
        return f"{self.contact_name} - {self.start_time}"
    



class FacebookCampaign(models.Model):
    account_currency = models.CharField(max_length=10)
    campaign_id = models.CharField(max_length=50, unique=True)
    campaign_name = models.CharField(max_length=255)
    impressions = models.IntegerField()
    clicks = models.IntegerField()
    cpc = models.DecimalField(max_digits=10, decimal_places=2)
    ctr = models.DecimalField(max_digits=5, decimal_places=2)
    spend = models.DecimalField(max_digits=10, decimal_places=2)
    date_start = models.DateField()
    date_stop = models.DateField()
    account_id = models.CharField(max_length=50)
    conversions = models.IntegerField()
    cost_per_conversion = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = 'facebookcampaign'

    def __str__(self):
        return f"{self.campaign_name} ({self.campaign_id})"
    


class GoogleCampaign(models.Model):
    customer_resource_name = models.CharField(max_length=255)
    currency_code = models.CharField(max_length=10)
    campaign_resource_name = models.CharField(max_length=255)
    campaign_id = models.CharField(max_length=50)
    campaign_name = models.CharField(max_length=255)
    status = models.CharField(max_length=50)
    date = models.DateField()
    clicks = models.IntegerField()
    impressions = models.IntegerField()
    interactions = models.IntegerField()
    conversions = models.FloatField()
    cost_micros = models.BigIntegerField()
    cost_per_conversion = models.FloatField(null=True, blank=True)
    ctr = models.FloatField()
    avg_cpc = models.FloatField()
    conversion_rate = models.FloatField()
    view_through_conversions = models.IntegerField()

    class Meta:
        db_table = 'googlecampaign'

    def __str__(self):
        return self.campaign_name




from django.db import models

class CallReport(models.Model):
    id = models.CharField(max_length=50, primary_key=True)
    account_sid = models.CharField(max_length=50, blank=True, null=True)
    assigned_to = models.CharField(max_length=50, blank=True, null=True)
    call_sid = models.CharField(max_length=50, blank=True, null=True)
    call_status = models.CharField(max_length=20, blank=True, null=True)
    called = models.CharField(max_length=20, blank=True, null=True)
    called_city = models.CharField(max_length=50, blank=True, null=True)
    called_country = models.CharField(max_length=10, blank=True, null=True)
    called_state = models.CharField(max_length=10, blank=True, null=True)
    called_zip = models.CharField(max_length=10, blank=True, null=True)
    caller = models.CharField(max_length=20, blank=True, null=True)
    caller_city = models.CharField(max_length=50, blank=True, null=True)
    caller_country = models.CharField(max_length=10, blank=True, null=True)
    caller_state = models.CharField(max_length=10, blank=True, null=True)
    caller_zip = models.CharField(max_length=10, blank=True, null=True)
    contact_id = models.CharField(max_length=50, blank=True, null=True)
    date_added = models.DateTimeField(blank=True, null=True)
    date_updated = models.DateTimeField(blank=True, null=True)
    deleted = models.BooleanField(default=False)
    direction = models.CharField(max_length=10, blank=True, null=True)
    from_number = models.CharField(max_length=20, blank=True, null=True)
    from_city = models.CharField(max_length=50, blank=True, null=True)
    from_country = models.CharField(max_length=10, blank=True, null=True)
    from_state = models.CharField(max_length=10, blank=True, null=True)
    from_zip = models.CharField(max_length=10, blank=True, null=True)
    location_id = models.CharField(max_length=50, blank=True, null=True)
    message_id = models.CharField(max_length=50, blank=True, null=True)
    to_number = models.CharField(max_length=20, blank=True, null=True)
    to_city = models.CharField(max_length=50, blank=True, null=True)
    to_country = models.CharField(max_length=10, blank=True, null=True)
    to_state = models.CharField(max_length=10, blank=True, null=True)
    to_zip = models.CharField(max_length=10, blank=True, null=True)
    user_id = models.CharField(max_length=50, blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    duration = models.IntegerField(blank=True, null=True)
    first_time = models.BooleanField(default=False)
    recording_url = models.URLField(blank=True, null=True)

    class Meta:
        db_table = 'callreport'

    def __str__(self):
        return f"Call {self.call_sid} - {self.call_status}"
    

class FirebaseToken(models.Model):
    access_token = models.TextField()
    expires_in = models.IntegerField()
    token_type = models.CharField(max_length=50)
    refresh_token = models.TextField()
    id_token = models.TextField()
    user_id = models.CharField(max_length=100)
    project_id = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)


class LeadConnectorAuth(models.Model):
    token = models.TextField()
    trace_id = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

class IdentityToolkitAuth(models.Model):
    kind = models.CharField(max_length=100)
    id_token = models.TextField()
    refresh_token = models.TextField()
    expires_in = models.IntegerField()
    is_new_user = models.BooleanField()
    created_at = models.DateTimeField(auto_now_add=True)







class Opportunity(models.Model):
    contact_id = models.CharField(max_length=255, null=True, blank=True)
    date_created = models.DateTimeField(null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    full_name = models.CharField(max_length=255, null=True, blank=True)
    opportunity_name = models.CharField(max_length=255, null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    pipeline_name = models.CharField(max_length=255, null=True, blank=True)
    pipeline_stage = models.CharField(max_length=255, null=True, blank=True)
    lead_value = models.IntegerField(null=True, blank=True)
    source = models.CharField(max_length=255, null=True, blank=True)
    assigned = models.CharField(max_length=255, null=True, blank=True)
    updated_on = models.DateTimeField(null=True, blank=True)
    lost_reason_id = models.CharField(max_length=255, null=True, blank=True)
    lost_reason_name = models.CharField(max_length=255, null=True, blank=True)
    followers = models.TextField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    tags = models.CharField(max_length=255, null=True, blank=True)
    engagement_score = models.IntegerField(null=True, blank=True)
    status = models.CharField(max_length=50, null=True, blank=True)
    sq_ft = models.CharField(max_length=50, null=True, blank=True)
    opportunity_id = models.CharField(max_length=255, null=True, blank=True)
    pipeline_stage_id = models.CharField(max_length=255, null=True, blank=True)
    pipeline_id = models.CharField(max_length=255, null=True, blank=True)
    days_since_last_stage_change = models.CharField(max_length=50, null=True, blank=True)
    days_since_last_status_change = models.CharField(max_length=50, null=True, blank=True)
    days_since_last_updated = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return self.full_name or "Unnamed Opportunity"

    

class Budget(models.Model):
    budgeted_sq_ft = models.IntegerField(null=True, blank=True)
    budget_date = models.DateField(null=True, blank=True)
    budgeted_revenue = models.IntegerField(null=True, blank=True)
    location_name = models.CharField(max_length=255, null=True, blank=True)
    location_id = models.CharField(max_length=255, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Budget for {self.location_name or 'Unknown Location'}"



class Contact(models.Model):
    contact_id = models.CharField(max_length=50, unique=True)
    first_name = models.CharField(max_length=255, blank=True, null=True)
    last_name = models.CharField(max_length=255, blank=True, null=True)
    business_name = models.CharField(max_length=255, blank=True, null=True)
    company_name = models.CharField(max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    created = models.DateTimeField(blank=True, null=True)
    tags = models.TextField(blank=True, null=True)
    utm_source = models.CharField(max_length=255, blank=True, null=True)
    utm_medium = models.CharField(max_length=255, blank=True, null=True)
    utm_campaign = models.CharField(max_length=255, blank=True, null=True)
    utm_content = models.CharField(max_length=255, blank=True, null=True)
    utm_term = models.CharField(max_length=255, blank=True, null=True)
    utm_traffic_type = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.first_name if self.first_name else "Unnamed Contact"



class GoogleCampaignTotal(models.Model):
    all_conversions = models.FloatField(null=True, blank=True)
    avg_cpc = models.FloatField(null=True, blank=True)
    clicks = models.IntegerField(null=True, blank=True)
    date = models.DateField()
    conversion_rate = models.FloatField(null=True, blank=True)
    conversions = models.IntegerField(null=True, blank=True)
    cost = models.FloatField(null=True, blank=True)
    cost_per_conversion = models.FloatField(null=True, blank=True)
    impressions = models.IntegerField(null=True, blank=True)
    interactions = models.IntegerField(null=True, blank=True)
    view_through_conversions = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = 'googlecampaigntotal'
    
    def __str__(self):
        return f"Campaign Total - Clicks: {self.clicks}, Conversions: {self.conversions}"
    


class UserAppointment(models.Model):
    appointment_id = models.CharField(max_length=50)
    contact_name = models.CharField(max_length=255, null=True, blank=True)
    appointment_status = models.CharField(max_length=50, null=True, blank=True)
    title = models.CharField(max_length=255, null=True, blank=True)
    start_time = models.CharField(max_length=50, null=True, blank=True)
    date_added = models.CharField(max_length=50, null=True, blank=True)
    calendar_name = models.CharField(max_length=255, null=True, blank=True)
    assigned_to = models.CharField(max_length=255, null=True, blank=True)
    contact_id = models.CharField(max_length=50, null=True, blank=True)
    sort = models.JSONField(null=True, blank=True)
    source = models.CharField(max_length=100, null=True, blank=True)
    created_by = models.CharField(max_length=100, null=True, blank=True)
    mode = models.CharField(max_length=50, null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    email = models.EmailField(max_length=255, null=True, blank=True)
    appointment_owner = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        db_table = 'userappointment'

    def __str__(self):
        return f"{self.contact_name} - {self.title}"



class GHLAuthCredentials(models.Model):
    user_id = models.CharField(max_length=255, unique=True)
    access_token = models.TextField()
    refresh_token = models.TextField()
    expires_in = models.IntegerField()
    scope = models.CharField(max_length=500, null=True, blank=True)
    user_type = models.CharField(max_length=50, null=True, blank=True)
    company_id = models.CharField(max_length=255, null=True, blank=True)
    location_id = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"{self.user_id} - {self.company_id}"