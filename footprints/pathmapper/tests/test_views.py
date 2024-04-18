from datetime import datetime
from json import loads

from django.test.client import RequestFactory
from django.test.testcases import TestCase
from django.urls.base import reverse

from footprints.main.models import CanonicalPlace
from footprints.main.tests.factories import PlaceFactory
from footprints.main.viewsets import PlaceViewSet
from footprints.pathmapper.forms import PlaceSearchForm
from footprints.pathmapper.views import PathmapperView, PathmapperEventViewSet


class PathmapperViewTest(TestCase):

    def test_parse_layer_no_layers(self):
        view = PathmapperView()
        view.request = RequestFactory().get('/')
        self.assertIsNone(view.parse_layer(0))

    def test_parse_layer_invalid_layer(self):
        q = 'foo:bar,baz:q'
        view = PathmapperView()
        view.request = RequestFactory().get('/', {'l0': q})
        self.assertIsNone(view.parse_layer(0))

    def test_parse_layer_valid_layer(self):
        q = ('id:0,i:,t:Kuzari,w:12,i:,il:,fl:,flf:,a:,ps:'
             ',pe:,pr:,fs:,fe:,fr:,c:,e:,v:true,tc:1')
        view = PathmapperView()
        view.request = RequestFactory().get('/', {'l0': q})
        layer = view.parse_layer(0)
        self.assertEqual(layer['title'], 'Kuzari')
        self.assertEqual(layer['work'], '12')
        self.assertEqual(layer['visible'], 'true')

    def test_get_layers_invalid_count(self):
        view = PathmapperView()

        view.request = RequestFactory().get('/')
        self.assertEqual(view.get_layers(), [])

        view.request = RequestFactory().get('/', {'n': '0'})
        self.assertEqual(view.get_layers(), [])

        view.request = RequestFactory().get('/', {'n': '10'})
        self.assertEqual(view.get_layers(), [])

    def test_get_layers(self):
        q0 = ('id:0,i:,t:Kuzari,w:12,i:,il:,fl:,flf:,a:,ps:'
              ',pe:,pr:,fs:,fe:,fr:,c:,e:,v:true,tc:1')
        q1 = ('id:1,i:,t:Shehitot,w:13,i:,il:,fl:,flf:,a:,ps:'
              ',pe:,pr:,fs:,fe:,fr:,c:,e:,v:false,tc:2')

        view = PathmapperView()
        view.request = RequestFactory().get('/', {'n': 2, 'l0': q0, 'l1': q1})
        layers = view.get_layers()
        self.assertEqual(len(layers), 2)
        self.assertEqual(layers[0]['title'], 'Kuzari')
        self.assertEqual(layers[1]['title'], 'Shehitot')


class BookCopySearchViewTest(TestCase):

    def test_post(self):
        url = reverse('bookcopy-search-view')
        response = self.client.post(url, {},
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        the_json = loads(response.content.decode('utf-8'))
        self.assertEqual(the_json['total'], 0)


class PathmapperTableViewTest(TestCase):

    def test_post(self):
        url = reverse('pathmapper-table-view')
        response = self.client.post(url, {'layers': '{}'},
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        the_json = loads(response.content.decode('utf-8'))
        self.assertEqual(the_json['count'], 0)
        self.assertEqual(the_json['next'], None)
        self.assertEqual(the_json['previous'], None)
        self.assertEqual(the_json['results'], [])


class PathmapperRouteViewTest(TestCase):

    def test_post(self):
        url = reverse('pathmapper-route-view')
        response = self.client.post(url, {'layer': '{}'},
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        the_json = loads(response.content.decode('utf-8'))
        self.assertEqual(the_json['count'], 0)
        self.assertEqual(the_json['next'], None)
        self.assertEqual(the_json['previous'], None)
        self.assertEqual(the_json['results'], [])


class PlaceViewSetTest(TestCase):

    def test_filter_places(self):
        cp1 = PlaceFactory().canonical_place
        cp2 = PlaceFactory(alternate_name='Miasto Kraków').canonical_place

        form = PlaceSearchForm()
        form.cleaned_data = {'q': ''}
        qs = CanonicalPlace.objects.all()

        vs = PlaceViewSet()
        results = vs.filter_places(form, qs)
        self.assertEqual(results.count(), 2)
        self.assertEqual(results.get(id=cp1.id), cp1)
        self.assertEqual(results.get(id=cp2.id), cp2)

        form.cleaned_data = {'q': 'foo'}
        results = vs.filter_places(form, qs)
        self.assertEqual(results.count(), 0)

        form.cleaned_data = {'q': 'Miasto'}
        results = vs.filter_places(form, qs)
        self.assertEqual(results.count(), 1)
        self.assertEqual(results.get(id=cp2.id), cp2)


class PathmapperEventViewSetTest(TestCase):

    def test_get_book_copies_invalid(self):
        layer = {
            'work': None,
            'imprint': None,
            'imprintLocation': None,
            'footprintLocation': None,
            'footprintStart': '2000',
            'footprintEnd': '1970',
            'footprintRange': True,
            'pubRange': 'false',
            'pubStart': None,
            'pubEnd': None
        }

        viewset = PathmapperEventViewSet()
        self.assertIsNone(viewset.get_book_copies(layer))

    def test_get_book_copies_valid(self):
        layer = {
            'work': None,
            'imprint': None,
            'imprintLocation': None,
            'footprintLocation': None,
            'footprintStart': '',
            'footprintEnd': '',
            'footprintRange': False,
            'pubRange': 'false',
            'pubStart': None,
            'pubEnd': None
        }

        viewset = PathmapperEventViewSet()
        sqs = viewset.get_book_copies(layer)
        self.assertEqual(sqs.count(), 0)

    def test_map_events(self):
        events = {}
        current_year = int(datetime.now().year)
        counts = [('1950', 1), ('1950', 2), ('1970', 0),
                  ('1', 15), ('2100', 17)]
        viewset = PathmapperEventViewSet()
        viewset.map_events(counts, current_year, events)

        self.assertEqual(events[1950], {'year': '1950-01-01', 'count': 3})
        self.assertFalse('1970' in events)
        self.assertFalse('1' in events)
        self.assertFalse('2100' in events)
