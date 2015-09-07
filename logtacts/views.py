from django.views.generic import TemplateView
from contacts.views.contact_views import ContactListView


class HomeView(TemplateView):

    template_name = "home.html"

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            return ContactListView.as_view()(request)

        return super(HomeView, self).dispatch(request, *args, **kwargs)

