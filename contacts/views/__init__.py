from braces.views import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import (
    get_object_or_404,
    redirect
)

from contacts.models import (
    Book,
    BookOwner,
)


class BookOwnerMixin(LoginRequiredMixin):

    def get_queryset(self):
        if self.kwargs.get('book'):
            try:
                bookowner = BookOwner.objects.get(
                    user=self.request.user,
                    book_id=self.kwargs.get('book'),
                )
                return self.model.objects.for_user(
                    self.request.user, book=bookowner.book,
                )
            except BookOwner.DoesNotExist:
                pass
        return self.model.objects.for_user(self.request.user)

    def get_object(self, queryset=None):
        instance = super(BookOwnerMixin, self).get_object(queryset)

        if not instance.can_be_viewed_by(self.request.user):
            raise PermissionDenied

        return instance

    def form_valid(self, form):
        form.instance.book = BookOwner.objects.get(
            user=self.request.user
        ).book
        response = super(BookOwnerMixin, self).form_valid(form)

        return response
