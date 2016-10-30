import csv
import logging
from django.core.mail import EmailMessage
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone


logger = logging.getLogger('scripts')


class Command(BaseCommand):
    help = "Export users, names, and email addresses as CSV"

    def handle(self, *args, **kwargs):
        date_string = timezone.now().strftime("%Y_%m_%d")
        with open("co_users_{}.csv".format(date_string), 'w') as csvfile:
            writer = csv.writer(csvfile)
            for user in User.objects.all():
                writer.writerow([user.email, user.username, user.first_name, user.last_name])
        with open("co_users_{}.csv".format(date_string), 'r') as csvfile:
            message = EmailMessage(
                'CO Users',
                'See attached',
                'site@contactotter.com',
                ['philip@inkpebble.com'],
            )
            message.attach("co_users_{}.csv".format(date_string), csvfile.read(), 'text/csv')
            message.send()
