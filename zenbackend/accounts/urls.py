from django.urls import path
from .views import *

urlpatterns = [
    # path('api/campaign-data/', fetch_campaign_data_by_day, name='campaign_data'),
    # path('api/campaign-data-full/', fetch_campaign_data, name='campaign_data'),
    # path('api/facebook-attribution/', fetch_facebook_attribution_data, name='facebook_attribution'),
    # path('api/get-appoinments/',scheduled_appointment_sync),
    # path('api/fetch/facebook/', fetch_campaigns_facebook),
    # path('api/fetch/google/', fetch_and_store_google_campaigns),
    path("webhook/", webhook_handler_for_opportunity),
    path("create-budget", budget_webhook_handler),
    path("auth/connect/", auth_connect, name="oauth_connect"),
    path("auth/tokens/", tokens, name="oauth_tokens"),
    path("auth/callback/", callback, name="oauth_callback"),
]
