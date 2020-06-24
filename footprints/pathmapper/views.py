# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from datetime import datetime
import html
from json import loads
import re

from django.views.generic.base import TemplateView, View
from rest_framework import viewsets
from rest_framework.generics import ListAPIView
from rest_framework.response import Response

from footprints.main.models import Footprint, BookCopy
from footprints.main.serializers import (
    PathmapperRouteSerializer, PathmapperTableRowSerializer,
    PathmapperEventSerializer)
from footprints.mixins import JSONResponseMixin
from footprints.pathmapper.forms import BookCopySearchForm, \
    BookCopyFootprintsForm


class PathmapperView(TemplateView):
    template_name = 'pathmapper/map.html'

    valid_keys = {
        't': 'title',
        'w': 'work',
        'i': 'imprint',
        'il': 'imprintLocation',
        'fl': 'footprintLocation',
        'flf': 'footprintLocationFinal',
        'a': 'actor',
        'ps': 'pubStart',
        'pe': 'pubEnd',
        'pr': 'pubRange',
        'fs': 'footprintStart',
        'fe': 'footprintEnd',
        'fr': 'footprintRange',
        'c': 'censored',
        'e': 'expurgated',
        'v': 'visible'
    }

    def expand_key(self, key):
        if key in self.valid_keys:
            return self.valid_keys[key]
        return None

    def parse_layer(self, idx):
        data = self.request.GET.get('l{}'.format(idx), None)
        if not data:
            return None

        layer = {}
        args = re.split(':|,', data)  # string of parameters like so: w:1,i:2
        for idx in range(0, len(args), 2):
            key = self.expand_key(args[idx])
            if key:
                layer[key] = html.escape(args[idx + 1])

        # validate the layer has the expected parameters
        if len(layer.keys()) != len(self.valid_keys.keys()):
            return None

        return layer

    def get_layers(self):
        # The "Share" url crunches an array of layers into GET query params
        # if layer args exist, parse them into a dict and place in view context
        layers = []
        n = int(self.request.GET.get('n', '0'))
        if n < 1 or n > 9:
            return layers

        for idx in range(0, n):
            layer = self.parse_layer(idx)
            if layer:
                layers.append(layer)
        return layers

    def get_context_data(self, **kwargs):
        ctx = TemplateView.get_context_data(self, **kwargs)
        ctx['layers'] = self.get_layers()
        return ctx


class BookCopySearchView(JSONResponseMixin, View):

    def min_year(self, sqs, key):
        stats = sqs.stats(key).stats_results()
        if not stats or not stats[key] or not stats[key]['min']:
            return 1000

        return datetime.strptime(stats[key]['min'], '%Y-%m-%dT%H:%M:%SZ').year

    def max_year(self, sqs, key):
        this_year = datetime.now().year
        stats = sqs.stats(key).stats_results()
        if not stats or not stats[key] or not stats[key]['max']:
            return this_year
        return min(
            this_year,
            datetime.strptime(stats[key]['max'], '%Y-%m-%dT%H:%M:%SZ').year)

    def post(self, request):
        form = BookCopySearchForm(request.POST)
        if form.is_valid():
            sqs = form.search()
            ctx = {
                'totalMax': BookCopy.objects.count(),
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
    serializer_class = PathmapperTableRowSerializer
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

        form = BookCopyFootprintsForm()
        sqs = form.search(ids)
        return sqs.order_by('wtitle', 'pub_start_date', 'book_copy_id')

    def post(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)


class PathmapperEventViewSet(viewsets.ViewSet):
    serializer_class = PathmapperEventSerializer
    authentication_classes = []
    permission_classes = []
    page_size = 15

    def get_book_copies(self, layer):
        form = BookCopySearchForm(layer)
        if form.is_valid():
            sqs = form.search()
            return sqs

    def map_events(self, counts):
        for key, value in counts:
            key = int(key)
            if value > 0 and key > 1000 and key < self.current_year:
                year = '{}-01-01'.format(key)
                self.events.setdefault(key, {'year': year, 'count': 0})
                self.events[key]['count'] += value

    def get_events(self):
        ids = []
        layers = loads(self.request.POST.get('layers'))
        for layer in layers:
            sqs = self.get_book_copies(layer)
            counts = sqs.facet('pub_year').facet_counts()
            self.map_events(counts['fields']['pub_year'])
            ids += sqs.values_list('object_id', flat=True)

        form = BookCopyFootprintsForm()
        sqs = form.search(ids)
        counts = sqs.facet('footprint_year').facet_counts()
        self.map_events(counts['fields']['footprint_year'])
        return self.events.values()

    def list(self, request):
        self.events = {}
        self.current_year = int(datetime.now().year)
        serializer = PathmapperEventSerializer(
            instance=self.get_events(), many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)
