from django.contrib.auth.decorators import login_required, user_passes_test
from django.http.response import HttpResponseNotAllowed, HttpResponse
from django.utils.decorators import method_decorator
import json


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


def is_staff(func):

    def wrap(request, *args, **kwargs):
        user = request.user
        if user.is_anonymous() or not user.is_staff:
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


class LoggedInMixin(object):
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(LoggedInMixin, self).dispatch(*args, **kwargs)


class LoggedInStaffMixin(object):
    @method_decorator(is_staff)
    def dispatch(self, *args, **kwargs):
        return super(LoggedInStaffMixin, self).dispatch(*args, **kwargs)


class LoggedInMixinSuperuserMixin(object):
    @method_decorator(user_passes_test(lambda u: u.is_superuser))
    def dispatch(self, *args, **kwargs):
        return super(LoggedInMixinSuperuserMixin,
                     self).dispatch(*args, **kwargs)
