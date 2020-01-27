# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from datetime import datetime, date
from json import loads

from django.views.generic.base import TemplateView, View
from rest_framework.generics import ListAPIView

from footprints.main.models import Footprint, BookCopy
from footprints.main.serializers import (
    PathmapperRouteSerializer, FootprintSerializer)
from footprints.mixins import JSONResponseMixin
from footprints.pathmapper.forms import BookCopySearchForm


class PathmapperView(TemplateView):
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


class PathmapperRouteView(ListAPIView):

    model = BookCopy
    serializer_class = PathmapperRouteSerializer
    authentication_classes = []
    permission_classes = []
    page_size = 15

    def get_book_copies(self, layer):
        form = BookCopySearchForm(layer)
        if form.is_valid():
            sqs = form.search()
            return sqs.values_list('object_id', flat=True)

    def get_queryset(self):
        layer = loads(self.request.POST.get('layer'))
        ids = self.get_book_copies(layer)
        return BookCopy.objects.filter(id__in=ids).select_related(
            'imprint__place')

    def post(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)


class PathmapperTableView(ListAPIView):
    model = Footprint
    serializer_class = FootprintSerializer
    authentication_classes = []
    permission_classes = []
    page_size = 15

    def get_book_copies(self, layer):
        form = BookCopySearchForm(layer)
        if form.is_valid():
            sqs = form.search()
            return sqs.values_list('object_id', flat=True)

    def get_queryset(self):
        ids = []
        layers = loads(self.request.POST.get('layers'))
        for layer in layers:
            ids += self.get_book_copies(layer)
        return Footprint.objects.filter(book_copy__id__in=ids)

    def post(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)
