from django.conf.urls import patterns, include, url

from .views import (
    contact_views,
    log_views,
    search_views,
)

from .api import views as contact_api_views

contact_urls = [
    url(
        r'^list/$',
        contact_views.ContactListView.as_view(),
        name='contacts-list',
    ),
    url(
        r'^(?P<pk>\d+)/$',
        contact_views.ContactView.as_view(),
        name='contacts-view',
    ),
    url(
        r'^new$',
        contact_views.CreateContactView.as_view(),
        name='contacts-new',
    ),
    url(
        r'^edit/(?P<pk>\d+)/$',
        contact_views.EditContactView.as_view(),
        name='contacts-edit',
    ),
    url(
        r'^delete/(?P<pk>\d+)/$',
        contact_views.DeleteContactView.as_view(),
        name='contacts-delete',
    ),
    url(
        r'^tagged/(?P<pk>\d+)/$',
        contact_views.TaggedContactListView.as_view(),
        name='contacts-tagged',
    ),
    url(
        r'^search/',
        search_views.ContactSearchView.as_view(),
        name="search",
    ),
    url(
        r'^emails/',
        contact_views.ExportEmailView.as_view(),
        name='contact_emails',
    ),
    url(
        r'^emailexport/',
        contact_views.email_csv_view,
        name='contact_email_export',
    ),
]

tag_urls = [
    url(
        r'^new$',
        contact_views.CreateTagView.as_view(),
        name='tags-new',
    ),
    url(
        r'^(?P<pk>\d+)/edit/$',
        contact_views.EditTagView.as_view(),
        name='tags-edit',
    ),
    url(
        r'^(?P<pk>\d+)/delete/$',
        contact_views.DeleteTagView.as_view(),
        name='tags-delete',
    ),
]

log_urls = [
    url(
        r'^log/edit/(?P<pk>\d+)/$',
        log_views.EditLogView.as_view(),
        name='log-edit',
    ),
    url(
        r'^log/delete/(?P<pk>\d+)/$',
        log_views.DeleteLogView.as_view(),
        name='log-delete',
    ),
]

api_urls = [
    url(r'^search/$', contact_api_views.ContactSearchAPIView.as_view()),
    url(
        r'^contacts/$',
        contact_api_views.ContactListCreateAPIView.as_view(),
    ),
    url(
        r'^contacts/(?P<pk>\d+)/$',
        contact_api_views.ContactDetailEditAPIView.as_view(),
    ),
    url(
        r'^contacts/(?P<pk>\d+)/logs/$',
        contact_api_views.LogListCreateAPIView.as_view(),
    ),
    url(r'^tags/$', contact_api_views.TagListCreateAPIView.as_view()),
]