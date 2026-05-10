from django.apps import AppConfig


class AdviceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.advice'
    label = 'advice'
    verbose_name = 'AI Advice Engine'
