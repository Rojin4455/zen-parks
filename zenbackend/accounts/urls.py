from django.urls import path
from .views import *

urlpatterns = [
    path("webhook/", webhook_handler_for_opportunity),
    path("create-budget", budget_webhook_handler),
    path("auth/connect/", auth_connect, name="oauth_connect"),
    path("auth/tokens/", tokens, name="oauth_tokens"),
    path("auth/callback/", callback, name="oauth_callback"),
]