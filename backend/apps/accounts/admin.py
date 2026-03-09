from django.contrib import admin
from .models import User, UserProfile


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'firebase_uid', 'is_active', 'created_at']
    search_fields = ['username', 'email', 'firebase_uid']
    list_filter = ['is_active', 'created_at']


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'age_group', 'income_type', 'living_situation', 'food_provided']
    list_filter = ['age_group', 'income_type', 'living_situation']
