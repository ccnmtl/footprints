from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import logout as auth_logout_view
from django.core.urlresolvers import reverse
from django.db.models.query_utils import Q
from django.http.response import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.views.generic.base import TemplateView, View
from django.views.generic.detail import DetailView
from djangowind.views import logout as wind_logout_view
from haystack.query import SearchQuerySet
from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from rest_framework.renderers import JSONPRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

from footprints.main.models import (Footprint, Imprint, BookCopy,
                                    Actor, Person, Name, Role, WrittenWork,
                                    Language)
from footprints.main.permissions import IsOwnerOrReadOnly, IsStaffOrReadOnly
from footprints.main.serializers import TitleSerializer, NameSerializer, \
    FootprintSerializer, LanguageSerializer, RoleSerializer
from footprints.mixins import (JSONResponseMixin, LoggedInMixin,
                               EditableMixin)


class IndexView(TemplateView):
    template_name = "main/index.html"


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


class PersonDetailView(EditableMixin, DetailView):

    model = Person

    def get_context_data(self, **kwargs):
        context = super(PersonDetailView, self).get_context_data(**kwargs)

        related = []
        context['related'] = related
        return context


class FootprintDetailView(EditableMixin, LoggedInMixin, DetailView):

    model = Footprint

    def get_context_data(self, **kwargs):
        context = super(FootprintDetailView, self).get_context_data(**kwargs)

        related = []
        if self.object.book_copy.imprint.work is None:
            # written works, imprints & footprints with similar titles
            sqs = SearchQuerySet().autocomplete(title=self.object.title)
            serializer = TitleSerializer(sqs, many=True)
            related.extend(serializer.data)

        context['related'] = related
        context['editable'] = self.has_edit_permission(self.request.user,
                                                       self.object)
        context['languages'] = Language.objects.all().order_by('name')
        return context


class PlaceDetailView(EditableMixin, DetailView):

    model = Actor

    def get_context_data(self, **kwargs):
        context = super(PersonDetailView, self).get_context_data(**kwargs)

        related = []
        context['related'] = related
        context['editable'] = self.has_edit_permission(self.request.user,
                                                       self.object)
        return context


class WrittenWorkDetailView(EditableMixin, DetailView):

    model = WrittenWork

    def get_context_data(self, **kwargs):
        context = super(WrittenWorkDetailView, self).get_context_data(**kwargs)

        related = []
        context['related'] = related
        context['editable'] = self.has_edit_permission(self.request.user,
                                                       self.object)
        return context


class CreateFootprintView(LoggedInMixin, TemplateView):
    template_name = "record/create_footprint.html"

    def get_or_create_author(self, name_id, full_name):
        author_role = Role.objects.get_author_role()

        if len(name_id) == 0:
            name = Name.objects.create(name=full_name)
            person = Person.objects.create(name=name)
            return Actor.objects.create(person=person, role=author_role)
        else:
            # Is there an Actor with this name & the author role?
            authors = Actor.objects.filter(Q(actor_name__id=name_id) |
                                           Q(person__name__id=name_id),
                                           role=author_role)
            # Pick up actor name first
            authors = authors.order_by('actor_name', 'person__name')

            # return the first match
            if authors.count() > 0:
                return authors.first()

            # Get the associated Person with this name & create the author role
            person = Person.objects.get(name__id=name_id)
            return Actor.objects.create(person=person, role=author_role)

    def get_names(self):
        names = []
        prefix = 'author_'
        for key, value in self.request.POST.items():
            if key.startswith(prefix):
                names.append((key[len(prefix):], value))
        return sorted(names)

    def post(self, *args, **kwargs):
        # Create stub objects for the footprint
        imprint = Imprint.objects.create()
        book_copy = BookCopy.objects.create(imprint=imprint)

        for name in self.get_names():
            actor = self.get_or_create_author(name[0], name[1])
            imprint.actor.add(actor)

        title = self.request.POST.get('footprint-title')
        provenance = self.request.POST.get('footprint-provenance')
        medium = self.request.POST.get('footprint-medium')
        notes = self.request.POST.get('footprint-notes', '')
        fp = Footprint.objects.create(title=title, medium=medium,
                                      provenance=provenance,
                                      book_copy=book_copy,
                                      notes=notes)

        url = reverse('footprint-detail-view', kwargs={'pk': fp.pk})
        return HttpResponseRedirect(url)


class FootprintRemoveActorView(LoggedInMixin, JSONResponseMixin, View):

    def post(self, *args, **kwargs):
        footprint_id = kwargs.get('footprint_id', None)
        footprint = get_object_or_404(Footprint, pk=footprint_id)

        actor_id = self.request.POST.get('actor_id', None)
        actor = get_object_or_404(Actor, pk=actor_id)
        footprint.actor.remove(actor)
        return self.render_to_json_response({'success': True})


class FootprintAddActorView(LoggedInMixin, JSONResponseMixin, View):

    def post(self, *args, **kwargs):
        footprint_id = kwargs.get('footprint_id', None)
        footprint = get_object_or_404(Footprint, pk=footprint_id)

        return self.render_to_json_response({
            'success': True,
            'footprint_id': footprint.id
        })


class TitleListView(APIView):
    renderer_classes = (JSONPRenderer,)
    permission_classes = (AllowAny,)

    def get(self, request, format=None):
        sqs = SearchQuerySet().autocomplete(
            title=request.GET.get('q', ''))
        serializer = TitleSerializer(sqs, many=True)
        return Response(serializer.data)


class NameListView(APIView):
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


class FootprintViewSet(viewsets.ModelViewSet):
    queryset = Footprint.objects.all()
    serializer_class = FootprintSerializer
    permission_classes = (IsOwnerOrReadOnly,)


class LanguageViewSet(viewsets.ModelViewSet):
    queryset = Language.objects.all()
    serializer_class = LanguageSerializer
    permission_classes = (IsStaffOrReadOnly,)


class RoleViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = (IsStaffOrReadOnly,)
