"""
PocketSense — Web Frontend URL Configuration
All server-side rendered pages.
"""

from django.urls import path
from pocketsense.web_views import (
    login_view, register_view, logout_view,
    dashboard_view,
    transactions_view, add_expense_view, add_income_view, delete_transaction_view,
    wallet_view,
    savings_view, savings_create_view, savings_deposit_view,
    budgets_view, budget_create_view,
    analytics_view,
    settings_view,
    export_csv_view,
)

app_name = 'web'

urlpatterns = [
    # Auth
    path('login/', login_view, name='login'),
    path('register/', register_view, name='register'),
    path('logout/', logout_view, name='logout'),

    # Dashboard
    path('', dashboard_view, name='dashboard'),

    # Transactions
    path('transactions/', transactions_view, name='transactions'),
    path('add-expense/', add_expense_view, name='add_expense'),
    path('add-income/', add_income_view, name='add_income'),
    path('transactions/<uuid:pk>/delete/', delete_transaction_view, name='delete_transaction'),

    # Wallet
    path('wallet/', wallet_view, name='wallet'),

    # Savings
    path('savings/', savings_view, name='savings'),
    path('savings/create/', savings_create_view, name='savings_create'),
    path('savings/<uuid:pk>/deposit/', savings_deposit_view, name='savings_deposit'),

    # Budgets
    path('budgets/', budgets_view, name='budgets'),
    path('budgets/create/', budget_create_view, name='budget_create'),

    # Analytics
    path('analytics/', analytics_view, name='analytics'),

    # Settings
    path('settings/', settings_view, name='settings'),

    # Export
    path('export/csv/', export_csv_view, name='export_csv'),
]
