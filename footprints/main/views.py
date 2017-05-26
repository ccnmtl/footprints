import csv

from django.apps import apps
from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import logout as auth_logout_view
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.db.models.fields import FieldDoesNotExist
from django.db.models.fields.related import ManyToManyField
from django.db.models.query import Prefetch
from django.db.models.query_utils import Q
from django.http.response import HttpResponseRedirect, StreamingHttpResponse
from django.shortcuts import get_object_or_404
from django.template import loader
from django.views.generic.base import TemplateView, View
from django.views.generic.detail import DetailView
from django.views.generic.edit import FormView
from django.views.generic.list import ListView
from djangowind.views import logout as wind_logout_view
from haystack.generic_views import SearchView
from haystack.query import SearchQuerySet
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_jsonp.renderers import JSONPRenderer
from s3sign.views import SignS3View as BaseSignS3View

from footprints.main.forms import DigitalObjectForm, ContactUsForm, \
    SUBJECT_CHOICES, ExtendedDateForm, FootprintSearchForm
from footprints.main.models import (
    Footprint, Actor, Person, Role, WrittenWork, Language,
    Place, Imprint, BookCopy, StandardizedIdentification,
    StandardizedIdentificationType, ExtendedDate, MEDIUM_CHOICES)
from footprints.main.serializers import NameSerializer
from footprints.main.templatetags.moderation import moderation_footprints
from footprints.main.utils import string_to_point
from footprints.mixins import (
    JSONResponseMixin, LoggedInMixin, ModerationAccessMixin,
    AddChangeAccessMixin)


# returns important setting information for all web pages.
def django_settings(request):
    return {'settings':
            {'GOOGLE_MAP_API': getattr(settings, 'GOOGLE_MAP_API', '')}}


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


class FootprintDetailView(DetailView):

    model = Footprint

    def can_edit(self, user):
        return user.has_perms(AddChangeAccessMixin.permission_required)

    def is_creator(self, user):
        return user.groups.filter(name='Creator').exists()

    def has_perm(self, user, can_edit, is_creator, obj):
        if not can_edit:
            return False

        if not is_creator:
            return True

        return obj.created_by == user

    def permissions(self, user, obj):
        can_edit = self.can_edit(user)
        creator = self.is_creator(user)

        return {
            'can_edit_footprint':
                self.has_perm(user, can_edit, creator, obj),
            'can_edit_copy':
                self.has_perm(user, can_edit, creator, obj.book_copy),
            'can_edit_imprint':
                self.has_perm(user, can_edit, creator,
                              obj.book_copy.imprint),
            'can_edit_work':
                self.has_perm(user, can_edit, creator,
                              obj.book_copy.imprint.work),
        }

    def get_context_data(self, **kwargs):
        context = super(FootprintDetailView, self).get_context_data(**kwargs)

        context['related'] = []
        context['languages'] = Language.objects.all().order_by('name')
        context['roles'] = Role.objects.all().order_by('name')
        context['identifier_types'] = \
            StandardizedIdentificationType.objects.all().order_by('name')
        context['mediums'] = MEDIUM_CHOICES
        context.update(self.permissions(self.request.user, self.get_object()))
        return context


SORT_OPTIONS = {
    'added': {
        'label': 'Added',
        'q': ['-created_at']
    },
    'complete': {
        'label': 'Complete',
        'q': ['percent_complete']
    },
    'fdate': {
        'label': 'Footprint Date',
    },
    'flocation': {
        'label': 'Footprint Location',
    },
    'ftitle': {
        'label': 'Footprint',
        'q': ['title']
    },
    'owners': {
        'label': 'Owners'
    },
    'wtitle': {
        'label': 'Literary Work',
        'q': ['book_copy__imprint__work__title']
    },
}


class FootprintSearchView(SearchView):
    model = Footprint
    form_class = FootprintSearchForm
    template_name = 'main/footprint_advanced_search.html'
    paginate_by = 15
    facet_fields = [
        'footprint_location', 'imprint_location', 'actor']

    def get_queryset(self):
        sqs = super(FootprintSearchView, self).get_queryset()

        # @todo - this is only required when the form is unbound
        # work through the flow to see if this can be removed
        sqs = sqs.filter(django_ct='main.footprint')

        # Sort logic is located here rather than in the SearchForm
        # The first view is "unbound" and retrieves all Footprints
        # as such, the sort needs to happen here rather than in the form
        sort_by = self.request.GET.get('sort_by', 'ftitle')
        direction = self.request.GET.get('direction', 'asc')
        if direction == 'desc':
            sort_by = '-{}'.format(sort_by)

        return sqs.order_by(sort_by)

    def get_context_data(self, **kwargs):
        context = super(FootprintSearchView, self).get_context_data(**kwargs)

        base = reverse('search')
        context['base_url'] = u'{}?page='.format(base)

        query = self.request.GET.get('q', '')
        export = reverse('export-footprint-list')
        context['export_url'] = u'{}?q={}'.format(export, query)

        if context['form'].is_bound:
            for field in self.facet_fields:
                counts = self.queryset.facet(field).facet_counts()
                if 'fields' in counts:
                    context[field] = counts['fields'][field]

        context['search_criteria'] = (
            self.request.GET.get('q') or
            self.request.GET.get('footprint_start_year') or
            self.request.GET.get('footprint_end_year'))

        return context


class FootprintListView(ListView):
    model = Footprint
    template_name = 'main/footprint_list.html'
    paginate_by = 15

    def get_sort_by(self):
        sort_by = self.kwargs.get('sort_by')
        if sort_by in SORT_OPTIONS.keys():
            return sort_by

        return 'ftitle'

    def get_context_data(self, **kwargs):
        context = super(FootprintListView, self).get_context_data(**kwargs)
        context['sort_options'] = SORT_OPTIONS

        sort_by = self.get_sort_by()
        direction = self.request.GET.get('direction', 'asc')
        query = self.request.GET.get('q', '')

        context['selected_sort'] = sort_by
        context['direction'] = direction
        context['query'] = query

        base = reverse('browse-footprint-list', args=[sort_by])
        context['base_url'] = \
            u'{}?direction={}&q={}&page='.format(base, direction, query)

        export = reverse('export-footprint-list')
        context['export_url'] = u'{}?q={}'.format(export, query)

        return context

    def sort_by_date(self, qs, direction):
        lst = list(qs)
        lst.sort(reverse=direction == 'desc',
                 key=lambda obj: obj.sort_date())
        return lst

    def sort_by_place(self, qs, direction):
        lst = list(qs)
        lst.sort(reverse=direction == 'desc',
                 key=lambda obj:
                 obj.place.__unicode__() if obj.place else '')
        return lst

    def format_owner(self, obj):
        actors = [actor.display_name() for actor in obj.owners()]
        return ', '.join(actors)

    def sort_by_owner(self, qs, direction):
        owners = Actor.objects.filter(
            role__name=Role.OWNER).select_related('person')
        qs = qs.prefetch_related(
            Prefetch('actor', queryset=owners, to_attr='owners'))
        lst = list(qs)
        lst.sort(reverse=direction == 'desc',
                 key=lambda obj: self.format_owner(obj))
        return lst

    def default_sort(self, qs, sort_by, direction):
        qs = qs.order_by(*SORT_OPTIONS[sort_by]['q'])
        if direction == 'asc':
            return qs
        else:
            return qs.reverse()

    def filter(self, qs):
        q = self.request.GET.get('q', '')
        if len(q) < 1:
            return qs

        return qs.filter(
            Q(title__icontains=q) |
            Q(book_copy__imprint__work__title__icontains=q) |
            Q(actor__person__name__icontains=q) |
            Q(book_copy__imprint__work__actor__person__name__icontains=q))

    def get_queryset(self):
        sort_by = self.get_sort_by()
        direction = self.request.GET.get('direction', 'asc')

        qs = super(FootprintListView, self).get_queryset()
        qs = self.filter(qs)
        qs = qs.select_related(
            'book_copy', 'associated_date', 'place').prefetch_related(
            'digital_object',
            'book_copy__imprint__publication_date',
            'book_copy__imprint__actor__person',
            'book_copy__imprint__place')

        if sort_by == 'fdate':
            return self.sort_by_date(qs, direction)
        elif sort_by == 'flocation':
            return self.sort_by_place(qs, direction)
        elif sort_by == 'owners':
            return self.sort_by_owner(qs, direction)
        else:
            return self.default_sort(qs, sort_by, direction)


class Echo(object):
        """An object that implements just the write method of the file-like
        interface.
        """
        def write(self, value):
            """
            Write the value by returning it, instead of storing in a buffer.
            """
            return value


class ExportFootprintListView(FootprintListView):
    def get_rows(self):
        headers = ['Footprint Title', 'Footprint Date', 'Footprint Location',
                   'Footprint Owners', 'Written Work Title',
                   'Imprint Display Title', 'Imprint Printers',
                   'Imprint Publication Date', 'Imprint Creation Date',
                   'Footprint Percent Complete', 'Literary Work LOC',
                   'Imprint Actor and Role', 'Imprint BHB Number',
                   'Imprint OCLC Number', 'Evidence Type', 'Evidence Location',
                   'Evidence Call Number', 'Evidence Details']

        yield headers

        for o in self.object_list:
            row = []
            # Footprint title
            row.append(unicode(o.title).encode('utf-8'))
            # Footprint date
            row.append(unicode(o.associated_date))

            # Footprint location
            row.append(unicode(o.place).encode('utf-8'))

            # owners
            a = [owner.display_name().encode('utf-8') for owner in o.owners()]
            row.append('; '.join(a))

            # Written work title
            row.append(unicode(o.book_copy.imprint.work.title).encode('utf-8'))

            # Imprint display_title
            a = unicode(o.book_copy.imprint.display_title()).encode('utf-8')
            row.append(a)

            # Imprint Printers
            a = [p.display_name().encode('utf-8')
                 for p in o.book_copy.imprint.printers()]
            row.append('; '.join(a))

            # Imprint publication date
            row.append(unicode(o.book_copy.imprint.publication_date))

            # Imprint created at date
            row.append(o.created_at.strftime('%m/%d/%Y'))

            # Footprint percent complete
            row.append(o.percent_complete)

            # Literary work LOC
            loc_id = o.book_copy.imprint.work\
                .get_library_of_congress_identifier()
            unicode(loc_id).encode('utf-8')
            row.append(loc_id)

            # Imprint actor
            actors = [unicode(p).encode('utf-8')
                      for p in o.book_copy.imprint.actor.all()]
            row.append('; '.join(actors))

            # Imprint BHB
            if o.book_copy.imprint.has_bhb_number():
                row.append(unicode(o.book_copy
                                    .imprint.get_bhb_number()
                                    .identifier).encode('utf-8'))
            else:
                row.append('')

            # Imprint OCLC #
            if o.book_copy.imprint.has_oclc_number():
                row.append(unicode(o.book_copy
                                   .imprint.get_oclc_number()
                                   .identifier).encode('utf-8'))
            else:
                row.append('')

            # Evidence type
            row.append(unicode(o.medium).encode('utf-8'))

            # Evidence location
            row.append(unicode(o.provenance).encode('utf-8'))

            # Evidence source
            row.append(unicode(o.call_number).encode('utf-8'))

            # Evidence details
            row.append(unicode(o.notes).encode('utf-8'))
            yield row

    def get(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        rows = self.get_rows()
        pseudo_buffer = Echo()
        writer = csv.writer(pseudo_buffer)

        fnm = "footprints.csv"
        response = StreamingHttpResponse(
            (writer.writerow(row) for row in rows), content_type="text/csv"
        )
        response['Content-Disposition'] = 'attachment; filename="' + fnm + '"'
        return response


class WrittenWorkDetailView(DetailView):

    model = WrittenWork

    def get_context_data(self, **kwargs):
        context = super(WrittenWorkDetailView, self).get_context_data(**kwargs)

        context['related'] = []
        context['imprints'] = self.object.imprints()
        context['state'] = {
            'imprint': self.kwargs.get('imprint', None),
            'copy': self.kwargs.get('copy', None),
            'footprint': self.kwargs.get('footprint', None)
        }
        return context


class CreateFootprintView(LoggedInMixin, AddChangeAccessMixin, TemplateView):
    template_name = "record/create_footprint.html"

    def get_context_data(self, **kwargs):
        context = TemplateView.get_context_data(self, **kwargs)
        context['mediums'] = MEDIUM_CHOICES
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


class ConnectFootprintView(LoggedInMixin, AddChangeAccessMixin, View):
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


class RemoveRelatedView(LoggedInMixin, AddChangeAccessMixin,
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
            field = the_model._meta.get_field(attr)

            model_name = field.rel.to._meta.model_name
            the_model = apps.get_model(app_label='main', model_name=model_name)
            the_child = get_object_or_404(
                the_model, pk=self.request.POST.get('child_id', None))

            # m2m?
            if isinstance(field, ManyToManyField):
                return self.removeManyToMany(the_parent, the_child, attr)
            else:
                return self.removeForeignKey(the_parent, the_child, attr)

        except (ValueError, FieldDoesNotExist):
            return self.render_to_json_response({'success': False})


class AddRelatedRecordView(LoggedInMixin, AddChangeAccessMixin,
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

        if len(languages) < 1 or len(languages[0]) < 1:
            # remove all languages
            the_parent.language.clear()
            return self.render_to_json_response({'success': True})

        # remove all language that are not in the posted list
        to_remove = the_parent.language.exclude(id__in=languages)
        the_parent.language.remove(*to_remove)

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

        try:
            place, created = Place.objects.get_or_create(
                city=self.request.POST.get('city', ''),
                country=self.request.POST.get('country', ''),
                latlng=string_to_point(position))
        except Place.MultipleObjectsReturned:
            place = Place.objects.filter(
                city=self.request.POST.get('city', ''),
                country=self.request.POST.get('country', ''),
                latlng=string_to_point(position)).first()

        the_parent.place = place
        the_parent.save()

        return self.render_to_json_response({'success': True})


class AddDigitalObjectView(AddRelatedRecordView):

    def post(self, *args, **kwargs):
        the_parent = self.get_parent()

        form = DigitalObjectForm(self.request.POST)
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
        sender = settings.SERVER_EMAIL
        recipients = (getattr(settings, 'CONTACT_US_EMAIL'),)

        tmpl = loader.get_template('main/contact_notification_email.txt')
        send_mail(subject, tmpl.render(form_data), sender, recipients)

        return super(ContactUsView, self).form_valid(form)


class SignS3View(LoggedInMixin, BaseSignS3View):
    root = "uploads/"

    def get_bucket(self):
        return settings.AWS_STORAGE_BUCKET_NAME


class ModerationView(LoggedInMixin, ModerationAccessMixin, TemplateView):
    template_name = 'main/moderation.html'

    def get_context_data(self, **kwargs):
        context = super(ModerationView, self).get_context_data(**kwargs)
        context['footprints'] = moderation_footprints()
        return context


class VerifyFootprintView(LoggedInMixin, ModerationAccessMixin, View):

    def post(self, *args, **kwargs):
        verified = self.request.POST.get('verified')

        fp = get_object_or_404(Footprint, pk=kwargs.get('pk'))
        fp.save_verified(verified == '1')

        url = reverse('footprint-detail-view', kwargs={'pk': fp.pk})
        return HttpResponseRedirect(url)
