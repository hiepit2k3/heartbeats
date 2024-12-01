from rest_framework import serializers
from .models import User, Authenticator

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

class AuthenticatorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Authenticator
        fields = '__all__'
