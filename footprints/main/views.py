from django.apps import apps
from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import logout as auth_logout_view
from django.core.urlresolvers import reverse
from django.http.response import HttpResponseRedirect, HttpResponseForbidden
from django.shortcuts import get_object_or_404
from django.views.generic.base import TemplateView, View
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from djangowind.views import logout as wind_logout_view
from haystack.query import SearchQuerySet
from rest_framework.permissions import AllowAny
from rest_framework.renderers import JSONPRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

from footprints.main.forms import DigitalObjectForm
from footprints.main.models import (
    Footprint, Actor, Person, Role, WrittenWork, Language, ExtendedDateFormat,
    Place, Imprint, BookCopy, IDENTIFIER_TYPES, StandardizedIdentification)
from footprints.main.serializers import NameSerializer
from footprints.mixins import (
    JSONResponseMixin, LoggedInMixin, EditableMixin)


class IndexView(TemplateView):
    template_name = "main/index.html"

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)

        context['footprint_count'] = Footprint.objects.count()
        return context


class LoginView(JSONResponseMixin, View):

    def post(self, request):
        request.session.set_test_cookie()
        login_form = AuthenticationForm(request, request.POST)
        if login_form.is_valid():
            login(request, login_form.get_user())
            if request.user is not None:
                next_url = request.POST.get('next', '/')
                return self.render_to_json_response({'next': next_url})

        return self.render_to_json_response({'error': True})


class LogoutView(LoggedInMixin, View):

    def get(self, request):
        if hasattr(settings, 'CAS_BASE'):
            return wind_logout_view(request, next_page="/")
        else:
            return auth_logout_view(request, "/")


class PersonDetailView(EditableMixin, LoggedInMixin, DetailView):

    model = Person

    def get_context_data(self, **kwargs):
        context = super(PersonDetailView, self).get_context_data(**kwargs)

        context['related'] = []
        return context


class FootprintDetailView(EditableMixin, LoggedInMixin, DetailView):

    model = Footprint

    def get_context_data(self, **kwargs):
        context = super(FootprintDetailView, self).get_context_data(**kwargs)

        context['related'] = []
        context['editable'] = self.has_edit_permission(self.request.user,
                                                       self.object)
        context['languages'] = Language.objects.all().order_by('name')
        context['roles'] = Role.objects.all().order_by('name')
        context['identifier_types'] = IDENTIFIER_TYPES
        return context


class FootprintListView(LoggedInMixin, ListView):
    model = Footprint
    default_sort = ['title']
    paginate_by = 20

    def get_context_data(self, **kwargs):
        context = super(FootprintListView, self).get_context_data(**kwargs)
        return context

    def get_queryset(self):
        qs = super(FootprintListView, self).get_queryset()
        qs = qs.order_by(*self.default_sort)
        return qs


class PlaceDetailView(EditableMixin, LoggedInMixin, DetailView):

    model = Place

    def get_context_data(self, **kwargs):
        context = super(PlaceDetailView, self).get_context_data(**kwargs)

        context['related'] = []
        context['editable'] = self.has_edit_permission(self.request.user,
                                                       self.object)
        return context


class WrittenWorkDetailView(EditableMixin, LoggedInMixin, DetailView):

    model = WrittenWork

    def get_context_data(self, **kwargs):
        context = super(WrittenWorkDetailView, self).get_context_data(**kwargs)

        context['related'] = []
        context['editable'] = self.has_edit_permission(self.request.user,
                                                       self.object)
        return context


class CreateFootprintView(LoggedInMixin, TemplateView):
    template_name = "record/create_footprint.html"

    def get_context_data(self, **kwargs):
        context = TemplateView.get_context_data(self, **kwargs)
        context['mediums'] = Footprint.MEDIUM_CHOICES
        return context

    def post(self, *args, **kwargs):
        title = self.request.POST.get('footprint-title')
        provenance = self.request.POST.get('footprint-provenance')
        medium = self.request.POST.get('footprint-medium')
        description = self.request.POST.get('footprint-medium-description')
        notes = self.request.POST.get('footprint-notes', '')

        work = WrittenWork.objects.create()
        imprint = Imprint.objects.create(work=work)
        book_copy = BookCopy.objects.create(imprint=imprint)
        fp = Footprint.objects.create(title=title,
                                      medium=medium,
                                      medium_description=description,
                                      provenance=provenance, notes=notes,
                                      book_copy=book_copy)

        url = reverse('footprint-detail-view', kwargs={'pk': fp.pk})
        return HttpResponseRedirect(url)


class ConnectFootprintView(LoggedInMixin, EditableMixin, View):
    CREATE_ID = '0'

    def get_or_create_work(self, pk):
        if pk == self.CREATE_ID:
            work = WrittenWork.objects.create()
        else:
            work = get_object_or_404(WrittenWork, pk=pk)

        return work

    def get_or_create_imprint(self, pk, work):
        if pk == self.CREATE_ID or len(pk) == 0:
            imprint = Imprint.objects.create(work=work)
        else:
            imprint = get_object_or_404(Imprint, pk=pk)

        return imprint

    def get_or_create_copy(self, pk, imprint):
        if pk == self.CREATE_ID or len(pk) == 0:
            copy = BookCopy.objects.create(imprint=imprint)
        else:
            copy = get_object_or_404(BookCopy, pk=pk)

        return copy

    def post(self, *args, **kwargs):
        fp = get_object_or_404(Footprint, pk=kwargs.get('pk', None))
        if not self.has_edit_permission(self.request.user, fp):
            return HttpResponseForbidden()

        pk = self.request.POST.get('work', self.CREATE_ID)
        work = self.get_or_create_work(pk)

        pk = self.request.POST.get('imprint', self.CREATE_ID)
        imprint = self.get_or_create_imprint(pk, work)

        pk = self.request.POST.get('copy', self.CREATE_ID)
        copy = self.get_or_create_copy(pk, imprint)

        fp.book_copy = copy
        fp.save()

        url = reverse('footprint-detail-view', kwargs={'pk': fp.pk})
        return HttpResponseRedirect(url)


class RemoveRelatedView(LoggedInMixin, EditableMixin,
                        JSONResponseMixin, View):

    def post(self, *args, **kwargs):
        try:
            model_name = self.request.POST.get('parent_model', None)
            the_model = apps.get_model(app_label='main', model_name=model_name)

            the_parent = get_object_or_404(
                the_model, pk=self.request.POST.get('parent_id', None))
        except ValueError:
            return self.render_to_json_response({'success': False})

        if not self.has_edit_permission(self.request.user, the_parent):
            return HttpResponseForbidden()

        # cheating a bit here. @todo - make this totally generic
        # will need to figure out whether related is FK or M2M
        success = True
        actor_id = self.request.POST.get('actor_id', None)
        associateddate_id = self.request.POST.get('associateddate_id', None)
        publicationdate_id = self.request.POST.get('publicationdate_id', None)
        identifier_id = self.request.POST.get('identifier_id', None)
        place_id = self.request.POST.get('place_id', None)

        if actor_id:
            actor = get_object_or_404(Actor, id=actor_id)
            the_parent.actor.remove(actor)
        elif associateddate_id:
            the_date = get_object_or_404(ExtendedDateFormat,
                                         id=associateddate_id)
            if the_parent.associated_date == the_date:
                the_parent.associated_date = None
                the_parent.save()
        elif publicationdate_id:
            the_date = get_object_or_404(ExtendedDateFormat,
                                         id=publicationdate_id)
            if the_parent.date_of_publication == the_date:
                the_parent.date_of_publication = None
                the_parent.save()
        elif place_id:
            place = get_object_or_404(Place, id=place_id)
            if the_parent.place == place:
                the_parent.place = None
                the_parent.save()
        elif identifier_id:
            identifier = get_object_or_404(StandardizedIdentification,
                                           id=identifier_id)
            the_parent.standardized_identifier.remove(identifier)
        else:
            success = False

        return self.render_to_json_response({'success': success})


class AddRelatedRecordView(LoggedInMixin, EditableMixin,
                           JSONResponseMixin, View):

    def get_parent(self):
        parent_model = self.request.POST.get('parent_model', None)
        the_model = apps.get_model(app_label='main', model_name=parent_model)

        parent_id = self.request.POST.get('parent_id', None)
        the_parent = get_object_or_404(the_model, pk=parent_id)
        return the_parent


class AddActorView(AddRelatedRecordView):

    def create_actor(self, person_id, person_name, role, alias):
        try:
            person = Person.objects.get(pk=person_id)
        except (Person.DoesNotExist, ValueError):
            person = None

        if person is None or person.name != person_name:
            person = Person.objects.create(name=person_name)

        return Actor.objects.create(person=person, role=role, alias=alias)

    def post(self, *args, **kwargs):
        the_parent = self.get_parent()

        if not self.has_edit_permission(self.request.user, the_parent):
            return HttpResponseForbidden()

        role = get_object_or_404(Role, pk=self.request.POST.get('role', None))

        person_name = self.request.POST.get('person_name', None)
        person_id = self.request.POST.get('person_id', None)
        alias = self.request.POST.get('alias', None)

        actor = self.create_actor(person_id, person_name, role, alias)
        the_parent.actor.add(actor)

        return self.render_to_json_response({'success': True})


class AddDateView(AddRelatedRecordView):

    def post(self, *args, **kwargs):
        the_parent = self.get_parent()

        attr = self.request.POST.get('attr', None)

        if not self.has_edit_permission(self.request.user, the_parent):
            return HttpResponseForbidden()

        date_string = self.request.POST.get('date_string', None)
        if date_string is not None:
            edtf = ExtendedDateFormat.objects.create(edtf_format=date_string)
            setattr(the_parent, attr, edtf)
            the_parent.save()

            return self.render_to_json_response({'success': True})
        else:
            return self.render_to_json_response({
                'success': False,
                'error': 'Please enter a date'
            })


class AddIdentifierView(AddRelatedRecordView):

    def post(self, *args, **kwargs):
        the_parent = self.get_parent()

        if not self.has_edit_permission(self.request.user, the_parent):
            return HttpResponseForbidden()

        identifier_type = self.request.POST.get('identifier_type', None)
        identifier = self.request.POST.get('identifier', None)

        if identifier is None or identifier_type is None:
            return self.render_to_json_response({
                'success': False,
                'error': 'Please enter identifier information'
            })
        else:
            si = StandardizedIdentification.objects.create(
                identifier=identifier, identifier_type=identifier_type)
            the_parent.standardized_identifier.add(si)
            return self.render_to_json_response({'success': True})


class AddPlaceView(AddRelatedRecordView):

    def post(self, *args, **kwargs):
        the_parent = self.get_parent()

        if not self.has_edit_permission(self.request.user, the_parent):
            return HttpResponseForbidden()

        position = self.request.POST.get('position', '')
        if len(position) < 1:
            return self.render_to_json_response({
                'success': False,
                'error': 'Please specify a position'
            })

        place, created = Place.objects.get_or_create(
            city=self.request.POST.get('city', ''),
            country=self.request.POST.get('country', ''),
            position=position)

        the_parent.place = place
        the_parent.save()

        return self.render_to_json_response({'success': True})


class AddDigitalObjectView(AddRelatedRecordView):

    def post(self, *args, **kwargs):
        the_parent = self.get_parent()

        if not self.has_edit_permission(self.request.user, the_parent):
            return HttpResponseForbidden()

        form = DigitalObjectForm(self.request.POST, self.request.FILES)
        if not form.is_valid():
            return self.render_to_json_response({'success': False})
        else:
            the_object = form.save()
            the_parent.digital_object.add(the_object)
        return self.render_to_json_response({'success': True})


class TitleListView(LoggedInMixin, JSONResponseMixin, View):

    def get(self, request, *args, **kwargs):
        sqs = SearchQuerySet().autocomplete(title=request.GET.get('q', ''))

        object_type = request.GET.get('object_type', None)
        if object_type:
            sqs = sqs.filter(object_type=object_type)

        titles = list(set(sqs.values_list('title', flat=True)))
        titles.sort()

        return self.render_to_json_response(titles)


class NameListView(LoggedInMixin, APIView):
    renderer_classes = (JSONPRenderer,)
    permission_classes = (AllowAny,)

    def get(self, request, format=None):
        q = request.GET.get('q', '')
        if len(q) > 0:
            sqs = SearchQuerySet().autocomplete(name=q)
            serializer = NameSerializer(sqs, many=True)
            return Response(serializer.data)
        else:
            return Response({})
