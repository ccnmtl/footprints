# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from datetime import datetime, date
from json import loads

from django.http.response import JsonResponse
from django.views.generic.base import TemplateView, View
from django.views.generic.list import ListView

from footprints.main.models import Footprint
from footprints.main.serializers import FootprintSerializer
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


class PathMapperRouteView(JSONResponseMixin, ListView):

    model = Footprint
    http_method_names = ['get']
    paginate_by = 15

    def get_queryset(self):
        return Footprint.objects.none()


class PathmapperTableView(JSONResponseMixin, ListView):

    model = Footprint
    http_method_names = ['post']
    paginate_by = 15

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

    def render_to_response(self, context, **response_kwargs):
        serializer = FootprintSerializer(
            context['page_obj'].object_list, many=True,
            context={'request': self.request})

        page = {
            'number': context['page_obj'].number,
            'hasNext': context['page_obj'].has_next(),
            'hasPrev': context['page_obj'].has_previous()
        }
        if page['hasNext']:
            page['nextPageNumber'] = context['page_obj'].next_page_number()
        if page['hasPrev']:
            page['prevPageNumber'] = context['page_obj'].previous_page_number()

        ctx = {
            'page': page,
            'num_pages': context['paginator'].num_pages,
            'footprints': serializer.data
        }
        return JsonResponse(ctx, status=200, safe=False)

    def post(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)
