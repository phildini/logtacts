from django.apps import AppConfig


class InvitationConfig(AppConfig):
    name = 'invitations'

    def ready(self):
        import invitations.signals