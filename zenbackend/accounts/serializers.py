from rest_framework import serializers
from .models import FirebaseToken, LeadConnectorAuth, IdentityToolkitAuth

class FirebaseTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = FirebaseToken
        fields = '__all__'


class LeadConnectorAuthSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeadConnectorAuth
        fields = '__all__'

class IdentityToolkitAuthSerializer(serializers.ModelSerializer):
    class Meta:
        model = IdentityToolkitAuth
        fields = '__all__'
