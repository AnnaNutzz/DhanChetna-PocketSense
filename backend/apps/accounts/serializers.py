"""Accounts app — Serializers for User and UserProfile."""

from rest_framework import serializers
from .models import User, UserProfile


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = [
            'age_group', 'income_type', 'income_frequency',
            'income_amount', 'living_situation', 'food_provided',
            'currency', 'theme_preference', 'onboarding_complete',
        ]


class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'profile']
        read_only_fields = ['id', 'email']
