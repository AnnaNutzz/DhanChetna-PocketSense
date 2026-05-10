from django.urls import path
from . import views

urlpatterns = [
    path('advice/', views.get_advice_view, name='get-advice'),
]
