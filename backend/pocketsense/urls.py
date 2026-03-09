"""
PocketSense — Main URL Configuration
Web frontend at root, API endpoints at /api/v1/
"""

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),

    # API v1 endpoints (for Tkinter, Kivy, and external clients)
    path('api/v1/auth/', include('apps.accounts.urls')),
    path('api/v1/', include('apps.transactions.urls')),
    path('api/v1/', include('apps.budgets.urls')),
    path('api/v1/', include('apps.analytics.urls')),
    path('api/v1/', include('apps.advice.urls')),
    path('api/v1/', include('apps.sync.urls')),

    # Web frontend (server-side rendered)
    path('', include('pocketsense.web_urls')),
]
