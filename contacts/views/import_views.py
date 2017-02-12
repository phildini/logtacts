import httplib2
import logging

from allauth.socialaccount.models import SocialToken, SocialApp
from apiclient.discovery import build
from braces.views import LoginRequiredMixin
from channels import Channel
from gargoyle import gargoyle
from googleapiclient.errors import HttpError
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.views.generic import View
from oauth2client.client import (
    HttpAccessTokenRefreshError,
    GoogleCredentials,
)
from oauth2client import GOOGLE_TOKEN_URI

from contacts.models import Book

sentry = logging.getLogger('sentry')


class GoogleImportView(LoginRequiredMixin, View):

    def dispatch(self, request, *args, **kwargs):
        if not gargoyle.is_active('import_from_google', request):
            return HttpResponseRedirect('/')
        app = SocialApp.objects.filter(provider='google')[0]
        url = "{}?process=connect&next={}".format(
            reverse("google_login"), reverse("import-google-contacts", kwargs={'book': self.request.current_book.id}),
        )
        try:
            token = SocialToken.objects.get(account__user=self.request.user, app=app)
        except SocialToken.DoesNotExist:
            sentry.error("Social token missing in google import", extra={
                "user": self.request.user,
            })
            return HttpResponseRedirect(url)
        try:
            creds = GoogleCredentials(
                access_token=token.token,
                token_expiry=None,
                token_uri=GOOGLE_TOKEN_URI,
                client_id=app.client_id,
                client_secret=app.secret,
                refresh_token=None,
                user_agent='Python',
                revoke_uri=None,
            )
            http = httplib2.Http()
            http = creds.authorize(http)
            people_service = build(serviceName='people', version='v1', http=http)
            connections = people_service.people().connections().list(resourceName='people/me', pageSize=50).execute()
        except HttpAccessTokenRefreshError:
            return HttpResponseRedirect(url)
        cache.set("{}::google-import".format(request.user.username), "processing", 86400)
        Channel('import-google-contacts').send({
            'user_id': self.request.user.id,
            'book_id': self.request.current_book.id
        })
        messages.success(request, "We're importing your Google contacts now! You'll receive an email when we're done.")
        return HttpResponseRedirect('/')
