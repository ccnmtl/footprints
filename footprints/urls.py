from django.conf import settings
from django.urls import include, path, re_path
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import (
    PasswordChangeDoneView, PasswordResetDoneView, PasswordResetConfirmView,
    PasswordResetCompleteView, PasswordChangeView, PasswordResetView)
from django.views.generic import TemplateView
from django.views.static import serve
from django_cas_ng import views as cas_views
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from registration.backends.default.views import RegistrationView
from rest_framework import routers

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
    AlternatePlaceNameViewSet, DigitalObjectExtendedViewSet)
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
router.register(r'digitalobjectex', DigitalObjectExtendedViewSet)
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
    path('', views.IndexView.as_view()),

    path('cas/login', cas_views.LoginView.as_view(),
         name='cas_ng_login'),
    path('cas/logout', cas_views.LogoutView.as_view(),
         name='cas_ng_logout'),

    # password change & reset. overriding to gate them.
    path('accounts/password_change/',
         login_required(PasswordChangeView.as_view()),
         name='password_change'),
    path('accounts/password_change/done/',
         login_required(PasswordChangeDoneView.as_view()),
         name='password_change_done'),
    path('password/reset/',
         PasswordResetView.as_view(),
         name='password_reset'),
    path('password/reset/done/', PasswordResetDoneView.as_view(),
         name='password_reset_done'),
    re_path(
        r'password/reset/confirm/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/',
        PasswordResetConfirmView.as_view(),
        name='password_reset_confirm'),
    path('password/reset/complete/',
         PasswordResetCompleteView.as_view(), name='password_reset_complete'),

    path('accounts/register/',
         RegistrationView.as_view(form_class=CustomRegistrationForm),
         name='registration_register'),
    path('accounts/', include('registration.backends.default.urls')),

    path('accounts/', include('django.contrib.auth.urls')),

    path('actor/add/',
         AddActorView.as_view(), name='add-actor-view'),
    path('language/add/',
         AddLanguageView.as_view(), name='add-language-view'),
    path('place/add/',
         AddPlaceView.as_view(), name='add-place-view'),
    path('date/add/',
         AddDateView.as_view(), name='add-date-view'),
    path('identifier/add/',
         AddIdentifierView.as_view(), name='add-identifier-view'),
    path('digitalobject/add/',
         AddDigitalObjectView.as_view(), name='add-digital-object-view'),

    path('remove/related/',
         RemoveRelatedView.as_view(), name='remove-related'),

    path('footprint/create/', CreateFootprintView.as_view(),
         name='create-footprint-view'),
    path('footprint/connect/<int:pk>/', ConnectFootprintView.as_view(),
         name='connect-footprint-view'),
    path('footprint/copy/<int:pk>/', CopyFootprintView.as_view(),
         name='copy-footprint-view'),
    path('footprint/verify/<int:pk>/', VerifyFootprintView.as_view(),
         name='verify-footprint-view'),

    path('footprint/<int:pk>/',
         FootprintDetailView.as_view(), name='footprint-detail-view'),

    path('writtenwork/<int:pk>/<int:imprint>/<int:copy>/<int:footprint>/',
         WrittenWorkDetailView.as_view(),
         name='writtenwork-detail-view-footprint'),
    path('writtenwork/<int:pk>/<int:imprint>/<int:copy>/',
         WrittenWorkDetailView.as_view(),
         name='writtenwork-detail-view-copy'),
    path('writtenwork/<int:pk>/<int:imprint>/',
         WrittenWorkDetailView.as_view(),
         name='writtenwork-detail-view-imprint'),
    path('writtenwork/<int:pk>/',
         WrittenWorkDetailView.as_view(), name='writtenwork-detail-view'),

    path('export/footprints/',
         ExportFootprintSearch.as_view(),
         name='export-footprint-list'),

    path('date/display/',
         DisplayDateView.as_view(), name='display-date-view'),

    re_path(r'^search/book/', BookCopySearchView.as_view(),
            name='bookcopy-search-view'),
    re_path(r'^search/', FootprintSearchView.as_view(), name='search'),

    re_path(r'^api-auth/', include('rest_framework.urls',
                                   namespace='rest_framework')),
    re_path(r'^api/', include(router.urls)),
    path('api/title/', TitleListView.as_view()),
    path('api/name/', NameListView.as_view()),

    # Contact us forms.
    path('contact/success/',
         TemplateView.as_view(template_name='main/contact_success.html')),
    path('contact/', ContactUsView.as_view()),

    # Batch Import
    re_path(r'^batch/', include('footprints.batch.urls')),

    # Moderation Interface
    path('moderate/', ModerationView.as_view(), name='moderation-view'),

    # Rss Feeds
    path('feed/verified/', VerifiedFootprintFeed()),

    path('admin/', admin.site.urls),
    path('_impersonate/', include('impersonate.urls')),
    path('stats/', TemplateView.as_view(template_name="stats.html")),
    path(r'smoketest/', include('smoketest.urls')),
    path('uploads/<path>',
         serve, {'document_root': settings.MEDIA_ROOT}),
    path('sign_s3/', SignS3View.as_view()),

    re_path(r'^pathmapper/route/',
            PathmapperRouteView.as_view(), name='pathmapper-route-view'),
    re_path(r'^pathmapper/table/',
            PathmapperTableView.as_view(), name='pathmapper-table-view'),
    re_path(r'^pathmapper/vision/',
            TemplateView.as_view(template_name='design/pathmapper.html')),
    re_path(r'^pathmapper/', PathmapperView.as_view(), name='pathmapper-view'),

    path('adminactions/', include('adminactions.urls')),

    # Temporary table view template for pathmapper
    path('tableview/',
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
        path('__debug__/', include(debug_toolbar.urls)),
    ]
