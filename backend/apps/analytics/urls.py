from django.urls import path
from . import views

urlpatterns = [
    path('summary/', views.dashboard_summary, name='dashboard-summary'),
    path('analytics/category-split/', views.category_split, name='category-split'),
    path('analytics/weekly/', views.weekly_trend, name='weekly-trend'),
]
