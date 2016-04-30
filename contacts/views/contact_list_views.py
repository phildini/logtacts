import json
import re
from braces.views import LoginRequiredMixin
from django.conf import settings
from django.contrib import messages
from django.core.paginator import Paginator
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import (
    get_object_or_404,
    redirect,
)
from django.views.generic import (
    ListView,
    FormView,
)
from haystack.generic_views import SearchView
from haystack.inputs import AutoQuery
from haystack.query import SearchQuerySet

from contacts.models import (
    Book,
    Contact,
    Tag,
    LogEntry,
)
from contacts import forms
from contacts.views import BookOwnerMixin


class ContactListView(BookOwnerMixin, FormView, ListView):

    model = Contact
    template_name = 'contact_list.html'
    form_class = forms.MultiContactForm
    paginate_by = settings.LIST_PAGINATE_BY
    paginate_orphans = settings.LIST_PAGINATE_ORPHANS

    def get_search_contacts(self):
        try:
            book = Book.objects.get(bookowner__user=self.request.user)
        except Book.DoesNotExist:
            raise Http404()
        self.query = self.request.GET.get('q')
        results = re.split(
            r'(?P<tag>\w+\:(?:\"[\w\s]+\"|\w+\b))',
            self.query,
        )
        self.search_tags = []
        parts = []
        for result in results:
            if result.startswith('tag:'):
                tag_str = result.strip().split(':')[1].strip('"')
                try:
                    self.search_tags.append(Tag.objects.get(book=book, tag=tag_str))
                except Tag.DoesNotExist:
                    pass
            else:
                parts.append(result.strip())
        searchqueryset = SearchQuerySet().filter(book=book.id)
        if self.search_tags:
            searchqueryset = searchqueryset.filter(
                tags_ids__in=[tag.id for tag in self.search_tags],
            )

        query = ' '.join(parts)
        sqs = searchqueryset.auto_query(query.strip())
        contact_ids = [result.object.id for result in sqs]
        return contact_ids

    def get_success_url(self, *args, **kwargs):
        return reverse('contacts-list')

    def get_form_kwargs(self):
        kwargs = super(ContactListView, self).get_form_kwargs()
        kwargs['contact_ids'] = [contact.id for contact in self.get_queryset()]
        return kwargs

    def form_valid(self, form, *args, **kwargs):
        contact_ids = []
        for contact in form.cleaned_data:
            if form.cleaned_data[contact]:
                contact_ids.append(contact.split('_')[1])
        self.request.session['selected_contacts'] = json.dumps(contact_ids)
        import pdb; pdb.set_trace()
        if not contact_ids:
            messages.info(self.request, "No contacts selected.")
            return HttpResponseRedirect(reverse('contacts-list'))
        if self.request.POST.get('emails'):
            return HttpResponseRedirect(reverse('contact_emails'))
        if self.request.POST.get('addresses'):
            return HttpResponseRedirect(reverse('contact_addresses'))
        if self.request.POST.get('merge'):
            return HttpResponseRedirect(reverse('contacts_merge'))
        if self.request.POST.get('addtag'):
            return HttpResponseRedirect(reverse('contacts_add_tag'))
        return HttpResponseRedirect(self.get_success_url())

    def get_queryset(self):
        if not (hasattr(self, '_queryset') and self._queryset):
            base_queryset = super(ContactListView, self).get_queryset()
            if self.request.GET.get('q'):
                base_queryset = base_queryset.filter(id__in=self.get_search_contacts())
            self._queryset = base_queryset
            sort = self.request.GET.get('s')
            if sort == 'oldnew':
                self._queryset = self._queryset.order_by('last_contact')
            if sort == 'newold':
                self._queryset = self._queryset.order_by('-last_contact')
            if sort == 'za':
                self._queryset = self._queryset.order_by('-name')
            else:
                self._queryset = self._queryset.order_by('name')
            self._queryset = self._queryset.prefetch_related('tags')
        return self._queryset

    def get_logs(self):
        return LogEntry.objects.logs_for_user_book(
            self.request.user,
        ).order_by('-created')

    def get_context_data(self, **kwargs):
        context = super(ContactListView, self).get_context_data(**kwargs)
        context['tags'] = Tag.objects.get_tags_for_user(self.request.user)
        context['logs'] = self.get_logs()[:10]
        if self.request.GET.get('q'):
            context['search_tags'] = self.search_tags
            context['query_raw'] = self.query
            context['is_search'] = True
        return context


class TaggedContactListView(ContactListView):

    def dispatch(self, request, *args, **kwargs):
        self.tag = get_object_or_404(
            Tag.objects.get_tags_for_user(self.request.user),
            pk=self.kwargs.get('pk'),
        )
        return super(TaggedContactListView, self).dispatch(request, *args, **kwargs)

    def get_logs(self):
        return LogEntry.objects.logs_for_user_and_tag(
            self.request.user,
            self.tag,
        ).order_by('-created')

    def get_queryset(self):
        return super(TaggedContactListView, self).get_queryset().filter(
            tags__id=self.kwargs.get('pk'),
        )

    def get_context_data(self, **kwargs):
        context = super(TaggedContactListView, self).get_context_data(**kwargs)
        context['tag'] = self.tag

        return context
