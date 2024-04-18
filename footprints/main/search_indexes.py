import re

from django.utils.encoding import smart_str

from django.db.models.query_utils import Q
from footprints.main.models import WrittenWork, Footprint, Person, Place, \
    Imprint, Actor, BookCopy
from haystack.constants import Indexable
from haystack.fields import CharField, NgramField, DateTimeField, \
    IntegerField, MultiValueField, BooleanField
from unidecode import unidecode
from haystack.indexes import SearchIndex


def format_sort_by(sort_term, remove_articles=False):
    ''' processes text for sorting field:
        * converts non-ASCII characters to ASCII equivalents
        * converts to lowercase
        * (optional) remove leading a/the
        * removes outside spaces
    '''
    try:
        sort_term = unidecode(sort_term).lower().strip()
        if remove_articles:
            sort_term = re.sub(r'^(a\s+|the\s+)', '', sort_term)
        return sort_term
    except AttributeError:
        return ''


class WrittenWorkIndex(SearchIndex, Indexable):
    object_id = CharField(model_attr='id')
    object_type = CharField()
    text = NgramField(document=True, use_template=True)
    title = NgramField(model_attr='title', null=True)
    sort_by = CharField()

    imprint_location = MultiValueField(faceted=True)
    imprint_location_title = MultiValueField(faceted=True)
    pub_start_date = DateTimeField()
    pub_end_date = DateTimeField()

    footprint_location = MultiValueField(faceted=True)
    footprint_location_title = MultiValueField(faceted=True)
    footprint_start_date = DateTimeField()
    footprint_end_date = DateTimeField()

    actor = MultiValueField(faceted=True)
    actor_title = MultiValueField(faceted=True)

    def get_model(self):
        return WrittenWork

    def index_queryset(self, using=None):
        return self.get_model().objects.prefetch_related(
            'imprint_set__bookcopy_set__footprint_set__associated_date',
            'standardized_identifier__identifier_type', 'actor__person')

    def prepare_object_type(self, obj):
        return type(obj).__name__

    def prepare_sort_by(self, obj):
        return format_sort_by(smart_str(obj), remove_articles=True)

    def prepare_footprint_end_date(self, obj):
        return obj.footprints_end_date()

    def prepare_footprint_start_date(self, obj):
        return obj.footprints_start_date()

    def prepare_pub_end_date(self, obj):
        return obj.pub_end_date()

    def prepare_pub_start_date(self, obj):
        return obj.pub_start_date()

    def prepare_footprint_location(self, obj):
        places = []
        for f in obj.footprints():
            if f.place:
                places.append(f.place.canonical_place.id)
        return places

    def prepare_imprint_location(self, obj):
        places = []
        for imprint in obj.imprints():
            if imprint.place:
                places.append(imprint.place.canonical_place.id)
        return places

    def _actors(self, obj):
        footprints = obj.footprints().values_list('id', flat=True)
        imprints = obj.imprint_set.all().values_list('id', flat=True)
        return Actor.objects.filter(
            Q(writtenwork=obj) |
            Q(imprint__in=imprints) |
            Q(footprint__in=footprints)).distinct()

    def prepare_actor(self, obj):
        # prepare all actors associated with this work
        return [actor.id for actor in self._actors(obj)]

    def prepare_actor_title(self, obj):
        # prepare all actors associated with this work
        return [smart_str(actor) for actor in self._actors(obj)]


class ImprintIndex(SearchIndex, Indexable):
    object_id = CharField(model_attr='id')
    object_type = CharField()
    text = NgramField(document=True, use_template=True)
    title = NgramField(model_attr='title', null=True)

    work_id = CharField(model_attr='work__id')

    imprint_location = MultiValueField(faceted=True)
    imprint_location_title = MultiValueField(faceted=True)
    pub_start_date = DateTimeField()
    pub_end_date = DateTimeField()

    footprint_location = MultiValueField(faceted=True)
    footprint_location_title = MultiValueField(faceted=True)
    footprint_start_date = DateTimeField()
    footprint_end_date = DateTimeField()

    actor = MultiValueField(faceted=True)
    actor_title = MultiValueField(faceted=True)

    def get_model(self):
        return Imprint

    def prepare_object_type(self, obj):
        return type(obj).__name__

    def prepare_footprint_end_date(self, obj):
        return obj.footprints_end_date()

    def prepare_footprint_start_date(self, obj):
        return obj.footprints_start_date()

    def prepare_pub_end_date(self, obj):
        return obj.end_date()

    def prepare_pub_start_date(self, obj):
        return obj.start_date()

    def prepare_imprint_location(self, obj):
        if obj.place:
            return [obj.place.canonical_place.id]
        return []

    def prepare_imprint_location_title(self, obj):
        if obj.place:
            return [smart_str(obj.place.canonical_place.canonical_name)]
        return []

    def prepare_footprint_location(self, obj):
        places = []
        for f in obj.footprints():
            if f.place:
                places.append(f.place.canonical_place.id)
        return places

    def prepare_footprint_location_title(self, obj):
        places = []
        for f in obj.footprints():
            if f.place:
                name = f.place.canonical_place.canonical_name
                places.append(smart_str(name))
        return places

    def _actors(self, obj):
        qs = Footprint.objects.filter(book_copy__imprint=obj)
        footprints = qs.values_list('id', flat=True)
        return Actor.objects.filter(
            Q(imprint=obj) |
            Q(footprint__in=footprints)).distinct()

    def prepare_actor(self, obj):
        return [actor.id for actor in self._actors(obj)]

    def prepare_actor_title(self, obj):
        return [smart_str(actor) for actor in self._actors(obj)]


class BookCopyIndex(SearchIndex, Indexable):
    object_id = CharField(model_attr='id')
    object_type = CharField()
    text = NgramField(document=True, use_template=True)

    work_id = CharField(model_attr='imprint__work__id')
    imprint_id = CharField(model_attr='imprint__id')

    imprint_location = MultiValueField(faceted=True)
    imprint_location_title = MultiValueField(faceted=True)

    pub_year = CharField(faceted=True)
    pub_start_date = DateTimeField()
    pub_end_date = DateTimeField()

    footprint_location = MultiValueField(faceted=True)
    footprint_location_title = MultiValueField(faceted=True)
    footprint_start_date = DateTimeField()
    footprint_end_date = DateTimeField()

    actor = MultiValueField(faceted=True)
    actor_title = MultiValueField(faceted=True)

    censored = BooleanField()
    expurgated = BooleanField()

    def get_model(self):
        return BookCopy

    def index_queryset(self, using=None):
        qs = self.get_model().objects.all()
        return qs.select_related(
            'imprint__work',
            'imprint__place__canonical_place').prefetch_related(
            'footprint_set__associated_date',
            'footprint_set__place',
            'footprint_set__actor')

    def prepare_object_type(self, obj):
        return type(obj).__name__

    def prepare_footprint_end_date(self, obj):
        return obj.footprints_end_date()

    def prepare_footprint_start_date(self, obj):
        return obj.footprints_start_date()

    def prepare_pub_year(self, obj):
        dt = obj.imprint.sort_date()
        if dt:
            return dt.year

    def prepare_pub_end_date(self, obj):
        return obj.imprint.end_date()

    def prepare_pub_start_date(self, obj):
        return obj.imprint.start_date()

    def prepare_imprint_location(self, obj):
        if obj.imprint.place:
            return [obj.imprint.place.canonical_place.id]
        return []

    def prepare_imprint_location_title(self, obj):
        if obj.imprint.place:
            name = smart_str(obj.imprint.place.canonical_place.canonical_name)
            return [name]
        return []

    def prepare_footprint_location(self, obj):
        places = []
        for f in obj.footprints():
            if f.place:
                places.append(f.place.canonical_place.id)
        return places

    def prepare_footprint_location_title(self, obj):
        places = []
        for f in obj.footprints():
            if f.place:
                name = smart_str(f.place.canonical_place.canonical_name)
                places.append(name)
        return places

    def prepare_actor(self, obj):
        footprints = obj.footprint_set.all().values_list('id', flat=True)
        qs = Actor.objects.filter(
            Q(writtenwork=obj.imprint.work) |
            Q(imprint=obj.imprint) |
            Q(footprint__in=footprints)).distinct()

        return [actor.id for actor in qs]

    def prepare_actor_title(self, obj):
        footprints = obj.footprint_set.all().values_list('id', flat=True)
        qs = Actor.objects.filter(
            Q(writtenwork=obj.imprint.work) |
            Q(imprint=obj.imprint) |
            Q(footprint__in=footprints)).distinct()

        return [smart_str(actor) for actor in qs]

    def prepare_censored(self, obj):
        return obj.has_censor()

    def prepare_expurgated(self, obj):
        return obj.has_expurgator()


class FootprintIndex(SearchIndex, Indexable):
    object_id = CharField(model_attr='id')
    object_type = CharField()
    text = NgramField(document=True, use_template=True)
    title = NgramField(model_attr='title')
    sort_by = CharField()

    creator = CharField(model_attr='created_by__username')

    work_id = CharField(model_attr='book_copy__imprint__work__id')
    imprint_id = CharField(model_attr='book_copy__imprint__id')
    book_copy_id = CharField(model_attr='book_copy__id')
    book_copy_identifier = CharField()

    imprint_location = MultiValueField(faceted=True)
    imprint_location_title = MultiValueField(faceted=True)
    pub_start_date = DateTimeField()
    pub_end_date = DateTimeField()

    footprint_location = MultiValueField(faceted=True)
    footprint_location_title = MultiValueField(faceted=True)

    footprint_year = CharField(faceted=True)
    footprint_start_date = DateTimeField()
    footprint_end_date = DateTimeField()

    actor = MultiValueField(faceted=True)
    actor_title = MultiValueField(faceted=True)

    has_image = BooleanField()

    is_terminal = BooleanField()

    # custom sort fields
    added = DateTimeField(model_attr='created_at')
    complete = IntegerField(model_attr='percent_complete')
    ftitle = CharField()
    fdate = DateTimeField()
    flocation = CharField()
    owners = CharField()
    wtitle = CharField()

    def get_model(self):
        return Footprint

    def index_queryset(self, using=None):
        qs = self.get_model().objects.all()
        qs = qs.select_related(
            'created_by', 'associated_date', 'place__canonical_place',
            'book_copy__imprint__work', 'book_copy__imprint__place',
            'book_copy__imprint__place__canonical_place').prefetch_related(
                'book_copy__imprint__standardized_identifier__identifier_type',
                'actor__person', 'book_copy__imprint__work__actor')
        return qs

    def prepare_object_type(self, obj):
        return type(obj).__name__

    def prepare_sort_by(self, obj):
        return format_sort_by(obj.title, remove_articles=True)

    def prepare_ftitle(self, obj):
        return format_sort_by(obj.title, remove_articles=True)

    def prepare_flocation(self, obj):
        if obj.place:
            return smart_str(obj.place)

        return ''

    def prepare_fdate(self, obj):
        return obj.sort_date()

    def prepare_footprint_year(self, obj):
        dt = obj.sort_date()
        if dt:
            return dt.year

    def prepare_footprint_end_date(self, obj):
        return obj.end_date()

    def prepare_footprint_start_date(self, obj):
        return obj.start_date()

    def prepare_pub_end_date(self, obj):
        imprint = obj.book_copy.imprint
        return imprint.end_date()

    def prepare_pub_start_date(self, obj):
        imprint = obj.book_copy.imprint
        return imprint.start_date()

    def prepare_wtitle(self, obj):
        return format_sort_by(obj.book_copy.imprint.work.title,
                              remove_articles=True)

    def prepare_owners(self, obj):
        a = [o.display_name() for o in obj.owners()]
        return format_sort_by(', '.join(a), remove_articles=True)

    def prepare_footprint_location(self, obj):
        if obj.place:
            return [obj.place.canonical_place.id]

        return []

    def prepare_footprint_location_title(self, obj):
        if obj.place:
            return [smart_str(obj.place.canonical_place.canonical_name)]

        return []

    def prepare_imprint_location(self, obj):
        if obj.book_copy.imprint.place:
            return [obj.book_copy.imprint.place.canonical_place.id]

        return []

    def prepare_imprint_location_title(self, obj):
        if obj.book_copy.imprint.place:
            place = obj.book_copy.imprint.place
            return [smart_str(place.canonical_place.canonical_name)]

        return []

    def prepare_actor(self, obj):
        qs = Actor.objects.filter(
            Q(writtenwork=obj.book_copy.imprint.work) |
            Q(imprint=obj.book_copy.imprint) |
            Q(footprint=obj)).distinct()

        return [actor.id for actor in qs]

    def prepare_actor_title(self, obj):
        qs = Actor.objects.filter(
            Q(writtenwork=obj.book_copy.imprint.work) |
            Q(imprint=obj.book_copy.imprint) |
            Q(footprint=obj)).distinct()

        return [smart_str(actor) for actor in qs]

    def prepare_has_image(self, obj):
        return obj.has_at_least_one_digital_object()

    def prepare_book_copy_identifier(self, obj):
        return obj.book_copy.identifier()

    def prepare_is_terminal(self, obj):
        return obj.is_terminal()


# PersonIndex is used by the NameListView to create an autocomplete field
class PersonIndex(SearchIndex, Indexable):
    object_id = CharField(model_attr='id')
    object_type = CharField()
    text = NgramField(document=True, use_template=True)
    name = NgramField(model_attr='name')
    sort_by = CharField()

    def get_model(self):
        return Person

    def prepare_object_type(self, obj):
        return type(obj).__name__

    def prepare_sort_by(self, obj):
        return format_sort_by(obj.name, remove_articles=True)


#  @todo: Is this in use?
class PlaceIndex(SearchIndex, Indexable):
    object_id = CharField(model_attr='id')
    object_type = CharField()
    text = NgramField(document=True, use_template=True)
    sort_by = CharField()

    def get_model(self):
        return Place

    def prepare_object_type(self, obj):
        return type(obj).__name__

    def prepare_sort_by(self, obj):
        return format_sort_by(smart_str(obj), remove_articles=True)
