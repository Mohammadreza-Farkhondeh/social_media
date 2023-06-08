from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Profile


# A serializer class for the Profile model
class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ('first_name', 'last_name', 'url', 'profile_info', 'created', 'avatar.path')


# A serializer class for the User model
class UserSerializer(serializers.ModelSerializer):
    # A nested serializer for the profile field
    profile = ProfileSerializer(required=True)
    class Meta:
        model = User
        fields = ('url', 'email', 'profile', 'created')
