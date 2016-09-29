from django.http import Http404
from gargoyle import gargoyle
from contacts.models import Book

class ContactBookMiddleware(object):

    def process_view(self, request, view_func, view_args, view_kwargs):

        if gargoyle.is_active('multi_book', request):
            if hasattr(request, 'user'):
                if request.user.is_authenticated:
                    request.books = Book.objects.filter_for_user(request.user)
                if 'book' in view_kwargs:
                    current_book = request.books.filter(id=view_kwargs['book'])
                    if current_book:
                        request.current_book = current_book
                    else:
                        return Http404

