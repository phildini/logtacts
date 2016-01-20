from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import LogEntry


@receiver(post_save, sender=LogEntry)
def log_last_contact(sender, **kwargs):
    instance = kwargs.get('instance')
    if not kwargs.get('raw') and instance and instance.kind != 'edit':
        time = instance.created
        if instance.time:
            time = instance.time
        if instance.contact.last_contact and time > instance.contact.last_contact:
            instance.contact.last_contact = time
            instance.contact.save()
        if not instance.contact.last_contact:
            instance.contact.last_contact = time
            instance.contact.save()
