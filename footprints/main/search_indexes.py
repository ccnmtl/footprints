import re

from haystack import indexes
from haystack.fields import CharField
from unidecode import unidecode

from footprints.main.models import WrittenWork, Footprint, Person, Place


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


class WrittenWorkIndex(indexes.SearchIndex, indexes.Indexable):
    object_id = CharField(model_attr='id')
    object_type = CharField()
    text = indexes.NgramField(document=True, use_template=True)
    title = indexes.NgramField(model_attr='title', null=True)
    sort_by = CharField()

    def get_model(self):
        return WrittenWork

    def prepare_object_type(self, obj):
        return type(obj).__name__

    def prepare_sort_by(self, obj):
        return format_sort_by(obj.title, remove_articles=True)


class FootprintIndex(indexes.SearchIndex, indexes.Indexable):
    object_id = CharField(model_attr='id')
    object_type = CharField()
    text = indexes.NgramField(document=True, use_template=True)
    title = indexes.NgramField(model_attr='title')
    sort_by = CharField()

    def get_model(self):
        return Footprint

    def prepare_object_type(self, obj):
        return type(obj).__name__

    def prepare_sort_by(self, obj):
        return format_sort_by(obj.title, remove_articles=True)


class PersonIndex(indexes.SearchIndex, indexes.Indexable):
    object_id = CharField(model_attr='id')
    object_type = CharField()
    text = indexes.NgramField(document=True, use_template=True)
    name = indexes.NgramField(model_attr='name')
    sort_by = CharField()

    def get_model(self):
        return Person

    def prepare_object_type(self, obj):
        return type(obj).__name__

    def prepare_sort_by(self, obj):
        return format_sort_by(obj.name, remove_articles=True)


class PlaceIndex(indexes.SearchIndex, indexes.Indexable):
    object_id = CharField(model_attr='id')
    object_type = CharField()
    text = indexes.NgramField(document=True, use_template=True)
    sort_by = CharField()

    def get_model(self):
        return Place

    def prepare_object_type(self, obj):
        return type(obj).__name__

    def prepare_sort_by(self, obj):
        return format_sort_by(obj.__unicode__(), remove_articles=True)
