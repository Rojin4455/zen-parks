from django.contrib import admin
from accounts.models import GoogleCampaign, Appointment, Opportunity

admin.site.register(Appointment)
admin.site.register(GoogleCampaign)
admin.site.register(Opportunity)
