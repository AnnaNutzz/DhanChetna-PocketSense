from django.urls import path
from . import views

urlpatterns = [
    path('advice/', views.get_advice, name='get-advice'),
]
