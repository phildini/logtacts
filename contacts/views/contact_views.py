from collections import OrderedDict
import csv
import json
from braces.views import LoginRequiredMixin
from django.conf import settings
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.db import IntegrityError
from django.http import (
    Http404,
    HttpResponse,
    HttpResponseRedirect,
    JsonResponse,
)
from django.shortcuts import (
    get_object_or_404,
    redirect,
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

from contacts.api import serializers
from contacts.models import (
    Contact,
    Book,
    BookOwner,
    Tag,
    LogEntry,
)

import contacts as contact_settings
from contacts import forms
from contacts.views import BookOwnerMixin
from contacts import common


class ContactView(BookOwnerMixin, FormView):

    template_name = 'contact.html'
    form_class = forms.LogEntryForm

    def dispatch(self, request, **kwargs):
        if self.request.user.is_authenticated():
            self.contact = get_object_or_404(
                Contact.objects.get_contacts_for_user(
                    user=self.request.user,
                    book=self.request.current_book,
                ),
                pk=self.kwargs.get('pk'),
            )
        return super(ContactView, self).dispatch(request, **kwargs)

    def get_success_url(self):
        return reverse(
            'contacts-view',
            kwargs={
                'pk': self.kwargs.get('pk'),
                'book': self.request.current_book.id,
            },
        )

    def get_context_data(self, **kwargs):
        context = super(ContactView, self).get_context_data(**kwargs)
        context['contact'] = self.contact
        context['logs'] = self.contact.logentry_set.all().order_by('-time')
        return context

    def form_valid(self, form):
        new_log = form.save(commit=False)
        new_log.contact = self.contact
        new_log.logged_by = self.request.user
        if not form.cleaned_data.get('time'):
            form.cleaned_data['time'] = timezone.now()
        form.save()
        self.contact.update_last_contact_from_log(new_log)
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
        return reverse('contacts-view', kwargs={
            'pk': self.object.id,
            'book': self.request.current_book.id,
        })

    def get_form_kwargs(self):
        kwargs = super(CreateContactView, self).get_form_kwargs()
        self.tags = Tag.objects.get_tags_for_user(
            user=self.request.user,
            book=self.request.current_book,
        )
        kwargs['tag_choices'] = self.tags.values_list('id', 'tag')
        kwargs['user'] = self.request.user
        kwargs['book'] = self.request.current_book
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(CreateContactView, self).get_context_data(**kwargs)
        context['action'] = reverse('contacts-new', kwargs={
            'book': self.request.current_book.id,
        })
        tag_dict = OrderedDict()
        for tag in self.tags:
            tag_dict[tag.id] = tag
        context['tag_dict'] = tag_dict
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
            kwargs={
                'pk': self.get_object().id,
                'book': self.request.current_book.id,
            },
        )

    def get_form_kwargs(self):
        kwargs = super(EditContactView, self).get_form_kwargs()
        self.tags = Tag.objects.get_tags_for_user(
            user=self.request.user,
            book=self.request.current_book,
        )
        kwargs['tag_choices'] = self.tags.values_list('id', 'tag')
        kwargs['user'] = self.request.user
        kwargs['book'] = self.request.current_book
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(EditContactView, self).get_context_data(**kwargs)
        tag_dict = OrderedDict()
        context['checked_tags'] = self.get_object().tags_cached.values_list(
            'id', flat=True,
        )
        for tag in self.tags:
            tag_dict[tag.id] = tag
        context['tag_dict'] = tag_dict
        context['action'] = reverse(
            'contacts-edit',
            kwargs={
                'pk': self.get_object().id,
                'book': self.request.current_book.id,
            },
        )

        return context

    def form_valid(self, form):
        messages.success(
            self.request,
            "Contact updated",
        )
        return super(EditContactView, self).form_valid(form)


class CopyContactView(BookOwnerMixin, UpdateView):

    model = Contact

    def dispatch(self, request, *args, **kwargs):
        contact = self.get_object()
        contact_fields = contact.contactfields.all()
        tags = contact.tags.all()
        contact.pk = None
        contact.save()
        # TODO: This is a hack. We should make a better copy method soon.
        for field in contact_fields:
            contact.contactfield_set.create(
                contact=contact,
                label=field.label,
                kind=field.kind,
                preferred=field.preferred,
                value=field.value,
            )
        for tag in tags:
            contact.tags.add(tag)
        messages.success(self.request, "Contact copied")
        return HttpResponseRedirect(
            reverse('contacts-edit', kwargs={
                'pk': contact.pk,
                'book': self.request.current_book.id,
            })
        )


class DeleteContactView(BookOwnerMixin, DeleteView):

    model = Contact
    template_name = 'delete_contact.html'

    def get_success_url(self):
        return reverse('contacts-list', kwargs={
            'book': self.request.current_book.id,
        })

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
        return reverse('contacts-list', kwargs={
            'book': self.request.current_book.id,
        })

    def get_context_data(self, **kwargs):
        context = super(CreateTagView, self).get_context_data(**kwargs)
        context['action'] = reverse('tags-new', kwargs={
                'book': self.request.current_book.id,
        })
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
        return reverse('contacts-list', kwargs={
            'book': self.request.current_book.id,
        })

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
        return reverse('contacts-list', kwargs={
            'book': self.request.current_book.id,
        })

    def form_valid(self, form):
        messages.success(
            self.request,
            "Tag deleted",
        )
        return super(DeleteTagView, self).form_valid(form)


class ExportEmailView(BookOwnerMixin, TemplateView):

    template_name = 'export_emails.html'

    def get_context_data(self, *args, **kwargs):
        context = super(ExportEmailView, self).get_context_data(*args, **kwargs)
        contacts = common.get_selected_contacts_from_request(self.request)
        context['contacts'] = contacts
        return context


class ExportAddressView(BookOwnerMixin, TemplateView):

    template_name = 'export_addresses.html'

    def get_context_data(self, *args, **kwargs):
        context = super(ExportAddressView, self).get_context_data(*args, **kwargs)
        contacts = common.get_selected_contacts_from_request(self.request)
        context['contacts'] = contacts
        return context


def email_csv_view(request):
    if request.user.is_authenticated():
        contacts = common.get_selected_contacts_from_request(request)
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="contact_emails.csv"'
        writer = csv.writer(response)
        writer.writerow(['Name', 'Email'])
        for contact in contacts:
            writer.writerow([contact.name, contact.preferred_email])
        request.session['selected_contacts'] = None
        return response
    raise Http404()


def address_csv_view(request):
    if request.user.is_authenticated():
        contacts = common.get_selected_contacts_from_request(request)
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="contact_addresses.csv"'
        writer = csv.writer(response)
        writer.writerow(['Name', 'Address'])
        for contact in contacts:
            writer.writerow([contact.name, contact.preferred_address])
        request.session['selected_contacts'] = None
        return response
    raise Http404()


def export_full_contact_book_json_view(request):
    if request.user.is_authenticated():
        contacts = Contact.objects.get_contacts_for_user(
            user=request.user,
            book=request.current_book,
        )
        contact_serializer = serializers.ContactSerializer(contacts, many=True)
        tags = Tag.objects.get_tags_for_user(
            user=request.user,
            book=request.current_book,
        )
        tag_serializer = serializers.TagSerializer(tags, many=True)
        export = {
            'version': 2,
            'contacts': contact_serializer.data,
            'tags': tag_serializer.data,
        }
        response = JsonResponse(export)
        response['Content-Disposition'] = 'attachment; filename="full_export.json"'
        return response
    raise Http404()


class MergeContactsView(BookOwnerMixin, TemplateView):

    template_name="merge_contacts.html"

    def get_success_url(self):
        return reverse('contacts-list', kwargs={
            'book': self.request.current_book.id,
        })

    def get_context_data(self, *args, **kwargs):
        context = super(MergeContactsView, self).get_context_data(*args, **kwargs)
        contacts = common.get_selected_contacts_from_request(self.request)
        context['contacts'] = contacts
        context['book'] = self.request.current_book
        return context

    def post(self, request, *args, **kwargs):
        contacts = common.get_selected_contacts_from_request(self.request)
        if contacts and len(contacts) > 1:
            contacts = list(contacts)
            primary_contact = contacts.pop(0)
            note_list = []
            for contact in contacts:
                for field in contact.contactfields:
                    field.preferred = False
                    field.contact = primary_contact
                    field.save()
                for log in LogEntry.objects.filter(contact=contact):
                    log.contact = primary_contact
                    log.save()
                for tag in contact.tags.all():
                    primary_contact.tags.add(tag)
                if not primary_contact.photo_url and contact.photo_url:
                    primary_contact.photo_url = contact.photo_url
                    primary_contact.save()
                note_list.append(contact.name)
                contact.delete()
            log = LogEntry.objects.create(
                contact = primary_contact,
                logged_by = self.request.user,
                kind = 'edit',
                time = timezone.now(),
                notes = "Merged with {}".format(", ".join(note_list)),
            )
            primary_contact.update_last_contact_from_log(log)
            messages.success(
                self.request,
                "Successfully merged contacts.",
            )
            self.request.session['selected_contacts'] = None
            return redirect(reverse(
                'contacts-view',
                kwargs={
                    'pk': primary_contact.id,
                    'book': self.request.current_book.id,
                },
            ))
        return redirect(reverse('contacts-list', kwargs={
            'book':self.request.current_book.id,
        }))


class AddTagView(LoginRequiredMixin, FormView):

    template_name = "contacts_add_tag.html"
    form_class = forms.MultiTagForm

    def get_success_url(self):
        return reverse('contacts-list', kwargs={
            'book': self.request.current_book.id,
        })

    def get_tags(self):
        if not hasattr(self, '_tags'):
            self._tags = Tag.objects.get_tags_for_user(
                user=self.request.user,
                book=self.request.current_book,
            )
        return self._tags

    def get_context_data(self, *args, **kwargs):
        context = super(AddTagView, self).get_context_data(*args, **kwargs)
        context['contacts'] = common.get_selected_contacts_from_request(
            self.request,
        )
        context['tags'] = self.get_tags()
        return context

    def get_form_kwargs(self):
        form_kwargs = super(AddTagView, self).get_form_kwargs()
        form_kwargs['tag_ids'] = [tag.id for tag in self.get_tags()]
        return form_kwargs

    def form_valid(self, form):
        contacts = common.get_selected_contacts_from_request(self.request)
        tag_ids = []
        for tag in form.cleaned_data:
            if form.cleaned_data[tag]:
                tag_ids.append(tag.split('_')[1])
        for contact in contacts:
            # Django's many-to-many add can take just ids, which saves us having
            # to pull the Tag objects from the DB.
            try:
                contact.tags.add(*tag_ids)
                contact.save()
            except IntegrityError:
                # If that contact already had the tag, step through tags to add
                # the missing ones
                for tag_id in tag_ids:
                    try:
                        contact.tags.add(tag_id)
                    except IntegrityError:
                        pass
            log = LogEntry.objects.create(
                contact=contact,
                kind='edit',
                notes='Added tags',
                logged_by=self.request.user,
            )
            contact.update_last_contact_from_log(log)
        self.request.session['selected_contacts'] = None
        return super(AddTagView, self).form_valid(form)
