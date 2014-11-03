from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import logout as auth_logout_view
from django.db.models.loading import get_model
from django.http.response import Http404, HttpResponse
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.views.generic.base import TemplateView, View
from djangowind.views import logout as wind_logout_view

import footprints.main.forms as model_forms
from footprints.mixins import JSONResponseMixin, LoggedInMixin, \
    LoggedInStaffMixin


class IndexView(TemplateView):
    template_name = "main/index.html"


class LoginView(JSONResponseMixin, View):

    def post(self, request):
        request.session.set_test_cookie()
        login_form = AuthenticationForm(request, request.POST)
        if login_form.is_valid():
            login(request, login_form.get_user())
            if request.user is not None:
                next_url = request.POST.get('next', '/')
                return self.render_to_json_response({'next': next_url})

        return self.render_to_json_response({'error': True})


class LogoutView(LoggedInMixin, View):

    def get(self, request):
        if hasattr(settings, 'CAS_BASE'):
            return wind_logout_view(request, next_page="/")
        else:
            return auth_logout_view(request, "/")


class RecordWorkspaceView(LoggedInStaffMixin, TemplateView):
    template_name = "record/workspace.html"

    def get_context_data(self, **kwargs):
        return {}


class RecordFormView(LoggedInStaffMixin, JSONResponseMixin, View):

    template_name = 'record/model-form.html'

    def get_model(self, model_name):
        if model_name is None:
            raise Http404

        the_model = get_model('main', model_name)
        if the_model is None:
            raise Http404

        return the_model

    def get_model_instance(self, the_model, pk):
        instance = None
        if pk is not None:
            instance = get_object_or_404(the_model.objects.get(pk=pk))
        return instance

    def get_context_data(self, request):
        the_model = self.get_model(request.GET.get('model', None))
        the_instance = self.get_model_instance(
            the_model, self.request.GET.get('pk', None))

        form_class_name = '%sForm' % the_model._meta.object_name
        form_class = getattr(model_forms, form_class_name)

        return {'action': '/record/model/',
                'model_display_name': the_model._meta.verbose_name,
                'model_name': the_model._meta.model_name,
                'instance': the_instance,
                'the_form': form_class(instance=the_instance)}

    def get(self, request):
        html = render_to_string(self.template_name,
                                self.get_context_data(request))
        return HttpResponse(html)
