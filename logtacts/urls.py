from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.views.generic import TemplateView

from allauth.account import views as allauth_views

import nexus
import gargoyle

from contacts.urls import (
    api_urls,
    contact_urls,
    log_urls,
    tag_urls,
)

from invitations.views import (
    CreateInviteView,
    AcceptInviteView,
)

from logtacts.views import HomeView

from profiles.views import ReviewUserView

admin.autodiscover()
gargoyle.autodiscover()

urlpatterns = [
    url(r'^api/', include(api_urls)),
    url(r'^docs/', include('rest_framework_swagger.urls')),
    url(r'^tags/', include(tag_urls)),
    url(r'^log/', include(log_urls)),
    url(r'^allauth_login/', allauth_views.login, name='account_login'),
    url(r'^login/', allauth_views.login, name='login'),
    url(r'^signup/', allauth_views.signup, name='account_signup'),
    url(
        r'^hold/',
        TemplateView.as_view(template_name='signup_success.html'),
        name='account_inactive',
    ),
    url(r'^admin/dashboard', ReviewUserView.as_view()),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^nexus/', include(nexus.site.urls)),
    url(r'^$', HomeView.as_view(), name='home'),
    url(r'^invites/add$', CreateInviteView.as_view(), name='create-invite'),
    url(
        r'^invites/accept/(?P<key>[\w-]+)/$',
        AcceptInviteView.as_view(),
        name='accept-invite',
    ),
    url(r'^u/', include('profiles.urls')),
    url(
        r'^policies$', 
        TemplateView.as_view(template_name='policies.html'),
        name='policies',
    ),
    url(r'^', include(contact_urls)),
    url(r'^', include('django.contrib.auth.urls')),
]
