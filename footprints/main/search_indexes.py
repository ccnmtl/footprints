import re

from haystack import indexes
from unidecode import unidecode

from celery_haystack.indexes import CelerySearchIndex
from footprints.main.models import WrittenWork, Footprint, Person, Place, \
    Imprint


def format_sort_by(sort_term, remove_articles=False):
    ''' processes text for sorting field:
        * converts non-ASCII characters to ASCII equivalents
        * converts to lowercase
        * (optional) remove leading a/the
        * removes outside spaces
    '''
    sort_term = unidecode(sort_term).lower().strip()
    if remove_articles:
        sort_term = re.sub(r'^(a\s+|the\s+)', '', sort_term)
    return sort_term


class WrittenWorkIndex(CelerySearchIndex, indexes.Indexable):
    object_id = indexes.CharField(model_attr='id')
    object_type = indexes.CharField()
    text = indexes.NgramField(document=True, use_template=True)
    title = indexes.NgramField(model_attr='title', null=True)
    sort_by = indexes.CharField()

    def get_model(self):
        return WrittenWork

    def prepare_object_type(self, obj):
        return type(obj).__name__

    def prepare_sort_by(self, obj):
        return format_sort_by(obj.__unicode__(), remove_articles=True)


class ImprintIndex(CelerySearchIndex, indexes.Indexable):
    object_id = indexes.CharField(model_attr='id')
    object_type = indexes.CharField()
    text = indexes.NgramField(document=True, use_template=True)
    title = indexes.NgramField(model_attr='title', null=True)

    def get_model(self):
        return Imprint

    def prepare_object_type(self, obj):
        return type(obj).__name__


class FootprintIndex(CelerySearchIndex, indexes.Indexable):
    object_id = indexes.CharField(model_attr='id')
    object_type = indexes.CharField()
    text = indexes.NgramField(document=True, use_template=True)
    title = indexes.NgramField(model_attr='title')
    sort_by = indexes.CharField()

    # custom sort fields
    added = indexes.DateTimeField(model_attr='created_at')
    complete = indexes.IntegerField(model_attr='percent_complete')
    ftitle = indexes.CharField()
    fdate = indexes.DateTimeField()
    flocation = indexes.NgramField()
    owners = indexes.CharField()
    wtitle = indexes.CharField()

    def get_model(self):
        return Footprint

    def prepare_object_type(self, obj):
        return type(obj).__name__

    def prepare_sort_by(self, obj):
        return format_sort_by(obj.title, remove_articles=True)

    def prepare_ftitle(self, obj):
        try:
            return format_sort_by(obj.title, remove_articles=True)
        except AttributeError:
            return ''

    def prepare_flocation(self, obj):
        if obj.place:
            return obj.place.__unicode__()

        return ''

    def prepare_fdate(self, obj):
        return obj.sort_date()

    def prepare_wtitle(self, obj):
        try:
            return format_sort_by(obj.book_copy.imprint.work.title,
                                  remove_articles=True)
        except AttributeError:
            return ''

    def prepare_owners(self, obj):
        a = [o.display_name() for o in obj.owners()]
        return format_sort_by(', '.join(a), remove_articles=True)


class PersonIndex(CelerySearchIndex, indexes.Indexable):
    object_id = indexes.CharField(model_attr='id')
    object_type = indexes.CharField()
    text = indexes.NgramField(document=True, use_template=True)
    name = indexes.NgramField(model_attr='name')
    sort_by = indexes.CharField()

    def get_model(self):
        return Person

    def prepare_object_type(self, obj):
        return type(obj).__name__

    def prepare_sort_by(self, obj):
        return format_sort_by(obj.name, remove_articles=True)


class PlaceIndex(CelerySearchIndex, indexes.Indexable):
    object_id = indexes.CharField(model_attr='id')
    object_type = indexes.CharField()
    text = indexes.NgramField(document=True, use_template=True)
    sort_by = indexes.CharField()

    def get_model(self):
        return Place

    def prepare_object_type(self, obj):
        return type(obj).__name__

    def prepare_sort_by(self, obj):
        return format_sort_by(obj.__unicode__(), remove_articles=True)
