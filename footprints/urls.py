from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import (
    PasswordChangeDoneView, PasswordResetDoneView, PasswordResetConfirmView,
    PasswordResetCompleteView, PasswordChangeView, PasswordResetView)
from django.urls import path
from django.views.generic import TemplateView
from django.views.static import serve
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from registration.backends.default.views import RegistrationView
from rest_framework import routers

from django_cas_ng import views as cas_views
from footprints.main import views
from footprints.main.forms import CustomRegistrationForm
from footprints.main.views import (
    AddActorView, CreateFootprintView,
    FootprintDetailView, WrittenWorkDetailView, TitleListView, NameListView,
    AddPlaceView, AddDateView, RemoveRelatedView,
    AddIdentifierView, AddDigitalObjectView, ConnectFootprintView,
    ContactUsView, AddLanguageView, DisplayDateView, CopyFootprintView,
    SignS3View, ModerationView, VerifyFootprintView,
    FootprintSearchView, ExportFootprintSearch, VerifiedFootprintFeed)
from footprints.main.viewsets import (
    BookCopyViewSet, ImprintViewSet, ActorViewSet,
    ExtendedDateViewSet, FootprintViewSet, LanguageViewSet,
    PersonViewSet, PlaceViewSet, RoleViewSet, WrittenWorkViewSet,
    StandardizedIdentificationViewSet, DigitalFormatViewSet,
    DigitalObjectViewSet, StandardizedIdentificationTypeViewSet,
    AlternatePlaceNameViewSet)
from footprints.pathmapper.views import (
    PathmapperView, BookCopySearchView, PathmapperTableView,
    PathmapperRouteView, PathmapperEventViewSet)


admin.autodiscover()

router = routers.DefaultRouter()
router.register(r'actor', ActorViewSet)
router.register(r'altname', AlternatePlaceNameViewSet, basename='altname')
router.register(r'book', BookCopyViewSet, basename='book')
router.register(r'digitalformat', DigitalFormatViewSet)
router.register(r'digitalobject', DigitalObjectViewSet)
router.register(r'edtf', ExtendedDateViewSet)
router.register(r'footprint', FootprintViewSet, basename='footprint')
router.register(r'identifiertype', StandardizedIdentificationTypeViewSet)
router.register(r'identifier', StandardizedIdentificationViewSet)
router.register(r'imprint', ImprintViewSet, basename='imprint')
router.register(r'language', LanguageViewSet)
router.register(r'person', PersonViewSet)
router.register(r'place', PlaceViewSet, basename='place')
router.register(r'role', RoleViewSet)
router.register(r'writtenwork', WrittenWorkViewSet, basename='writtenwork'),
router.register(r'events', PathmapperEventViewSet, basename='event')
urlpatterns = router.urls


urlpatterns = [
    url(r'^$', views.IndexView.as_view()),

    path('cas/login', cas_views.LoginView.as_view(),
         name='cas_ng_login'),
    path('cas/logout', cas_views.LogoutView.as_view(),
         name='cas_ng_logout'),

    # password change & reset. overriding to gate them.
    url(r'^accounts/password_change/$',
        login_required(PasswordChangeView.as_view()),
        name='password_change'),
    url(r'^accounts/password_change/done/$',
        login_required(PasswordChangeDoneView.as_view()),
        name='password_change_done'),
    url(r'^password/reset/$',
        PasswordResetView.as_view(),
        name='password_reset'),
    url(r'^password/reset/done/$', PasswordResetDoneView.as_view(),
        name='password_reset_done'),
    url(r'^password/reset/confirm/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/$',
        PasswordResetConfirmView.as_view(),
        name='password_reset_confirm'),
    url(r'^password/reset/complete/$',
        PasswordResetCompleteView.as_view(), name='password_reset_complete'),

    url(r'^accounts/register/$',
        RegistrationView.as_view(form_class=CustomRegistrationForm),
        name='registration_register'),
    url(r'^accounts/', include('registration.backends.default.urls')),

    url(r'^accounts/', include('django.contrib.auth.urls')),

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
    url(r'^footprint/verify/(?P<pk>\d+)/$', VerifyFootprintView.as_view(),
        name='verify-footprint-view'),

    url(r'^footprint/(?P<pk>\d+)/$',
        FootprintDetailView.as_view(), name='footprint-detail-view'),

    url(r'^writtenwork/(?P<pk>\d+)/(?P<imprint>\d+)/'
        r'(?P<copy>\d+)/(?P<footprint>\d+)/$',
        WrittenWorkDetailView.as_view(),
        name='writtenwork-detail-view-footprint'),
    url(r'^writtenwork/(?P<pk>\d+)/(?P<imprint>\d+)/(?P<copy>\d+)/$',
        WrittenWorkDetailView.as_view(),
        name='writtenwork-detail-view-copy'),
    url(r'^writtenwork/(?P<pk>\d+)/(?P<imprint>\d+)/$',
        WrittenWorkDetailView.as_view(),
        name='writtenwork-detail-view-imprint'),
    url(r'^writtenwork/(?P<pk>\d+)/$',
        WrittenWorkDetailView.as_view(), name='writtenwork-detail-view'),

    url(r'^export/footprints/$',
        ExportFootprintSearch.as_view(),
        name='export-footprint-list'),

    url(r'^date/display/$',
        DisplayDateView.as_view(), name='display-date-view'),

    url(r'^search/book/', BookCopySearchView.as_view(),
        name='bookcopy-search-view'),
    url(r'^search/', FootprintSearchView.as_view(), name='search'),

    url(r'^api-auth/', include('rest_framework.urls',
                               namespace='rest_framework')),
    url(r'^api/', include(router.urls)),
    url(r'^api/title/$', TitleListView.as_view()),
    url(r'^api/name/$', NameListView.as_view()),

    # Contact us forms.
    url(r'^contact/success/$',
        TemplateView.as_view(template_name='main/contact_success.html')),
    url(r'^contact/$', ContactUsView.as_view()),

    # Batch Import
    url(r'^batch/', include('footprints.batch.urls')),

    # Moderation Interface
    url(r'^moderate/', ModerationView.as_view(), name='moderation-view'),

    # Rss Feeds
    url(r'^feed/verified/$', VerifiedFootprintFeed()),

    url(r'^admin/', admin.site.urls),
    url(r'^_impersonate/', include('impersonate.urls')),
    url(r'^stats/$', TemplateView.as_view(template_name="stats.html")),
    url(r'smoketest/', include('smoketest.urls')),
    url(r'infranil/', include('infranil.urls')),
    url(r'^uploads/(?P<path>.*)$',
        serve, {'document_root': settings.MEDIA_ROOT}),
    url(r'^sign_s3/$', SignS3View.as_view()),

    url(r'^pathmapper/route/',
        PathmapperRouteView.as_view(), name='pathmapper-route-view'),
    url(r'^pathmapper/table/',
        PathmapperTableView.as_view(), name='pathmapper-table-view'),
    url(r'^pathmapper/vision/',
        TemplateView.as_view(template_name='design/pathmapper.html')),
    url(r'^pathmapper/', PathmapperView.as_view(), name='pathmapper-view'),

    url(r'^adminactions/', include('adminactions.urls')),

    # Temporary table view template for pathmapper
    url(r'^tableview/',
        TemplateView.as_view(template_name='pathmapper/table.html')),

    # Swagger API Viewer
    path('api/schema/', login_required(SpectacularAPIView.as_view()),
         name='schema'),
    path('api/schema/swagger-ui/',
         login_required(SpectacularSwaggerView.as_view(url_name='schema')),
         name='swagger-ui'),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ]
