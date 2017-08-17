from django.conf.urls import include, url

from . import views


urlpatterns = [
    url(r'^$', views.ProfileView.as_view(), name='profile'),
]