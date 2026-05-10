from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('categories', views.CategoryViewSet, basename='category')
router.register('transactions', views.TransactionViewSet, basename='transaction')
router.register('income-sources', views.IncomeSourceViewSet, basename='income-source')
router.register('patterns', views.RecurringPatternViewSet, basename='pattern')

urlpatterns = [
    path('', include(router.urls)),
]
