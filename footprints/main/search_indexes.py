from haystack import indexes
from haystack.fields import CharField

from footprints.main.models import WrittenWork, Imprint, Footprint


class BaseIndex(indexes.SearchIndex):
    text = CharField(document=True, use_template=True)
    title = CharField()

    # We add this for autocomplete.
    title_auto = indexes.NgramField(model_attr='title')

    class Meta:
        abstract = True

    def prepare_title(self, obj):
        if getattr(obj, 'title'):
            return obj.title
        return ''


class WrittenWorkIndex(BaseIndex, indexes.Indexable):
    def get_model(self):
        return WrittenWork


class ImprintIndex(BaseIndex, indexes.Indexable):
    def get_model(self):
        return Imprint


class FootprintIndex(BaseIndex, indexes.Indexable):
    def get_model(self):
        return Footprint
