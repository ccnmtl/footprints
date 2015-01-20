from haystack import indexes
from haystack.fields import CharField

from footprints.main.models import WrittenWork, Imprint, Footprint, Actor, \
    Person, Name


class WrittenWorkIndex(indexes.SearchIndex, indexes.Indexable):
    object_id = CharField(model_attr='id')
    object_type = CharField()
    text = indexes.NgramField(document=True, use_template=True)
    title = indexes.NgramField(model_attr='title')

    def get_model(self):
        return WrittenWork

    def prepare_object_type(self, obj):
        return type(obj).__name__


class ImprintIndex(indexes.SearchIndex, indexes.Indexable):
    object_id = CharField(model_attr='id')
    object_type = CharField()
    text = indexes.NgramField(document=True, use_template=True)
    title = indexes.NgramField(model_attr='title')

    def get_model(self):
        return Imprint

    def prepare_object_type(self, obj):
        return type(obj).__name__

    def index_queryset(self, using=None):
        "Used when the entire index for model is updated."
        return self.get_model().objects.filter(work__isnull=False)


class FootprintIndex(indexes.SearchIndex, indexes.Indexable):
    object_id = CharField(model_attr='id')
    object_type = CharField()
    text = indexes.NgramField(document=True, use_template=True)
    title = indexes.NgramField(model_attr='title')

    def get_model(self):
        return Footprint

    def prepare_object_type(self, obj):
        return type(obj).__name__


class ActorIndex(indexes.SearchIndex, indexes.Indexable):
    object_id = CharField(model_attr='id')
    object_type = CharField()
    text = indexes.NgramField(document=True, use_template=True)
    role = CharField(model_attr='role')

    def get_model(self):
        return Actor

    def prepare_role(self, obj):
        return obj.role.name

    def prepare_object_type(self, obj):
        return type(obj).__name__


class PersonIndex(indexes.SearchIndex, indexes.Indexable):
    object_id = CharField(model_attr='id')
    object_type = CharField()
    text = indexes.NgramField(document=True, use_template=True)
    name = indexes.NgramField(model_attr='full_name')

    def get_model(self):
        return Person

    def prepare_object_type(self, obj):
        return type(obj).__name__
