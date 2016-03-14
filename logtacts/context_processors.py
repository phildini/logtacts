def donottrack(request):
    return {
        'donottrack': request.META.get('HTTP_DNT') == '1'
    }