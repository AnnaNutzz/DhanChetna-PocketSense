from django.urls import path
from . import views

urlpatterns = [
    path('verify/', views.verify_token, name='auth-verify'),
    path('profile/', views.ProfileView.as_view(), name='auth-profile'),
]
