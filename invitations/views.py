from braces.views import LoginRequiredMixin
from django.conf import settings
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.utils.crypto import get_random_string
from django.shortcuts import (
    get_object_or_404,
    redirect,
)
from django.views.generic import (
    CreateView,
    FormView,
    View,
)

from contacts.models import (
    Book,
    BookOwner,
)

from gargoyle import gargoyle

import payments as payment_constants

from .models import Invitation
from .forms import InvitationForm


class CreateInviteView(LoginRequiredMixin, CreateView):

    model = Invitation
    form_class = InvitationForm
    template_name = 'invite_edit.html'

    def get_success_url(self, **kwargs):
        return reverse('contacts-list', kwargs={
            'book': self.request.current_book.id,
        })

    def get_context_data(self, *args, **kwargs):
        context = super(CreateInviteView, self).get_context_data(*args, **kwargs)
        if self.request.current_book:
            book = self.request.current_book
        else:
            book = BookOwner.objects.get(user=self.request.user).book
        invitations = Invitation.objects.filter(book=book)
        if gargoyle.is_active('enable_payments', self.request):
            has_more_invites = (
                book.plan and
                len(invitations) < payment_constants.PLANS[book.plan]['collaborators']
            )
            if not has_more_invites:
                messages.warning(
                    self.request,
                    "You are out of invites for this book. You can still invite people to ContactOtter, but need to upgrade your plan to share this book with other collaborators."
                )
        context['invitations'] = invitations


    def form_valid(self, form):
        form.instance.sender = self.request.user
        if form.cleaned_data.get('share_book'):
            book = self.request.current_book
            if gargoyle.is_active('enable_payments', self.request):
                invitations = Invitation.objects.filter(book=book)
                if book.plan and len(invitations) >= payment_constants.PLANS[book.plan]['collaborators']:
                    form.add_error(field=None, error="You don't have any invites left on this plan.")
                    return self.form_invalid(form)
            form.instance.book = book
        messages.success(
            self.request,
            "Invited {}".format(form.cleaned_data.get('email')),
        )
        return super(CreateInviteView, self).form_valid(form)


class AcceptInviteView(FormView):

    form_class = SetPasswordForm
    template_name = "set_password.html"

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            messages.warning(
                self.request,
                "Logged-in users can't accept invitations",
                )
            return redirect(reverse('contacts-list', kwargs={
                'book': self.request.current_book.id,
            }))
        invite = get_object_or_404(
            Invitation.objects,
            key=kwargs.get('key'),
            status=Invitation.SENT,
        )
        # By this point we should have a good invite.
        password_plain = get_random_string(20)
        password = make_password(password_plain)
        user = User.objects.create(
            username=invite.email,
            email=invite.email,
            password=password,
        )
        user = authenticate(username=invite.email, password=password_plain)
        if invite.book:
            self.book = invite.book
            BookOwner.objects.create_for_user(user=user, book=invite.book)
        else:
            self.book = Book.objects.create_for_user(user)
        user.save()
        login(request, user)
        invite.status = invite.ACCEPTED
        invite.save()
        response = super(AcceptInviteView, self).get(request, *args, **kwargs)
        return response

    def get_context_data(self, *args, **kwargs):
        context = super(AcceptInviteView, self).get_context_data(*args, **kwargs)
        context['book'] = self.book
        context['hide_chrome'] = True
        return context

    def get_success_url(self):
        return reverse('contacts-list', kwargs={
            'book': self.request.current_book.id,
        })

    def get_form(self):
        return self.form_class(self.request.user, **self.get_form_kwargs())

    def form_valid(self, form):
        messages.success(
            self.request,
            "Welcome to ContactOtter!",
        )
        return super(AcceptInviteView, self).form_valid(form)
