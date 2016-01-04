from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.views.generic import (
    DeleteView,
    UpdateView,
)

import contacts.forms
from contacts.models import LogEntry
from contacts.views import LoggedInMixin

class EditLogView(LoggedInMixin, UpdateView):
    model = LogEntry
    template_name = 'edit_log.html'
    form_class = contacts.forms.LogEntryForm

    def get_object(self, queryset=None):
        instance = super(LoggedInMixin, self).get_object(queryset)

        if not instance.can_be_edited_by(self.request.user):
            raise PermissionDenied

        return instance

    def get_success_url(self):
        return reverse(
            'contacts-view',
            kwargs={'pk': self.object.contact.id},
        )

    def form_valid(self, form):
        messages.success(
            self.request,
            "Log edited",
        )
        return super(EditLogView, self).form_valid(form)

class DeleteLogView(LoggedInMixin, DeleteView):

    model = LogEntry
    template_name = 'delete_log.html'

    def get_object(self, queryset=None):
        instance = super(LoggedInMixin, self).get_object(queryset)

        if not instance.can_be_edited_by(self.request.user):
            raise PermissionDenied

        return instance

    def get_success_url(self):
        return reverse(
            'contacts-view',
            kwargs={'pk': self.object.contact.id},
        )

        def form_valid(self, form):
            messages.success(
                self.request,
                "Log deleted",
            )
        return super(DeleteLogView, self).form_valid(form)