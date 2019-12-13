# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.views.generic.base import TemplateView, View

from footprints.mixins import JSONResponseMixin
from footprints.pathmapper.forms import BookCopySearchForm


class MapView(TemplateView):
    template_name = 'pathmapper/map.html'


class BookCopySearchView(JSONResponseMixin, View):

    def post(self, request):
        form = BookCopySearchForm(request.POST)
        if form.is_valid():
            sqs = form.search()

            ctx = {'total': sqs.count()}
            return self.render_to_json_response(ctx)

        return self.render_to_json_response({'errors': form.errors})
