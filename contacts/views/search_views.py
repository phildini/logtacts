from braces.views import LoginRequiredMixin
from django.conf import settings
from django.http import Http404
from django.shortcuts import (
    get_object_or_404,
    redirect,
)
from haystack.generic_views import SearchView
from haystack.inputs import AutoQuery
from haystack.query import SearchQuerySet
from contacts.forms import ContactSearchForm
from contacts.models import Book, Tag


class ContactSearchView(LoginRequiredMixin,SearchView):
    """ Searches across whole Library

    Restricts search to books and series in one Library.
    """

    paginate_by = settings.LIST_PAGINATE_BY
    paginate_orphans = settings.LIST_PAGINATE_ORPHANS
    form_class = ContactSearchForm

    def get_form_kwargs(self, *args, **kwargs):
        form_kwargs = super(ContactSearchView, self).get_form_kwargs(*args, **kwargs)
        try:
            book = Book.objects.get(bookowner__user=self.request.user)
        except Book.DoesNotExist:
            raise Http404()
        parts = self.request.GET.get('q').split(' ')
        query_parts = []
        self.tag = None
        if parts:
            for part in parts:
                if part.startswith('tag:'):
                    tag_str = part.split(':')[1]
                    self.tag = Tag.objects.get(book=book, tag=tag_str)
                else:
                    query_parts.append(part)
        queryset = SearchQuerySet().filter(book=book.id)
        if self.tag:
            queryset = queryset.filter(tags_ids=self.tag.id)
        form_kwargs['data'] = {'q': ' '.join(query_parts)}
        form_kwargs['searchqueryset'] = queryset
        return form_kwargs

    def get_context_data(self, *args, **kwargs):
        context = super(ContactSearchView, self).get_context_data(*args, **kwargs)
        context['tag'] = self.tag
        return context
