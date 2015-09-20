from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect

from contacts.models import BookOwner


class LoggedInMixin(object):

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated():
            return redirect(
                '/login?next={}'.format(request.path)
            )
        return super(LoggedInMixin, self).dispatch(request, *args, **kwargs)


class BookOwnerMixin(LoggedInMixin):

    def get_queryset(self):
        queryset = super(LoggedInMixin, self).get_queryset()
        queryset = queryset.filter(
            book__bookowner__user=self.request.user,
        )
        return queryset

    def get_object(self, queryset=None):
        instance = super(LoggedInMixin, self).get_object(queryset)

        if not instance.book.bookowner_set.filter(user=self.request.user):
            raise PermissionDenied

        return instance

    def form_valid(self, form):
        form.instance.book = BookOwner.objects.get(
            user=self.request.user
        ).book
        response = super(LoggedInMixin, self).form_valid(form)

        return response
