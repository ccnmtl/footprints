import re

from celery_haystack.indexes import CelerySearchIndex
from django.db.models.query_utils import Q
from django.utils.encoding import smart_text
from haystack.constants import Indexable
from haystack.fields import CharField, NgramField, DateTimeField, \
    IntegerField, MultiValueField, BooleanField
from unidecode import unidecode

from footprints.main.models import WrittenWork, Footprint, Person, Place, \
    Imprint, Actor, BookCopy


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


class WrittenWorkIndex(CelerySearchIndex, Indexable):
    object_id = CharField(model_attr='id')
    object_type = CharField()
    text = NgramField(document=True, use_template=True)
    title = NgramField(model_attr='title', null=True)
    sort_by = CharField()

    def get_model(self):
        return WrittenWork

    def prepare_object_type(self, obj):
        return type(obj).__name__

    def prepare_sort_by(self, obj):
        return format_sort_by(smart_text(obj), remove_articles=True)


class ImprintIndex(CelerySearchIndex, Indexable):
    object_id = CharField(model_attr='id')
    object_type = CharField()
    text = NgramField(document=True, use_template=True)
    title = NgramField(model_attr='title', null=True)

    def get_model(self):
        return Imprint

    def prepare_object_type(self, obj):
        return type(obj).__name__


class BookCopyIndex(CelerySearchIndex, Indexable):
    object_id = CharField(model_attr='id')
    object_type = CharField()
    text = NgramField(document=True, use_template=True)

    work_id = CharField(model_attr='imprint__work__id')
    imprint_id = CharField(model_attr='imprint__id')

    imprint_location = CharField(model_attr='imprint__place__id')
    pub_start_date = DateTimeField()
    pub_end_date = DateTimeField()

    footprint_start_date = DateTimeField()
    footprint_end_date = DateTimeField()
    footprint_locations = MultiValueField()

    actor = MultiValueField(faceted=True)

    # custom sort fields
    fdate = DateTimeField()

    def get_model(self):
        return BookCopy

    def prepare_object_type(self, obj):
        return type(obj).__name__

    def prepare_footprints_end_date(self, obj):
        return obj.footprint_end_date()

    def prepare_footprints_start_date(self, obj):
        return obj.footprint_start_date()

    def prepare_pub_end_date(self, obj):
        return obj.imprint.end_date()

    def prepare_pub_start_date(self, obj):
        return obj.imprint.start_date()

    def prepare_footprint_locations(self, obj):
        places = []
        for f in obj.footprints():
            if f.place:
                places.append(f.place.id)
        return places

    def prepare_actor(self, obj):
        qs = Actor.objects.filter(
            Q(writtenwork=obj.imprint.work) |
            Q(imprint=obj.imprint) |
            Q(footprint__book_copy=obj)).distinct()

        return [smart_text(actor) for actor in qs]


class FootprintIndex(CelerySearchIndex, Indexable):
    object_id = CharField(model_attr='id')
    object_type = CharField()
    text = NgramField(document=True, use_template=True)
    title = NgramField(model_attr='title')
    sort_by = CharField()

    footprint_start_date = DateTimeField()
    footprint_end_date = DateTimeField()

    pub_start_date = DateTimeField()
    pub_end_date = DateTimeField()

    footprint_location = CharField(faceted=True)
    imprint_location = CharField(faceted=True)

    actor = MultiValueField(faceted=True)

    has_image = BooleanField()

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

    def prepare_object_type(self, obj):
        return type(obj).__name__

    def prepare_sort_by(self, obj):
        return format_sort_by(obj.title, remove_articles=True)

    def prepare_ftitle(self, obj):
        return format_sort_by(obj.title, remove_articles=True)

    def prepare_flocation(self, obj):
        if obj.place:
            return smart_text(obj.place)

        return ''

    def prepare_fdate(self, obj):
        return obj.sort_date()

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
            return smart_text(obj.place)

        return ''

    def prepare_imprint_location(self, obj):
        if obj.book_copy.imprint.place:
            return smart_text(obj.book_copy.imprint.place)

        return ''

    def prepare_actor(self, obj):
        qs = Actor.objects.filter(
            Q(writtenwork=obj.book_copy.imprint.work) |
            Q(imprint=obj.book_copy.imprint) |
            Q(footprint=obj)).distinct()

        return [smart_text(actor) for actor in qs]

    def prepare_has_image(self, obj):
        return obj.has_at_least_one_digital_object()


class PersonIndex(CelerySearchIndex, Indexable):
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


class PlaceIndex(CelerySearchIndex, Indexable):
    object_id = CharField(model_attr='id')
    object_type = CharField()
    text = NgramField(document=True, use_template=True)
    sort_by = CharField()

    def get_model(self):
        return Place

    def prepare_object_type(self, obj):
        return type(obj).__name__

    def prepare_sort_by(self, obj):
        return format_sort_by(smart_text(obj), remove_articles=True)
