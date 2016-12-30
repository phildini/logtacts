import logging
from django.conf import settings
from django.contrib.sites.models import Site
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.utils import timezone

sentry = logging.getLogger("sentry")

def send_receipt(invoice, email):
    context = {
        'domain': Site.objects.get_current().domain,
        'invoice': invoice,
    }
    subject = "[ContactOtter] Receipt for payment to ContactOtter"
    txt = get_template('email/receipt.txt').render(context)
    html = get_template('email/receipt.html').render(context)
    try:
        message = EmailMultiAlternatives(
            subject=subject,
            body=txt,
            from_email="ContactOtter <help@contactotter.com>",
            to=[email],
        )
        message.attach_alternative(html, "text/html")
        message.send()
    except:
        sentry.exception('Problem sending receipt', extra={
            'invoice': invoice.id,
            'email': email,
        })
