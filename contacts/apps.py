from django.apps import AppConfig


class ContactConfig(AppConfig):
    name = 'contacts'

    def ready(self):
        import contacts.signals
