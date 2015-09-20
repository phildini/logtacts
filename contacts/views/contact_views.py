from django.contrib import messages
from django.core.urlresolvers import reverse
from django.shortcuts import (
    get_object_or_404,
)
from django.views.generic import (
    CreateView,
    DeleteView,
    ListView,
    UpdateView,
    FormView,
)
from django.utils import timezone

from contacts.models import (
    Contact,
    BookOwner,
    Tag,
)

from contacts import forms
from contacts.views import BookOwnerMixin

class ContactListView(BookOwnerMixin, ListView):

    model = Contact
    template_name = 'contact_list.html'

    def get_queryset(self):
        qs = super(ContactListView, self).get_queryset()
        return qs.order_by('name')

    def get_context_data(self, **kwargs):
        context = super(ContactListView, self).get_context_data(**kwargs)
        context['tags'] = Tag.objects.filter(book__bookowner__user=self.request.user)
        return context

class ContactView(BookOwnerMixin, FormView):

    template_name = 'contact.html'
    form_class = forms.LogEntryForm

    def dispatch(self, request, **kwargs):
        self.contact = get_object_or_404(
            Contact.objects,
            pk=self.kwargs.get('pk'),
            book__bookowner__user=self.request.user,
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

class TaggedContactListView(BookOwnerMixin, ListView):

    model = Contact
    template_name = 'contact_list.html'

    def get_queryset(self):
        return Contact.objects.filter(
            tags__id=self.kwargs.get('pk'),
        ).order_by('name')

    def get_context_data(self, **kwargs):
        context = super(TaggedContactListView, self).get_context_data(**kwargs)
        context['tag'] = Tag.objects.get(id=self.kwargs.get('pk'))
        context['tags'] = Tag.objects.all()

        return context

