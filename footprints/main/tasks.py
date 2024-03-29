from celery import shared_task
from django.apps import apps
from django.core.exceptions import ImproperlyConfigured
from haystack import connection_router, connections
from haystack.exceptions import NotHandled as IndexNotFoundException


# from django.conf import settings
# This integrates code to add celery 4+ compatability to the celery_haystack
# library. https://github.com/django-haystack/celery-haystack/pull/67/files
# This simplifies the approach where possible.
class IndexOperationException(Exception):
    def __init__(self, index, reason):
        self.index = index
        self.reason = reason

    def __str__(self):
        return "Failed to update index %s. %s" % (self.index, self.reason)


class InstanceNotFoundException(Exception):
    def __init__(self, model_class, pk, reason):
        self.model_class = model_class
        self.pk = pk
        self.reason = reason

    def __str__(self):
        return "Unable to load instance %s with pk=%s. %s" % (
            self.model_class, self.pk, self.reason)


class UnrecognizedActionException(Exception):
    def __init__(self, action):
        self.action = action

    def __str__(self):
        return "Unrecognized action '%s'" % self.action


class CeleryHaystackSignalHandler(object):

    def __init__(self, identifier):
        self.identifier = identifier

        # First get the object path and pk (e.g. ('notes.note', 23))
        self.object_path, self.pk = self.split_identifier(identifier)

    @staticmethod
    def split_identifier(identifier, **kwargs):
        """
        Break down the identifier representing the instance.
        Converts 'notes.note.23' into ('notes.note', 23).
        """
        bits = identifier.split('.')

        if len(bits) < 2:
            raise ValueError(
                'Unable to parse object identifer \'%s\'' % identifier)

        pk = bits[-1]
        # In case Django ever handles full paths...
        object_path = '.'.join(bits[:-1])
        return object_path, pk

    def get_model_class(self):
        """
        Fetch the model's class in a standarized way.
        """
        bits = self.object_path.split('.')
        app_name = '.'.join(bits[:-1])
        classname = bits[-1]
        model_class = apps.get_model(app_name, classname)

        if model_class is None:
            raise ImproperlyConfigured("Could not load model '%s'." %
                                       self.object_path)
        return model_class

    @staticmethod
    def get_instance(model_class, pk):
        """
        Fetch the instance in a standarized way.
        """
        try:
            instance = model_class._default_manager.get(pk=pk)
        except (model_class.DoesNotExist,
                model_class.MultipleObjectsReturned) as exc:
            raise InstanceNotFoundException(model_class, pk, reason=exc)

        return instance

    @staticmethod
    def get_indexes(model_class):
        """
        Fetch the model's registered ``SearchIndex`` in a standarized way.
        """
        try:
            using_backends = \
                connection_router.for_write(**{'models': [model_class]})
            for using in using_backends:
                index_holder = connections[using].get_unified_index()
                yield index_holder.get_index(model_class), using
        except IndexNotFoundException:
            raise ImproperlyConfigured(
                'Couldn\'t find a SearchIndex for %s.' % model_class)

    @staticmethod
    def get_index_name(index):
        """
            Get index name
        """
        return ".".join([index.__class__.__module__,
                         index.__class__.__name__])

    def handle_delete(self, current_index, using, model_class):
        # If the object is gone, we'll use just the identifier
        # against the index.
        try:
            current_index.remove_object(self.identifier, using=using)
        except Exception as exc:
            raise IndexOperationException(index=current_index, reason=exc)

    def handle_update(self, current_index, using, model_class):
        # and the instance of the model class with the pk

        instance = self.get_instance(model_class, self.pk)

        # Call the appropriate handler of the current index and
        # handle exception if neccessary
        try:
            current_index.update_object(instance, using=using)
        except Exception as exc:
            raise IndexOperationException(index=current_index, reason=exc)

    def handle(self, action):
        """
        Trigger the actual index handler depending on the
        given action ('update' or 'delete').
        """

        # Then get the model class for the object path
        model_class = self.get_model_class()

        for current_index, using in self.get_indexes(model_class):

            if action == 'delete':
                self.handle_delete(current_index, using, model_class)
            elif action == 'update':
                self.handle_update(current_index, using, model_class)
            else:
                raise UnrecognizedActionException(action)


@shared_task
def handle_haystack_signal(action, identifier, **kwargs):
    CeleryHaystackSignalHandler(identifier).handle(action)
