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
    template_name = 'edit_contact.html'
    form_class = contacts.forms.LogEntryForm

    def get_success_url(self):
        return reverse(
            'contacts-view',
            kwargs={'pk': self.object.contact.id},
        )

class DeleteLogView(LoggedInMixin, DeleteView):

    model = LogEntry
    template_name = 'delete_log.html'

    def get_success_url(self):
        return reverse(
            'contacts-view',
            kwargs={'pk': self.object.contact.id},
        )