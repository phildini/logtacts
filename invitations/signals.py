from django.contrib.auth.models import User
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Invitation


@receiver(post_save, sender=User)
def hold_account_on_signup(sender, instance=None, created=False, **kwargs):
    if created and not kwargs.get('raw'):
        if not (
            instance.email and Invitation.objects.filter(email=instance.email).exists()
        ):
            instance.is_active = False
            instance.save()