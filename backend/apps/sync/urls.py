from django.urls import path
from . import views

urlpatterns = [
    path('sync/push/', views.sync_push, name='sync-push'),
    path('sync/pull/', views.sync_pull, name='sync-pull'),
]
