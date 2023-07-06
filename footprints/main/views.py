import csv

from django.apps import apps
from django.conf import settings
from django.contrib.syndication.views import Feed
from django.core.mail import send_mail
from django.core.exceptions import FieldDoesNotExist
from django.db.models.fields.related import ManyToManyField
from django.http.response import HttpResponseRedirect, StreamingHttpResponse, \
    HttpResponseBadRequest
from django.shortcuts import get_object_or_404
from django.template import loader
from django.urls.base import reverse
from django.utils.encoding import smart_text
from django.views.generic.base import TemplateView, View
from django.views.generic.detail import DetailView
from django.views.generic.edit import FormView
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
    StandardizedIdentificationType, ExtendedDate, MEDIUM_CHOICES,
    work_actor_changed, CanonicalPlace)
from footprints.main.serializers import NameSerializer
from footprints.main.templatetags.moderation import moderation_footprints
from footprints.main.utils import interpolate_role_actors, string_to_point
from footprints.mixins import (
    JSONResponseMixin, LoggedInMixin, ModerationAccessMixin,
    AddChangeAccessMixin)


# returns important setting information for all web pages.
def django_settings(request):
    return {
        'settings':
            {
                'GOOGLE_MAP_API': getattr(settings, 'GOOGLE_MAP_API', ''),
                'GEONAMES_KEY': getattr(settings, 'GEONAMES_KEY', '')
            }
    }


class IndexView(TemplateView):
    template_name = "main/index.html"

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)

        context['footprint_count'] = Footprint.objects.count()
        return context


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


class BaseSearchView(SearchView):
    model = Footprint
    form_class = FootprintSearchForm

    def get_queryset(self):
        sqs = super(BaseSearchView, self).get_queryset()

        # @todo - this is only required when the form is unbound
        # work through the flow to see if this can be removed
        sqs = sqs.filter(django_ct='main.footprint')

        # Sort logic is located here rather than in the SearchForm
        # The first view is "unbound" and retrieves all Footprints
        # as such, the sort needs to happen here rather than in the form
        sort_by = self.request.GET.get('sort_by', 'ftitle')
        if sort_by not in SORT_OPTIONS.keys():
            sort_by = 'ftitle'

        direction = self.request.GET.get('direction', 'asc')
        if direction not in ['asc', 'desc']:
            direction = 'asc'

        if direction == 'desc':
            sort_by = '-{}'.format(sort_by)

        return sqs.order_by(sort_by)


class FootprintSearchView(BaseSearchView):
    template_name = 'search/search.html'
    paginate_by = 15
    facet_fields = [
        'footprint_location_title', 'imprint_location_title', 'actor_title']

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

        context['gallery_view'] = self.request.GET.get('gallery_view', False)

        return context


class Echo(object):
    """An object that implements just the write method of the file-like
    interface.
    """

    def write(self, value):
        """
        Write the value by returning it, instead of storing in a buffer.
        """
        return value


class ExportFootprintSearch(BaseSearchView):

    def get_header_string(self):
        headers = ['Footprint ID',
                   'Footprint Title', 'Footprint Date', 'Footprint Location',
                   'Footprint Owners', 'Written Work Title',
                   'Imprint Display Title', 'Imprint Printers',
                   'Imprint Publication Date', 'Imprint Creation Date',
                   'Footprint Percent Complete', 'Literary Work LOC',
                   'Imprint Actor and Role', 'Imprint BHB Number',
                   'Imprint OCLC Number', 'Book Copy Call Number',
                   'Evidence Type', 'Evidence Location',
                   'Evidence Call Number', 'Evidence Details']
        for r in Role.objects.for_footprint():
            role = 'Footprint Role ' + smart_text(r.name)\
                + ' Actor'
            headers.append(role)
            headers.append(role + ' VIAF Number')

        for r in Role.objects.for_imprint():
            role = 'Imprint Role: ' + smart_text(r.name) + ' Actor'
            headers.append(role)
            headers.append(role + ' VIAF Number')
        return headers

    # interpolate_role_actors returns a list of already encoded values, these
    # strings do not need to be encoded again.
    def get_footprint_actors_string(self, footprint):
        return interpolate_role_actors(Role.objects.all().for_footprint(),
                                       footprint.actors())

    def get_imprint_actors_string(self, footprint):
        return interpolate_role_actors(Role.objects.all().for_imprint(),
                                       footprint.book_copy.imprint.actor.all())

    def get_rows(self, queryset):
        yield self.get_header_string()

        for search_result in queryset:
            o = search_result.object
            if o is None or type(o) != Footprint:
                # Solr has an indexed object that is not in the database
                continue

            row = []

            # Footprint identifier
            row.append(o.identifier())
            # Footprint title
            row.append(o.title)
            # Footprint date
            row.append(smart_text(o.associated_date))

            # Footprint location
            row.append(smart_text(o.place))

            # owners
            a = [owner.display_name() for owner in o.owners()]
            row.append(smart_text('; '.join(a)))

            # Written work title
            row.append(smart_text(o.book_copy.imprint.work.title))

            # Imprint display_title
            a = smart_text(o.book_copy.imprint.display_title())
            row.append(a)

            # Imprint Printers
            a = [p.display_name()
                 for p in o.book_copy.imprint.printers()]
            row.append(smart_text('; '.join(a)))

            # Imprint publication date
            row.append(smart_text(o.book_copy.imprint.publication_date))

            # Imprint created at date
            row.append(o.created_at.strftime('%m/%d/%Y'))

            # Footprint percent complete
            row.append(o.percent_complete)

            # Literary work LOC
            loc_id = o.book_copy.imprint.work\
                .get_library_of_congress_identifier()
            loc_id = smart_text(loc_id)
            row.append(loc_id)

            # Imprint actor
            actors = [smart_text(p) for p
                      in o.book_copy.imprint.actor.all()]
            row.append('; '.join(actors))

            # Imprint BHB
            if o.book_copy.imprint.has_bhb_number():
                row.append(smart_text(o.book_copy
                                       .imprint.get_bhb_number()
                                       .identifier))
            else:
                row.append('')

            # Imprint OCLC #
            if o.book_copy.imprint.has_oclc_number():
                row.append(smart_text(o.book_copy
                                       .imprint.get_oclc_number()
                                       .identifier))
            else:
                row.append('')

            # Book copy call number
            row.append(smart_text(o.book_copy.call_number))

            # Evidence type
            row.append(smart_text(o.medium))

            # Evidence location
            row.append(smart_text(o.provenance))

            # Evidence source
            row.append(smart_text(o.call_number))

            # Evidence details
            row.append(smart_text(o.notes))

            # Footprint Actors
            row.extend(self.get_footprint_actors_string(o))

            # Imprint Actors
            row.extend(self.get_imprint_actors_string(o))

            yield row

    def get(self, request):
        form_class = self.get_form_class()
        form = self.get_form(form_class)

        if not form.is_valid():
            return HttpResponseBadRequest('')

        queryset = form.search()

        rows = self.get_rows(queryset)
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

        if (isinstance(the_parent, WrittenWork) and
                isinstance(the_child, Actor)):
            work_actor_changed(None, **{'instance': the_parent})

        return self.render_to_json_response({'success': True})

    def post(self, *args, **kwargs):
        try:
            model_name = self.request.POST.get('parent_model', None)
            the_model = apps.get_model(app_label='main', model_name=model_name)
            the_parent = get_object_or_404(
                the_model, pk=self.request.POST.get('parent_id', None))

            attr = self.request.POST.get('attr', None)
            field = the_model._meta.get_field(attr)

            model_name = field.remote_field.model._meta.object_name
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

        if isinstance(the_parent, WrittenWork):
            work_actor_changed(None, **{'instance': the_parent})

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
                'display': smart_text(form.get_extended_date())
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

    def set_place_by_id(self, the_parent):
        try:
            place_id = self.request.POST.get('placeId', '')
            place = Place.objects.get(id=place_id)
            self.set_place(the_parent, place)
        except (Place.DoesNotExist, ValueError):
            return None

    def get_canonical_place(self, gid, position, canonical_name):
        try:
            canonical_place = CanonicalPlace.objects.get(geoname_id=gid)
        except CanonicalPlace.DoesNotExist:
            latlng = string_to_point(position)
            canonical_place, created = CanonicalPlace.objects.get_or_create(
                latlng=latlng, canonical_name=canonical_name)
            canonical_place.geoname_id = gid
            canonical_place.save()

        return canonical_place

    def set_place(self, the_parent, place):
        the_parent.place = place
        the_parent.save()

    def post(self, *args, **kwargs):
        the_parent = self.get_parent()

        if self.set_place_by_id(the_parent):
            return

        position = self.request.POST.get('position', None)
        gid = self.request.POST.get('geonameId', None)
        canonical_name = self.request.POST.get('canonicalName', None)
        if not position or not gid or not canonical_name:
            return self.render_to_json_response({
                'success': False,
                'error': 'Please select a place'
            })

        canonical = self.get_canonical_place(gid, position, canonical_name)
        alt_name = self.request.POST.get('placeName', '')

        place, created = Place.objects.get_or_create(
            alternate_name=alt_name, canonical_place=canonical)

        self.set_place(the_parent, place)
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
        if not self.request.user.is_anonymous:
            initial['name'] = self.request.user.get_full_name()
            initial['email'] = self.request.user.email
        initial['subject'] = '-----'

        return initial

    def form_valid(self, form):
        subject = "Footprints Contact Us Request"
        form_data = form.cleaned_data

        if not self.request.user.is_anonymous:
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


class VerifiedFootprintFeed(Feed):
    title = 'Recently Verified Footprints'
    link = "/feed/verified/"
    description = ('Updates on newly verified footprints '
                   'for the Footprints project')

    def items(self):
        return Footprint.objects.filter(
            verified=True).order_by('-verified_modified_at')[:10]

    def item_title(self, item):
        return item.narrative
