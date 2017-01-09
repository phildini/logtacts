def book(request):
    if hasattr(request, 'current_book'):
        return {'book': request.current_book}
    return {'book': None }