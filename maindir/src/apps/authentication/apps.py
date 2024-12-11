from django.apps import AppConfig

class AuthenticationConfig(AppConfig):
    name = 'authentication'

    def ready(self):
        import apps.authentication.signals