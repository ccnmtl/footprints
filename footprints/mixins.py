import json

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.http.response import HttpResponseNotAllowed, HttpResponse
from django.utils.decorators import method_decorator


def ajax_required(func):
    """
    AJAX request required decorator
    use it in your views:

    @ajax_required
    def my_view(request):
        ....

    """
    def wrap(request, *args, **kwargs):
        if not request.is_ajax():
            return HttpResponseNotAllowed("")
        return func(request, *args, **kwargs)

    wrap.__doc__ = func.__doc__
    wrap.__name__ = func.__name__
    return wrap


class JSONResponseMixin(object):

    @method_decorator(ajax_required)
    def dispatch(self, *args, **kwargs):
        return super(JSONResponseMixin, self).dispatch(*args, **kwargs)

    def render_to_json_response(self, context, **response_kwargs):
        """
        Returns a JSON response, transforming 'context' to make the payload.
        """
        return HttpResponse(json.dumps(context),
                            content_type='application/json',
                            **response_kwargs)


class EditableMixin(object):

    def has_edit_permission(self, user):
        return user.is_authenticated()


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
