# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from datetime import datetime, date

from django.views.generic.base import TemplateView, View

from footprints.mixins import JSONResponseMixin
from footprints.pathmapper.forms import BookCopySearchForm


class MapView(TemplateView):
    template_name = 'pathmapper/map.html'


class BookCopySearchView(JSONResponseMixin, View):

    def min_year(self, sqs, key):
        stats = sqs.stats(key).stats_results()
        if not stats or not stats[key]['min']:
            return date.min.year

        return datetime.strptime(stats[key]['min'], '%Y-%m-%dT%H:%M:%SZ').year

    def max_year(self, sqs, key):
        stats = sqs.stats(key).stats_results()
        if not stats or not stats[key]['min']:
            return date.max.year
        return datetime.strptime(stats[key]['max'], '%Y-%m-%dT%H:%M:%SZ').year

    def post(self, request):
        form = BookCopySearchForm(request.POST)
        if form.is_valid():
            sqs = form.search()
            ctx = {
                'total': sqs.count(),
                'footprintMin': self.min_year(sqs, 'footprint_start_date'),
                'footprintMax': self.max_year(sqs, 'footprint_end_date'),
                'pubMin': self.min_year(sqs, 'pub_start_date'),
                'pubMax': self.max_year(sqs, 'pub_end_date')
            }
            return self.render_to_json_response(ctx)

        return self.render_to_json_response({'errors': form.errors})
