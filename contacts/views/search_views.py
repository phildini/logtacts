from braces.views import LoginRequiredMixin
from django.conf import settings
from django.http import Http404
from django.shortcuts import (
    get_object_or_404,
    redirect,
)
from haystack.generic_views import SearchView
from contacts.models import Book


class ContactSearchView(LoginRequiredMixin,SearchView):
    """ Searches across whole Library

    Restricts search to books and series in one Library.
    """

    paginate_by = settings.LIST_PAGINATE_BY
    paginate_orphans = settings.LIST_PAGINATE_ORPHANS

    def get_queryset(self):
        queryset = super(ContactSearchView, self).get_queryset()
        try:
            book = Book.objects.get(bookowner__user=self.request.user)
        except Book.DoesNotExist:
            raise Http404()
        return queryset.filter(book=book.id)
