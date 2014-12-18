from haystack import indexes
from haystack.fields import CharField

from footprints.main.models import WrittenWork, Imprint, Footprint, Actor, \
    Person


class WrittenWorkIndex(indexes.SearchIndex, indexes.Indexable):
    object_id = CharField(model_attr='id')
    text = indexes.NgramField(document=True, use_template=True)
    title = indexes.NgramField(model_attr='title')

    def get_model(self):
        return WrittenWork


class ImprintIndex(indexes.SearchIndex, indexes.Indexable):
    object_id = CharField(model_attr='id')
    text = indexes.NgramField(document=True, use_template=True)
    title = indexes.NgramField(model_attr='title')

    def get_model(self):
        return Imprint


class FootprintIndex(indexes.SearchIndex, indexes.Indexable):
    object_id = CharField(model_attr='id')
    text = indexes.NgramField(document=True, use_template=True)
    title = indexes.NgramField(model_attr='title')

    def get_model(self):
        return Footprint


class ActorIndex(indexes.SearchIndex, indexes.Indexable):
    object_id = CharField(model_attr='id')
    text = indexes.NgramField(document=True, use_template=True)
    name = indexes.NgramField()
    role = CharField(model_attr='role')

    def get_model(self):
        return Actor

    def prepare_name(self, obj):
        return obj.actor_name.__unicode__() if obj.actor_name else ''

    def prepare_role(self, obj):
        return obj.role.name


class PersonIndex(indexes.SearchIndex, indexes.Indexable):
    object_id = CharField(model_attr='id')
    text = indexes.NgramField(document=True, use_template=True)
    name = indexes.NgramField()

    def get_model(self):
        return Person

    def prepare_name(self, obj):
        return obj.__unicode__()
