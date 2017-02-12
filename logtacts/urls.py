from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.views.generic import TemplateView


# Why are we doing this crazy thing of spelling out all the allauth urls?
# Because I want to know _exactly_ what the surface area of the product is.
from allauth.account import views as allauth_views
from allauth.socialaccount import views as social_views
from allauth.socialaccount.providers.twitter import views as twitter_views
from allauth.socialaccount.providers.foursquare import views as foursquare_views
from allauth.socialaccount.providers.google import views as google_views

import nexus
import gargoyle

from contacts.urls import (
    api_urls,
    contact_urls,
    log_urls,
    tag_urls,
)

from contacts.views.import_views import GoogleImportView
from contacts.views.log_views import email_log_view

from invitations.views import (
    CreateInviteView,
    AcceptInviteView,
)

from logtacts.views import HomeView
from payments.views import (
    PaymentView,
    stripe_webhook_view,
)
from profiles.views import ReviewUserView
from chats.views import sms

admin.autodiscover()
gargoyle.autodiscover()


foursquare_urls = [
    url('^login/$', foursquare_views.oauth2_login, name="foursquare_login"),
    url(
        '^login/callback/$',
        foursquare_views.oauth2_callback,
        name="foursquare_callback",
    ),
]


twitter_urls = [
    url('^login/$', twitter_views.oauth_login, name="twitter_login"),
    url(
        '^login/callback/$',
        twitter_views.oauth_callback,
        name="twitter_callback",
    ),
]

google_urls = [
    url('^login/$', google_views.oauth2_login, name="google_login"),
    url(
        '^login/callback/$',
        google_views.oauth2_callback,
        name="google_callback",
    ),
]


social_urls = [
    url('^login/cancelled/$', social_views.login_cancelled,
        name='socialaccount_login_cancelled'),
    url('^login/error/$', social_views.login_error, name='socialaccount_login_error'),
    url('^signup/$', social_views.signup, name='socialaccount_signup'),
    url('^connections/$', social_views.connections, name='socialaccount_connections')
]


allauth_urls = [
    url(r"^signup/$", allauth_views.signup, name="account_signup"),
    url(r"^login/$", allauth_views.login, name="account_login"),
    url(r"^logout/$", allauth_views.logout, name="account_logout"),
    url(r"^password/change/$", allauth_views.password_change,
        name="account_change_password"),
    url(r"^email/$", allauth_views.email, name="account_email"),
    url(r"^confirm-email/$", allauth_views.email_verification_sent,
        name="account_email_verification_sent"),
    url(r"^confirm-email/(?P<key>[-:\w]+)/$", allauth_views.confirm_email,
        name="account_confirm_email"),
    url(r"^password/reset/$", allauth_views.password_reset,
        name="account_reset_password"),
    url(r"^password/reset/done/$", allauth_views.password_reset_done,
        name="account_reset_password_done"),
    url(r"^password/reset/key/(?P<uidb36>[0-9A-Za-z]+)-(?P<key>.+)/$",
        allauth_views.password_reset_from_key,
        name="account_reset_password_from_key"),
    url(r"^password/reset/key/done/$", allauth_views.password_reset_from_key_done,
        name="account_reset_password_from_key_done"),
    url('^social/', include(social_urls)),
    url('^twitter/', include(twitter_urls)),
    url('^foursquare/', include(foursquare_urls)),
    url('^google/', include(google_urls)),
]

landing_urls = [
    url(
        r'^alameda-made$',
        TemplateView.as_view(template_name='landing_pages/alameda_made.html'),
        name='alameda-made',
    )
]


urlpatterns = [
    url(r'^accounts/', include(allauth_urls)),
    url(r'^admin/dashboard', ReviewUserView.as_view()),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^api/', include(api_urls)),
    url(r'^benefits$', TemplateView.as_view(template_name='pages/benefits.html'), name='benefits'),
    url(r'^docs/', include('rest_framework_swagger.urls')),
    url(
        r'^(?P<book>\d+)/import/google/',
        GoogleImportView.as_view(),
        name='import-google-contacts',
    ),
    url(r'^(?P<book>\d+)/invites/add$', CreateInviteView.as_view(), name='create-invite'),
    url(r'^invites/accept/(?P<key>[\w-]+)/$', AcceptInviteView.as_view(), name='accept-invite'),
    url(r'^l/', include(landing_urls)),
    url(r"^login/$", allauth_views.login, name="login"),
    url(r'^log/email/$', email_log_view),
    url(r'^log/', include(log_urls)),
    url(r'^(?P<book>\d+)/log/', include(log_urls)),
    url(r'^nexus/', include(nexus.site.urls)),
    url(r'^policies$', TemplateView.as_view(template_name='pages/policies.html'), name='policies'),
    url(r'^pricing$', TemplateView.as_view(template_name='pages/pricing.html'), name='pricing'),
    url(r'^privacy/$', TemplateView.as_view(template_name='pages/privacy.html'), name='privacy'),
    url(r'^pay/$', PaymentView.as_view(), name='pay-view'),
    url(r"^signup/$", allauth_views.signup, name="signup"),
    url(r'^sms/$', sms),
    url(r'^stripe/$', stripe_webhook_view),
    url(r'^tags/', include(tag_urls)),
    url(r'^(?P<book>\d+)/tags/', include(tag_urls)),
    url(r'^u/', include('profiles.urls')),
    url(r'^$', HomeView.as_view(), name='home'),
    url(r'^(?P<book>\d+)/', include(contact_urls)),
    url(r'^', include('django.contrib.auth.urls')),
]
