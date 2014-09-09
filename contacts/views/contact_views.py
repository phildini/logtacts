from django.core.urlresolvers import reverse
from django.views.generic import (
    CreateView,
    DeleteView,
    ListView,
    UpdateView,
    FormView,
)

from contacts.models import (
    Contact,
    Tag,
)

from contacts import forms
from contacts.views import LoggedInMixin

class ContactListView(LoggedInMixin, ListView):

    model = Contact
    template_name = 'contact_list.html'

    def get_queryset(self):
        qs = super(ContactListView, self).get_queryset()
        return qs.order_by('name')

class ContactView(LoggedInMixin, FormView):

    template_name = 'contact.html'
    form_class = forms.LogEntryForm

    def dispatch(self, request, **kwargs):
        self.contact = Contact.objects.get(
            pk=self.kwargs.get('pk'),
        )
        return super(ContactView, self).dispatch(request, **kwargs)

    def get_success_url(self):
        return reverse(
            'contacts-view',
            args=(self.kwargs.get('pk')),
        )

    def get_context_data(self, **kwargs):
        context = super(ContactView, self).get_context_data(**kwargs)
        
        context['contact'] = self.contact
        return context

    def form_valid(self, form):
        new_log = form.save(commit=False)
        new_log.contact = self.contact
        new_log.logged_by = self.request.user
        form.save()
        return super(ContactView, self).form_valid(form)

class CreateContactView(LoggedInMixin, CreateView):

    model = Contact
    template_name = 'edit_contact.html'
    form_class = forms.ContactForm

    def get_success_url(self):
        return reverse('contacts-view', kwargs={'pk': self.object.id})

    def get_context_data(self, **kwargs):
        context = super(CreateContactView, self).get_context_data(**kwargs)
        context['action'] = reverse('contacts-new')

        return context

class EditContactView(LoggedInMixin, UpdateView):
    model = Contact
    template_name = 'edit_contact.html'
    form_class = forms.ContactForm

    def get_success_url(self):
        return reverse(
            'contacts-view',
            kwargs={'pk': self.get_object().id},
        )

    def get_context_data(self, **kwargs):
        context = super(EditContactView, self).get_context_data(**kwargs)
        context['action'] = reverse(
            'contacts-edit',
            kwargs={'pk': self.get_object().id},
        )

        return context


class DeleteContactView(LoggedInMixin, DeleteView):

    model = Contact
    template_name = 'delete_contact.html'

    def get_success_url(self):
        return reverse('contacts-list')

class CreateTagView(LoggedInMixin, CreateView):
    model = Tag
    template_name = 'edit_tag.html'
    form_class = forms.TagForm

    def get_success_url(self):
        return reverse('contacts-list')

    def get_context_data(self, **kwargs):
        context = super(CreateTagView, self).get_context_data(**kwargs)
        context['action'] = reverse('tags-new')

        return context

