from braces.views import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect

from contacts.models import BookOwner


class BookOwnerMixin(LoginRequiredMixin):

    def get_queryset(self):
        queryset = self.model.objects.for_user(self.request.user)
        return queryset

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
