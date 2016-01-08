from django.apps import apps
from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import logout as auth_logout_view
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.db.models.fields import FieldDoesNotExist
from django.db.models.fields.related import ManyToManyField
from django.http.response import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.template import loader
from django.template.context import Context
from django.views.generic.base import TemplateView, View
from django.views.generic.detail import DetailView
from django.views.generic.edit import FormView
from django.views.generic.list import ListView
from djangowind.views import logout as wind_logout_view
from haystack.query import SearchQuerySet
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_jsonp.renderers import JSONPRenderer

from footprints.main.forms import DigitalObjectForm, ContactUsForm, \
    SUBJECT_CHOICES, ExtendedDateForm
from footprints.main.models import (
    Footprint, Actor, Person, Role, WrittenWork, Language,
    Place, Imprint, BookCopy, StandardizedIdentification,
    StandardizedIdentificationType, ExtendedDate)
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


class PersonDetailView(EditableMixin, DetailView):

    model = Person

    def get_context_data(self, **kwargs):
        context = super(PersonDetailView, self).get_context_data(**kwargs)

        context['related'] = []
        return context


class FootprintDetailView(EditableMixin, DetailView):

    model = Footprint

    def get_context_data(self, **kwargs):
        context = super(FootprintDetailView, self).get_context_data(**kwargs)

        context['related'] = []
        context['editable'] = self.has_edit_permission(self.request.user)
        context['languages'] = Language.objects.all().order_by('name')
        context['roles'] = Role.objects.all().order_by('name')
        context['identifier_types'] = \
            StandardizedIdentificationType.objects.all().order_by('name')
        context['mediums'] = Footprint.MEDIUM_CHOICES
        return context


class FootprintListView(ListView):
    model = Footprint
    sort_options = {
        'wtitle': {
            'label': 'Literary Work',
            'q': ['book_copy__imprint__work__title']
        },
        'ftitle': {
            'label': 'Footprint',
            'q': ['title']
        },
        'added': {
            'label': 'Added',
            'q': ['-created_at']
        },
        'elocation': {
            'label': 'Evidence Location',
            'q': ['provenance']
        },
        'complete': {
            'label': 'Complete',
            'q': ['percent_complete']
        }
    }
    paginate_by = 15

    def get_context_data(self, **kwargs):
        context = super(FootprintListView, self).get_context_data(**kwargs)
        context['sort_options'] = self.sort_options

        sort_by = self.kwargs.get('sort_by', 'ftitle')
        context['selected_sort'] = sort_by
        context['selected_sort_label'] = self.sort_options[sort_by]['label']
        context['direction'] = self.request.GET.get('direction', 'asc')
        return context

    def get_queryset(self):
        sort_by = self.kwargs.get('sort_by', 'ftitle')
        direction = self.request.GET.get('direction', 'asc')

        qs = super(FootprintListView, self).get_queryset()
        qs = qs.order_by(*self.sort_options[sort_by]['q'])
        if direction == 'asc':
            return qs
        else:
            return qs.reverse()


class PlaceDetailView(EditableMixin, DetailView):

    model = Place

    def get_context_data(self, **kwargs):
        context = super(PlaceDetailView, self).get_context_data(**kwargs)

        context['related'] = []
        context['editable'] = self.has_edit_permission(self.request.user)
        return context


class WrittenWorkDetailView(EditableMixin, DetailView):

    model = WrittenWork

    def get_context_data(self, **kwargs):
        context = super(WrittenWorkDetailView, self).get_context_data(**kwargs)

        context['related'] = []
        context['editable'] = self.has_edit_permission(self.request.user)
        context['imprints'] = self.object.imprints()
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


class CopyFootprintView(ConnectFootprintView):

    def post(self, *args, **kwargs):
        fp = get_object_or_404(Footprint, pk=kwargs.get('pk', None))

        new_fp = Footprint()
        new_fp.medium = self.request.POST.get('footprint-medium')
        new_fp.title = self.request.POST.get('footprint-title')
        new_fp.provenance = self.request.POST.get(
            'footprint-provenance')
        new_fp.medium_description = self.request.POST.get(
            'footprint-medium-description')
        new_fp.call_number = self.request.POST.get('footprint-call-number')

        pk = self.request.POST.get('imprint', self.CREATE_ID)
        imprint = self.get_or_create_imprint(pk, fp.book_copy.imprint.work)

        pk = self.request.POST.get('copy', self.CREATE_ID)
        new_fp.book_copy = self.get_or_create_copy(pk, imprint)

        new_fp.save()

        if self.request.POST.get('copy-images', False) == '1':
            for do in fp.digital_object.all():
                new_fp.digital_object.add(do)

        url = reverse('footprint-detail-view', kwargs={'pk': new_fp.pk})
        return HttpResponseRedirect(url)


class RemoveRelatedView(LoggedInMixin, EditableMixin,
                        JSONResponseMixin, View):

    def removeForeignKey(self, the_parent, the_child, attr):
        current = getattr(the_parent, attr)
        if current != the_child:
            return self.render_to_json_response({'success': False})
        else:
            setattr(the_parent, attr, None)
            the_parent.save()

            # dates are a OneToOne relationship
            # delete once the relationship is removed
            if isinstance(current, ExtendedDate):
                current.delete()

            return self.render_to_json_response({'success': True})

    def removeManyToMany(self, the_parent, the_child, attr):
        m2m = getattr(the_parent, attr)
        m2m.remove(the_child)
        return self.render_to_json_response({'success': True})

    def post(self, *args, **kwargs):
        try:
            model_name = self.request.POST.get('parent_model', None)
            the_model = apps.get_model(app_label='main', model_name=model_name)
            the_parent = get_object_or_404(
                the_model, pk=self.request.POST.get('parent_id', None))

            attr = self.request.POST.get('attr', None)
            field = the_model._meta.get_field_by_name(attr)

            model_name = field[0].rel.to._meta.model_name
            the_model = apps.get_model(app_label='main', model_name=model_name)
            the_child = get_object_or_404(
                the_model, pk=self.request.POST.get('child_id', None))

            # m2m?
            if isinstance(field[0], ManyToManyField):
                return self.removeManyToMany(the_parent, the_child, attr)
            else:
                return self.removeForeignKey(the_parent, the_child, attr)

        except (ValueError, FieldDoesNotExist):
            return self.render_to_json_response({'success': False})


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

        role = get_object_or_404(Role, pk=self.request.POST.get('role', None))

        person_name = self.request.POST.get('person_name', None)
        person_id = self.request.POST.get('person_id', None)
        alias = self.request.POST.get('alias', None)

        actor = self.create_actor(person_id, person_name, role, alias)
        the_parent.actor.add(actor)

        return self.render_to_json_response({'success': True})


class AddDateView(AddRelatedRecordView):

    def post(self, *args, **kwargs):
        form = ExtendedDateForm(self.request.POST)
        if not form.is_valid():
            return self.render_to_json_response({
                'success': False,
                'msg': form.get_error_messages()
            })
        else:
            the_parent = self.get_parent()
            edtf = form.save()
            setattr(the_parent, form.get_attr(), edtf)
            the_parent.save()

            return self.render_to_json_response({'success': True})


class DisplayDateView(JSONResponseMixin, View):
    def post(self, *args, **kwargs):
        form = ExtendedDateForm(self.request.POST)

        if not form.is_valid():
            return self.render_to_json_response({
                'success': False,
                'msg': form.get_error_messages()
            })
        else:
            return self.render_to_json_response({
                'success': True,
                'display': form.get_extended_date().__unicode__()
            })


class AddIdentifierView(AddRelatedRecordView):

    def post(self, *args, **kwargs):
        the_parent = self.get_parent()

        slug = self.request.POST.get('identifier_type', None)
        identifier_type = get_object_or_404(StandardizedIdentificationType,
                                            slug=slug)
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


class AddLanguageView(AddRelatedRecordView):

    def post(self, *args, **kwargs):
        the_parent = self.get_parent()

        languages = self.request.POST.getlist('language')

        # delete all language that are not in the posted list
        the_parent.language.exclude(id__in=languages).delete()

        # add all languages. (no-op if already exists)
        for lid in languages:
            the_parent.language.add(Language.objects.get(id=lid))

        return self.render_to_json_response({'success': True})


class AddPlaceView(AddRelatedRecordView):

    def post(self, *args, **kwargs):
        the_parent = self.get_parent()

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


class ContactUsView(FormView):
    template_name = 'main/contact.html'
    form_class = ContactUsForm
    success_url = "/contact/success/"

    def get_initial(self):
        initial = super(ContactUsView, self).get_initial()
        if not self.request.user.is_anonymous():
            initial['name'] = self.request.user.get_full_name()
            initial['email'] = self.request.user.email
        initial['subject'] = '-----'

        return initial

    def form_valid(self, form):
        subject = "Footprints Contact Us Request"
        form_data = form.cleaned_data

        if not self.request.user.is_anonymous():
            form_data['username'] = self.request.user.username

        form_data['subject'] = dict(SUBJECT_CHOICES)[form_data['subject']]

        # POST to the support email
        sender = form_data['email']
        recipients = (getattr(settings, 'CONTACT_US_EMAIL'),)

        tmpl = loader.get_template('main/contact_notification_email.txt')
        send_mail(subject, tmpl.render(Context(form_data)), sender, recipients)

        return super(ContactUsView, self).form_valid(form)
