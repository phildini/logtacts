import logging
from django.http import Http404
from gargoyle import gargoyle
from contacts.models import Book

sentry = logging.getLogger('sentry')

class ContactBookMiddleware(object):

    def process_view(self, request, view_func, view_args, view_kwargs):
        # CONTRACT: At the end of this, if the user is authenticated,
        # request.current_book _must_ be populated with a valid book, and 
        # request.books _must_ be a list of Books with length greater than 1.
        request.current_book = None
        if hasattr(request, 'user'):
            if request.user.is_authenticated():
                request.books = Book.objects.filter_for_user(request.user)
                request.current_book = None
                if request.books:
                    if 'book' in view_kwargs:
                        current_book = request.books.get(id=view_kwargs['book'])
                        if current_book:
                            request.current_book = current_book
                        else:
                            return Http404
                    else:
                        request.current_book = request.books[0]
                else:
                    sentry.error("No book found for user", exc_info=True,
                        extra={"user": user}
                    )
                    request.current_book = Book.objects.create_for_user(request.user)
                    request.books = Book.objects.filter_for_user(request.user)

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
