from django.apps import AppConfig

class AutoBidConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'auto_bid'
    def ready(self):
        import auto_bid.signals  # Ensure this line is present