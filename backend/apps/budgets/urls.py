from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('budgets', views.BudgetViewSet, basename='budget')
router.register('savings', views.SavingsGoalViewSet, basename='savings')

urlpatterns = [
    path('', include(router.urls)),
]
