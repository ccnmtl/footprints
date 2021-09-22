# from django.conf import settings
from django.db.models import signals
from django.db import connection, transaction
from footprints.main.tasks import handle_haystack_signal
from haystack.exceptions import NotHandled
from haystack.indexes import SearchIndex
from haystack.signals import BaseSignalProcessor
from haystack.utils import get_identifier


class FootprintsSignalProcessor(BaseSignalProcessor):

    def setup(self):
        signals.post_save.connect(self.enqueue_save)
        signals.post_delete.connect(self.enqueue_delete)

    def teardown(self):
        signals.post_save.disconnect(self.enqueue_save)
        signals.post_delete.disconnect(self.enqueue_delete)

    def enqueue_save(self, sender, instance, **kwargs):
        return self.enqueue('update', instance, sender, **kwargs)

    def enqueue_delete(self, sender, instance, **kwargs):
        return self.enqueue('delete', instance, sender, **kwargs)

    def enqueue(self, action, instance, sender, **kwargs):
        """
        Given an individual model instance, determine if a backend
        handles the model, check if the index is Celery-enabled and
        enqueue task.
        """
        using_backends = self.connection_router.for_write(instance=instance)

        for using in using_backends:
            try:
                c = self.connections[using]
                index = c.get_unified_index().get_index(sender)
            except NotHandled:
                continue  # Check next backend

            if isinstance(index, SearchIndex):
                if action == 'update' and not index.should_update(instance):
                    continue
                if action in ['update', 'delete']:
                    self.enqueue_task(action, get_identifier(instance))

    def enqueue_task(self, action, identifier):
        func = lambda: handle_haystack_signal.apply_async(  # noqa: E731
            (action, identifier))

        if hasattr(transaction, 'on_commit'):
            # Django 1.9 on_commit hook
            transaction.on_commit(func)
        elif hasattr(connection, 'on_commit'):
            # Django-transaction-hooks
            connection.on_commit(func)
        else:
            func()
