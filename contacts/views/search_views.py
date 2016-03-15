import re
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
        self.query = self.request.GET.get('q')
        results = re.split(
            r'(?P<tag>\w+\:(?:\"[\w\s]+\"|\w+\b))',
            self.query,
        )
        self.tags = []
        parts = []
        for result in results:
            if result.startswith('tag:'):
                tag_str = result.strip().split(':')[1].strip('"')
                try:
                    self.tags.append(Tag.objects.get(book=book, tag=tag_str))
                except Tag.DoesNotExist:
                    pass
            else:
                parts.append(result.strip())
        queryset = SearchQuerySet().filter(book=book.id)
        if self.tags:
            queryset = queryset.filter(tags_ids__in=[tag.id for tag in self.tags])

        query = ' '.join(parts)
        form_kwargs['data'] = {'q': query.strip()}
        form_kwargs['searchqueryset'] = queryset
        return form_kwargs

    def get_context_data(self, *args, **kwargs):
        context = super(ContactSearchView, self).get_context_data(*args, **kwargs)
        context['tags'] = self.tags
        context['query_raw'] = self.query
        return context
