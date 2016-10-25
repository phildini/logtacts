import logging
from django.http import Http404
from gargoyle import gargoyle
from contacts.models import Book

logger = logging.getLogger('sentry')

class ContactBookMiddleware(object):

    def process_view(self, request, view_func, view_args, view_kwargs):

        if hasattr(request, 'user'):
            if request.user.is_authenticated():
                books = Book.objects.filter_for_user(request.user)
                request.current_book = None
                if gargoyle.is_active('multi_book', request):
                    request.books = books
                    request.current_book = books[0]
                    if 'book' in view_kwargs:
                        current_book = request.books.filter(id=view_kwargs['book'])
                        if current_book:
                            request.current_book = current_book
                        else:
                            return Http404
                else:
                    if books:
                        request.current_book = books[0]
                    else:
                        request.current_book = None
                        logger.error(
                            "No book for user: {}".format(request.user),
                            exc_info=True,
                        )
                if (
                    gargoyle.is_active('enable_payments', request) and
                    request.current_book
                ):
                    request.can_invite = (
                        request.current_book.plan and not
                        request.current_book.plan.startswith('basic')
                    )
                else:
                    request.can_invite = True
