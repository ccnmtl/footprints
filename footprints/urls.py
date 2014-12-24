from django.conf import settings
from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib.auth.views import password_change, password_change_done, \
    password_reset_done, password_reset_confirm, password_reset_complete
from django.views.generic import TemplateView
from haystack.views import SearchView
from rest_framework import routers

from footprints.main import views
from footprints.main.forms import FootprintSearchForm
from footprints.main.views import (LoginView, LogoutView, TitleListView,
                                   CreateFootprintView, NameListView,
                                   WrittenWorkDetailView, FootprintDetailView,
                                   PersonDetailView, PlaceDetailView)
from footprints.mixins import is_staff


admin.autodiscover()

auth_urls = (r'^accounts/', include('django.contrib.auth.urls'))
if hasattr(settings, 'CAS_BASE'):
    auth_urls = (r'^accounts/', include('djangowind.urls'))

router = routers.DefaultRouter()

urlpatterns = patterns(
    '',
    (r'^$', views.IndexView.as_view()),

    (r'^accounts/login/$', LoginView.as_view()),
    (r'^accounts/logout/$', LogoutView.as_view()),

    # password change & reset. overriding to gate them.
    url(r'^accounts/password_change/$',
        is_staff(password_change),
        name='password_change'),
    url(r'^accounts/password_change/done/$',
        is_staff(password_change_done),
        name='password_change_done'),
    url(r'^password/reset/done/$', password_reset_done,
        name='password_reset_done'),
    url(r'^password/reset/confirm/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/$',
        password_reset_confirm,
        name='password_reset_confirm'),
    url(r'^password/reset/complete/$',
        password_reset_complete, name='password_reset_complete'),

    auth_urls,
    (r'^footprint/create/$', CreateFootprintView.as_view()),
    url(r'^footprint/(?P<pk>\d+)/$',
        FootprintDetailView.as_view(), name='footprint-detail'),
    url(r'^person/(?P<pk>\d+)/$',
        PersonDetailView.as_view(), name='person-detail'),
    url(r'^place/(?P<pk>\d+)/$',
        PlaceDetailView.as_view(), name='place-detail'),
    url(r'^work/(?P<pk>[-_\w]+)/$',
        WrittenWorkDetailView.as_view(), name='writtenwork-detail'),

    url(r'^search/',
        SearchView(template="search/search.html",
                   form_class=FootprintSearchForm),
        name='search'),

    url(r'^api-auth/', include('rest_framework.urls',
                               namespace='rest_framework')),
    url(r'^api/', include(router.urls)),
    url(r'^api/title/$', TitleListView.as_view()),
    url(r'^api/name/$', NameListView.as_view()),

    (r'^admin/', include(admin.site.urls)),
    url(r'^_impersonate/', include('impersonate.urls')),
    (r'^stats/$', TemplateView.as_view(template_name="stats.html")),
    (r'smoketest/', include('smoketest.urls')),
    (r'infranil/', include('infranil.urls')),
    (r'^uploads/(?P<path>.*)$',
     'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
)

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += patterns(
        '',
        url(r'^__debug__/', include(debug_toolbar.urls)),
    )
