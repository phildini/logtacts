from django.core.urlresolvers import reverse
from django.views.generic import UpdateView

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