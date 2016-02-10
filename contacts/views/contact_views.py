import csv
import json
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import (
    get_object_or_404,
)
from django.views.generic import (
    CreateView,
    DeleteView,
    ListView,
    UpdateView,
    FormView,
    TemplateView,
)
from django.utils import timezone

from contacts.models import (
    Contact,
    BookOwner,
    Tag,
    LogEntry,
)

from contacts import forms
from contacts.views import BookOwnerMixin

class ContactListView(BookOwnerMixin, FormView, ListView):

    model = Contact
    template_name = 'contact_list.html'
    form_class = forms.MultiContactForm

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
        if not contact_ids:
            messages.info(self.request, "No contacts selected.")
            return HttpResponseRedirect(reverse('contacts-list'))
        if self.request.POST.get('emails'):
            return HttpResponseRedirect(reverse('contact_emails'))
        if self.request.POST.get('addresses'):
            return HttpResponseRedirect(reverse('contact_addresses'))
        return HttpResponseRedirect(self.get_success_url())

    def get_queryset(self):
        qs = super(ContactListView, self).get_queryset()
        sort = self.request.GET.get('s')
        if sort == 'oldnew':
            return qs.order_by('last_contact')
        if sort == 'newold':
            return qs.order_by('-last_contact')
        if sort == 'za':
            return qs.order_by('-name')
        return qs.order_by('name')

    def get_context_data(self, **kwargs):
        context = super(ContactListView, self).get_context_data(**kwargs)
        context['tags'] = Tag.objects.get_tags_for_user(self.request.user)
        context['editable'] = True
        return context

class ContactView(BookOwnerMixin, FormView):

    template_name = 'contact.html'
    form_class = forms.LogEntryForm

    def dispatch(self, request, **kwargs):
        self.contact = get_object_or_404(
            Contact.objects.get_contacts_for_user(self.request.user),
            pk=self.kwargs.get('pk'),
        )
        return super(ContactView, self).dispatch(request, **kwargs)

    def get_success_url(self):
        return reverse(
            'contacts-view',
            kwargs={'pk': self.kwargs.get('pk')},
        )

    def get_context_data(self, **kwargs):
        context = super(ContactView, self).get_context_data(**kwargs)
        context['contact'] = self.contact
        context['logs'] = self.contact.logentry_set.all().order_by('-created')
        return context

    def form_valid(self, form):
        new_log = form.save(commit=False)
        new_log.contact = self.contact
        new_log.logged_by = self.request.user
        if not form.cleaned_data.get('time'):
            form.cleaned_data['time'] = timezone.now()
        form.save()
        messages.success(
            self.request,
            "Log added",
        )
        return super(ContactView, self).form_valid(form)

class CreateContactView(BookOwnerMixin, CreateView):

    model = Contact
    template_name = 'edit_contact.html'
    form_class = forms.ContactForm

    def get_success_url(self):
        return reverse('contacts-view', kwargs={'pk': self.object.id})

    def get_form_kwargs(self):
        kwargs = super(CreateContactView, self).get_form_kwargs()
        kwargs['book'] = BookOwner.objects.get(user=self.request.user).book
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(CreateContactView, self).get_context_data(**kwargs)
        context['action'] = reverse('contacts-new')
        return context

    def form_valid(self, form):
        messages.success(
            self.request,
            "Contact added",
        )
        return super(CreateContactView, self).form_valid(form)

class EditContactView(BookOwnerMixin, UpdateView):
    model = Contact
    template_name = 'edit_contact.html'
    form_class = forms.ContactForm

    def get_success_url(self):
        return reverse(
            'contacts-view',
            kwargs={'pk': self.get_object().id},
        )

    def get_form_kwargs(self):
        kwargs = super(EditContactView, self).get_form_kwargs()
        kwargs['book'] = BookOwner.objects.get(user=self.request.user).book
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(EditContactView, self).get_context_data(**kwargs)
        context['action'] = reverse(
            'contacts-edit',
            kwargs={'pk': self.get_object().id},
        )

        return context

    def form_valid(self, form):
        messages.success(
            self.request,
            "Contact updated",
        )
        if form.has_changed:
            note_str = 'Updated ' + ', '.join(form.changed_data)
            LogEntry.objects.create(
                contact = form.instance,
                logged_by = self.request.user,
                kind = 'edit',
                notes = note_str,
            )
        return super(EditContactView, self).form_valid(form)


class DeleteContactView(BookOwnerMixin, DeleteView):

    model = Contact
    template_name = 'delete_contact.html'

    def get_success_url(self):
        return reverse('contacts-list')

    def form_valid(self, form):
        messages.success(
            self.request,
            "Contact deleted",
        )
        return super(DeleteContactView, self).form_valid(form)

class CreateTagView(BookOwnerMixin, CreateView):
    model = Tag
    template_name = 'edit_tag.html'
    form_class = forms.TagForm

    def get_success_url(self):
        return reverse('contacts-list')

    def get_context_data(self, **kwargs):
        context = super(CreateTagView, self).get_context_data(**kwargs)
        context['action'] = reverse('tags-new')
        return context

    def form_valid(self, form):
        messages.success(
            self.request,
            "Tag created",
        )
        return super(CreateTagView, self).form_valid(form)

class EditTagView(BookOwnerMixin, UpdateView):
    model = Tag
    template_name = 'edit_tag.html'
    form_class = forms.TagForm

    def get_success_url(self):
        return reverse('contacts-list')

    def form_valid(self, form):
        messages.success(
            self.request,
            "Tag updated",
        )
        return super(EditTagView, self).form_valid(form)


class DeleteTagView(BookOwnerMixin, DeleteView):

    model = Tag
    template_name = 'delete_tag.html'

    def get_success_url(self):
        return reverse('contacts-list')

    def form_valid(self, form):
        messages.success(
            self.request,
            "Tag deleted",
        )
        return super(DeleteTagView, self).form_valid(form)


class TaggedContactListView(ContactListView):

    def get_queryset(self):
        return Contact.objects.get_contacts_for_user(self.request.user).filter(
            tags__id=self.kwargs.get('pk'),
        ).order_by('name')

    def get_context_data(self, **kwargs):
        context = super(TaggedContactListView, self).get_context_data(**kwargs)
        self.tag = get_object_or_404(
            Tag.objects.get_tags_for_user(self.request.user),
            pk=self.kwargs.get('pk'),
        )
        context['tag'] = self.tag

        return context


class ExportEmailView(BookOwnerMixin, TemplateView):

    template_name = 'export_emails.html'

    def get_context_data(self, *args, **kwargs):
        context = super(ExportEmailView, self).get_context_data(*args, **kwargs)
        selected_contacts = json.loads(
            self.request.session.get('selected_contacts')
        )
        try:
            contacts = Contact.objects.get_contacts_for_user(
                self.request.user
            ).filter(
                id__in=selected_contacts
            )
        except TypeError:
            contacts = []
            messages.warning(
                self.request,
                "Woops! Problem fetching contacts. Try again.",
            )
        context['contacts'] = contacts
        return context


class ExportAddressView(BookOwnerMixin, TemplateView):

    template_name = 'export_addresses.html'

    def get_context_data(self, *args, **kwargs):
        context = super(ExportAddressView, self).get_context_data(*args, **kwargs)
        selected_contacts = json.loads(
            self.request.session.get('selected_contacts')
        )
        try:
            contacts = Contact.objects.get_contacts_for_user(
                self.request.user
            ).filter(
                id__in=selected_contacts
            )
        except TypeError:
            contacts = []
            messages.warning(
                self.request,
                "Woops! Problem fetching contacts. Try again.",
            )
        context['contacts'] = contacts
        return context


def email_csv_view(request):
    selected_contacts = json.loads(
        request.session.get('selected_contacts')
    )
    try:
        contacts = Contact.objects.get_contacts_for_user(
            request.user
        ).filter(
            id__in=selected_contacts
        )
    except TypeError:
        contacts = []
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="contact_emails.csv"'
    writer = csv.writer(response)
    writer.writerow(['Name', 'Email'])
    for contact in contacts:
        writer.writerow([contact.name, contact.email])

    return response


def address_csv_view(request):
    selected_contacts = json.loads(
        request.session.get('selected_contacts')
    )
    try:
        contacts = Contact.objects.get_contacts_for_user(
            request.user
        ).filter(
            id__in=selected_contacts
        )
    except TypeError:
        contacts = []
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="contact_addresses.csv"'
    writer = csv.writer(response)
    writer.writerow(['Name', 'Address'])
    for contact in contacts:
        writer.writerow([contact.name, contact.address])

    return response
