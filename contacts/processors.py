def book(request):
    return {'book': request.current_book}