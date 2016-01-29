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
from footprints.main.views import (
    LoginView, LogoutView, AddActorView, CreateFootprintView,
    FootprintDetailView, PersonDetailView, PlaceDetailView,
    WrittenWorkDetailView, TitleListView, NameListView,
    AddPlaceView, AddDateView, RemoveRelatedView, FootprintListView,
    AddIdentifierView, AddDigitalObjectView, ConnectFootprintView,
    ContactUsView, AddLanguageView, DisplayDateView, CopyFootprintView)
from footprints.main.viewsets import (
    BookCopyViewSet, ImprintViewSet, ActorViewSet,
    ExtendedDateViewSet, FootprintViewSet, LanguageViewSet,
    PersonViewSet, PlaceViewSet, RoleViewSet, WrittenWorkViewSet, UserViewSet,
    StandardizedIdentificationViewSet, DigitalFormatViewSet,
    DigitalObjectViewSet, StandardizedIdentificationTypeViewSet)
from footprints.mixins import is_staff


admin.autodiscover()

auth_urls = (r'^accounts/', include('django.contrib.auth.urls'))
if hasattr(settings, 'CAS_BASE'):
    auth_urls = (r'^accounts/', include('djangowind.urls'))

router = routers.DefaultRouter()
router.register(r'actor', ActorViewSet)
router.register(r'book', BookCopyViewSet, base_name='book')
router.register(r'digitalformat', DigitalFormatViewSet)
router.register(r'digitalobject', DigitalObjectViewSet)
router.register(r'edtf', ExtendedDateViewSet)
router.register(r'footprint', FootprintViewSet, base_name='footprint')
router.register(r'identifiertype', StandardizedIdentificationTypeViewSet)
router.register(r'identifier', StandardizedIdentificationViewSet)
router.register(r'imprint', ImprintViewSet, base_name='imprint')
router.register(r'language', LanguageViewSet)
router.register(r'person', PersonViewSet)
router.register(r'place', PlaceViewSet)
router.register(r'role', RoleViewSet)
router.register(r'user', UserViewSet)
router.register(r'writtenwork', WrittenWorkViewSet)


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
    url(r'^actor/add/$',
        AddActorView.as_view(), name='add-actor-view'),
    url(r'^language/add/$',
        AddLanguageView.as_view(), name='add-language-view'),
    url(r'^place/add/$',
        AddPlaceView.as_view(), name='add-place-view'),
    url(r'^date/add/$',
        AddDateView.as_view(), name='add-date-view'),
    url(r'^identifier/add/$',
        AddIdentifierView.as_view(), name='add-identifier-view'),
    url(r'^digitalobject/add/$',
        AddDigitalObjectView.as_view(), name='add-digital-object-view'),

    url(r'^remove/related/$',
        RemoveRelatedView.as_view(), name='remove-related'),

    url(r'^footprint/create/$', CreateFootprintView.as_view(),
        name='create-footprint-view'),
    url(r'^footprint/connect/(?P<pk>\d+)/$', ConnectFootprintView.as_view(),
        name='connect-footprint-view'),
    url(r'^footprint/copy/(?P<pk>\d+)/$', CopyFootprintView.as_view(),
        name='copy-footprint-view'),

    url(r'^footprint/(?P<pk>\d+)/$',
        FootprintDetailView.as_view(), name='footprint-detail-view'),
    url(r'^person/(?P<pk>\d+)/$',
        PersonDetailView.as_view(), name='person-detail-view'),
    url(r'^place/(?P<pk>\d+)/$',
        PlaceDetailView.as_view(), name='place-detail-view'),
    url(r'^writtenwork/(?P<pk>[-_\w]+)/$',
        WrittenWorkDetailView.as_view(), name='writtenwork-detail-view'),

    url(r'^browse/footprints/$', FootprintListView.as_view(),
        name='browse-footprint-list-default'),
    url(r'^browse/footprints/(?P<sort_by>\w+)/$', FootprintListView.as_view(),
        name='browse-footprint-list'),

    url(r'^date/display/$',
        DisplayDateView.as_view(), name='display-date-view'),

    url(r'^search/',
        SearchView(template="search/search.html",
                   form_class=FootprintSearchForm),
        name='search'),

    url(r'^api-auth/', include('rest_framework.urls',
                               namespace='rest_framework')),
    url(r'^api/', include(router.urls)),
    url(r'^api/title/$', TitleListView.as_view()),
    url(r'^api/name/$', NameListView.as_view()),

    # Contact us forms.
    (r'^contact/success/$',
     TemplateView.as_view(template_name='main/contact_success.html')),
    (r'^contact/$', ContactUsView.as_view()),

    (r'^admin/', include(admin.site.urls)),
    url(r'^_impersonate/', include('impersonate.urls')),
    (r'^stats/$', TemplateView.as_view(template_name="stats.html")),
    (r'smoketest/', include('smoketest.urls')),
    (r'infranil/', include('infranil.urls')),
    (r'^uploads/(?P<path>.*)$',
     'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),

    # Visualizations for grant application
    (r'^pathmapper/',
     TemplateView.as_view(template_name='design/pathmapper.html')),
)

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += patterns(
        '',
        url(r'^__debug__/', include(debug_toolbar.urls)),
    )
