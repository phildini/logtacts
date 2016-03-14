import pytz

from django.utils import timezone
from django.utils.cache import patch_vary_headers


class TimezoneMiddleware(object):
    def process_request(self, request):
        timezone.activate(pytz.timezone('America/Los_Angeles'))


class DoNotTrackMiddleware(object):
    def process_response(self, request, response):
        patch_vary_headers(response, ('DNT',))
        return response