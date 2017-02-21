from braces.views import LoginRequiredMixin
from channels import Channel
from datetime import timedelta
from django.contrib import messages
from django.conf import settings
from django.core.cache import cache
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.http import (
    HttpResponse,
    HttpResponseRedirect,
)
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import (
    DeleteView,
    ListView,
    UpdateView,
)
from django.shortcuts import redirect
from django.utils import timezone

import contacts.forms
from contacts.models import Contact, LogEntry, Tag
from contacts.views import BookOwnerMixin


class EditLogView(LoginRequiredMixin, UpdateView):
    model = LogEntry
    template_name = 'edit_log.html'
    form_class = contacts.forms.LogEntryForm

    def dispatch(self, request, *args, **kwargs):
        response = super(EditLogView, self).dispatch(request, *args, **kwargs)
        if response.status_code == 200:
            if self.object.kind == 'edit':
                messages.warning(self.request, "Edit logs cannot be changed")
                return redirect(reverse('contacts-view', kwargs={
                    'pk': self.object.contact.id,
                    'book': self.request.current_book.id,
                }))
        return response

    def get_object(self, queryset=None):
        instance = super(EditLogView, self).get_object(queryset)
        if not instance.can_be_edited_by(self.request.user):
            raise PermissionDenied
        return instance

    def get_success_url(self):
        return reverse(
            'contacts-view',
            kwargs={
                'pk': self.object.contact.id,
                'book': self.request.current_book.id,
            },
        )

    def form_valid(self, form):
        messages.success(
            self.request,
            "Log edited",
        )
        return super(EditLogView, self).form_valid(form)

    def get_context_data(self, *args, **kwargs):
        context = super(EditLogView, self).get_context_data(*args, **kwargs)
        context['book'] = self.request.current_book
        return context


class DeleteLogView(LoginRequiredMixin, DeleteView):

    model = LogEntry
    template_name = 'delete_log.html'

    def dispatch(self, request, *args, **kwargs):
        response = super(DeleteLogView, self).dispatch(request, *args, **kwargs)
        if response.status_code == 200:
            if self.object.kind == 'edit':
                messages.warning(self.request, "Edit logs cannot be changed")
                return redirect(
                    reverse('contacts-view', kwargs={
                            'pk': self.object.contact.id,
                            'book': self.request.current_book.id,
                    }))
        return response

    def get_object(self, queryset=None):
        instance = super(DeleteLogView, self).get_object(queryset)

        if not instance.can_be_edited_by(self.request.user):
            raise PermissionDenied

        return instance

    def get_success_url(self):
        return reverse(
            'contacts-view',
            kwargs={
                'pk': self.object.contact.id,
                'book': self.request.current_book.id,
            },
        )

        def form_valid(self, form):
            messages.success(
                self.request,
                "Log deleted",
            )
        return super(DeleteLogView, self).form_valid(form)

    def get_context_data(self, *args, **kwargs):
        context = super(DeleteLogView, self).get_context_data(*args, **kwargs)
        context['book'] = self.request.current_book
        return context


class LogListView(BookOwnerMixin, ListView):

    template_name = "log_list.html"
    model = LogEntry
    paginate_by = settings.LIST_PAGINATE_BY
    paginate_orphans = settings.LIST_PAGINATE_ORPHANS

    def get_context_data(self, *args, **kwargs):
        context = super(LogListView, self).get_context_data(*args, **kwargs)
        context['tags'] = Tag.objects.get_tags_for_user(
            user=self.request.user,
            book=self.request.current_book,
        )
        context['book'] = self.request.current_book
        cache_key = cache_key = "{}::{}::random".format(self.request.user, self.request.current_book)
        if cache.get(cache_key):
            try:
                contact = Contact.objects.for_user(
                    user=self.request.user, book=self.request.current_book,
                ).get(id=cache.get(cache_key))
                last_day = timezone.now() - timedelta(days=1)
                if not contact.last_contact or contact.last_contact < last_day:
                    context['random_contact'] = contact
            except Contact.DoesNotExist:
                pass
        return context


@csrf_exempt
def email_log_view(request):
    if request.method == 'POST':
        Channel('process-incoming-email').send(request.POST)
    return HttpResponse(status=200)
