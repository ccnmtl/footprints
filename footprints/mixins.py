import json

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.http.response import HttpResponseNotAllowed, HttpResponse
from django.utils.decorators import method_decorator


def is_ajax(request):
    return request.headers.get('x-requested-with') == 'XMLHttpRequest'


class JSONResponseMixin(object):

    def dispatch(self, *args, **kwargs):
        if not is_ajax(self.request):
            return HttpResponseNotAllowed("")

        return super(JSONResponseMixin, self).dispatch(*args, **kwargs)

    def render_to_json_response(self, context, **response_kwargs):
        """
        Returns a JSON response, transforming 'context' to make the payload.
        """
        return HttpResponse(json.dumps(context),
                            content_type='application/json',
                            **response_kwargs)


class LoggedInMixin(object):
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(LoggedInMixin, self).dispatch(*args, **kwargs)


class BatchAccessMixin(PermissionRequiredMixin):
    raise_exception = True
    permission_required = (
        'batch.add_batchjob', 'batch.change_batchjob', 'batch.delete_batchjob',
        'batch.add_batchrow', 'batch.change_batchrow', 'batch.delete_batchrow')


class ModerationAccessMixin(PermissionRequiredMixin):
    raise_exception = True
    permission_required = ('main.can_moderate',)


class DeleteAccessMixin(PermissionRequiredMixin):
    raise_exception = True
    permission_required = (
        'main.delete_role', 'main.delete_language',
        'main.delete_digitalobject',
        'main.delete_standardizedidentification', 'main.delete_person',
        'main.delete_place', 'main.delete_collection',
        'main.delete_writtenwork',
        'main.delete_imprint', 'main.delete_bookcopy', 'main.delete_footprint',
        'main.delete_actor', 'main.delete_standardizedidentificationtype',
        'main.delete_extendeddate'
    )


class AddChangeAccessMixin(PermissionRequiredMixin):
    raise_exception = True
    permission_required = (
        'main.add_role', 'main.change_role',
        'main.add_language', 'main.change_language',
        'main.add_digitalformat', 'main.change_digitalformat',
        'main.add_digitalobject', 'main.change_digitalobject',
        'main.add_standardizedidentification',
        'main.change_standardizedidentification',
        'main.add_person', 'main.change_person',
        'main.add_place', 'main.change_place',
        'main.add_collection', 'main.change_collection',
        'main.add_writtenwork', 'main.change_writtenwork',
        'main.add_imprint', 'main.change_imprint',
        'main.add_bookcopy', 'main.change_bookcopy',
        'main.add_footprint', 'main.change_footprint',
        'main.add_actor', 'main.change_actor',
        'main.add_standardizedidentificationtype',
        'main.change_standardizedidentificationtype',
        'main.add_extendeddate', 'main.change_extendeddate'
    )
