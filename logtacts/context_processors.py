from django.conf import settings

def donottrack(request):
    return {
        'donottrack': request.META.get('HTTP_DNT') == '1'
    }

def selected_settings(request):
    return {
        'ENVIRONMENT': settings.ENVIRONMENT,
    }