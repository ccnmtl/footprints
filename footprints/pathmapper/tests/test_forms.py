from datetime import date

from django.db.models.query_utils import Q
from django.test.testcases import TestCase
from django.utils.encoding import smart_str

from footprints.main.tests.factories import PlaceFactory
from footprints.pathmapper.forms import (
    ActorSearchForm, BookCopySearchForm, ModelSearchFormEx, ImprintSearchForm,
    WrittenWorkSearchForm)


class ModelSearchFormExTest(TestCase):

    def test_transform_data(self):
        form = ModelSearchFormEx()
        form.cleaned_data = {}
        form.data = {
            'work': None,
            'imprint': None,
            'imprintLocation': None,
        }
        form.transform_data()
        self.assertTrue('work' in form.cleaned_data)
        self.assertTrue('imprint' in form.cleaned_data)
        self.assertTrue('imprint_location' in form.cleaned_data)

    def test_transform_errors(self):
        form = ModelSearchFormEx()
        form._errors = {
            'work': 'an error',
            'imprint_location': 'another error'
        }
        form.transform_errors()
        self.assertEqual(form._errors['work'], 'an error')
        self.assertEqual(form._errors['imprintLocation'], 'another error')

    def test_handle_single_year(self):
        field_name = 'pub_start'
        start_year = 1850
        form = ModelSearchFormEx()
        kwargs = form.handle_single_year(field_name, start_year)
        self.assertEqual(kwargs['pub_start__gte'], date(1850, 1, 1))
        self.assertEqual(kwargs['pub_start__lte'], date(1850, 12, 31))

    def test_handle_range(self):
        field_name1 = 'pub_start'
        field_name2 = 'pub_end'
        start_year = 1850
        end_year = 1886

        form = ModelSearchFormEx()
        kwargs = form.handle_range(
            field_name1, field_name2, start_year, end_year)
        self.assertEqual(kwargs['pub_start__gte'], date(1850, 1, 1))
        self.assertEqual(kwargs['pub_end__lte'], date(1886, 12, 31))

    def test_handle_footprint_year(self):
        form = ModelSearchFormEx()
        form.cleaned_data = {
            'footprint_start': 1850,
            'footprint_end': 1886
        }

        kwargs = form.handle_footprint_year()
        self.assertEqual(kwargs['footprint_start_date__gte'], date(1850, 1, 1))
        self.assertEqual(
            kwargs['footprint_start_date__lte'], date(1850, 12, 31))

        form.cleaned_data['footprint_range'] = True
        kwargs = form.handle_footprint_year()
        self.assertEqual(kwargs['footprint_start_date__gte'], date(1850, 1, 1))
        self.assertEqual(
            kwargs['footprint_end_date__lte'], date(1886, 12, 31))

    def test_format_footprint_year_query(self):
        form = ModelSearchFormEx()
        fld = 'book_copy_id'
        q = form.format_footprint_year_query(fld, 1556, None, False)
        self.assertEqual(
            q,
            '{!join from=book_copy_id to=django_id}'
            'django_ct:"main.footprint" AND footprint_start_date:'
            '[1556-01-01T00:00:00Z TO 1556-12-31T00:00:00Z]'
            ' AND footprint_end_date:[1556-01-01T00:00:00Z TO '
            '1556-12-31T00:00:00Z]')

        q = form.format_footprint_year_query(fld, 1556, 1689, True)
        self.assertEqual(
            q,
            '{!join from=book_copy_id to=django_id}'
            'django_ct:"main.footprint" AND footprint_start_date:'
            '[1556-01-01T00:00:00Z TO 1689-12-31T00:00:00Z]'
            ' AND footprint_end_date:[1556-01-01T00:00:00Z TO '
            '1689-12-31T00:00:00Z]')

        q = form.format_footprint_year_query(fld, 1556, None, True)
        self.assertEqual(
            q,
            '{!join from=book_copy_id to=django_id}'
            'django_ct:"main.footprint" AND footprint_start_date:'
            '[1556-01-01T00:00:00Z TO *]'
            ' AND footprint_end_date:[1556-01-01T00:00:00Z TO *]')

        q = form.format_footprint_year_query(fld, None, 1556, True)
        self.assertEqual(
            q,
            '{!join from=book_copy_id to=django_id}'
            'django_ct:"main.footprint" AND footprint_start_date:'
            '[* TO 1556-12-31T00:00:00Z]'
            ' AND footprint_end_date:[* TO 1556-12-31T00:00:00Z]')

    def test_handle_pub_year(self):
        form = ModelSearchFormEx()
        form.cleaned_data = {
            'pub_start': 1850,
            'pub_end': 1886
        }

        kwargs = form.handle_pub_year()
        self.assertEqual(kwargs['pub_start_date__gte'], date(1850, 1, 1))
        self.assertEqual(
            kwargs['pub_start_date__lte'], date(1850, 12, 31))

        form.cleaned_data['pub_range'] = True
        kwargs = form.handle_pub_year()
        self.assertEqual(kwargs['pub_start_date__gte'], date(1850, 1, 1))
        self.assertEqual(
            kwargs['pub_end_date__lte'], date(1886, 12, 31))

    def test_handle_imprint_location(self):
        form = ModelSearchFormEx()
        form.cleaned_data = {
            'imprint_location': 1
        }

        kwargs = form.handle_imprint_location()
        self.assertEqual(kwargs['imprint_location'], 1)

    def test_handle_imprint_location_title(self):
        place = PlaceFactory()
        form = ModelSearchFormEx()
        form.cleaned_data = {
            'imprint_location': place.id
        }

        args = form.handle_imprint_location_title()
        self.assertEqual(
            args[0], Q(imprint_location_title_exact__in=[smart_str(place)]))

    def test_handle_footprint_location(self):
        form = ModelSearchFormEx()
        form.cleaned_data = {
            'footprint_location': 1
        }

        kwargs = form.handle_footprint_location()
        self.assertEqual(kwargs['footprint_location'], 1)

    def test_handle_footprint_location_title(self):
        place = PlaceFactory()
        form = ModelSearchFormEx()
        form.cleaned_data = {
            'footprint_location': place.id
        }

        args = form.handle_footprint_location_title()
        self.assertEqual(
            args[0], Q(footprint_location_title_exact__in=[smart_str(place)]))

    def test_handle_actor(self):
        form = ModelSearchFormEx()
        form.cleaned_data = {
            'actor': 1
        }
        args = form.handle_actor()
        self.assertEqual(args[0], Q(actor_exact__in=[1]))

    def test_empty_search(self):
        form = ModelSearchFormEx()
        form.cleaned_data = {}
        form.data = {
            'work': None,
            'imprint': None,
            'imprintLocation': None,
            'footprintLocation': None,
            'footprintStart': None,
            'footprintEnd': None,
            'footprintRange': False,
            'pubRange': 'false',
            'pubStart': None,
            'pubEnd': None
        }
        sqs = form.search()
        self.assertEqual(sqs.count(), 0)

    def test_form_clean_errors_string_date(self):
        form = ModelSearchFormEx()
        form._errors = {}
        form.cleaned_data = {}
        form.data = {
            'q': '',
            'footprintStart': '0',
            'footprintEnd': 2020,
            'footprintRange': 'false',
            'pubStart': None,
            'pubEnd': None,
            'pubRange': False
        }

        form.clean()
        self.assertTrue(form._errors['footprintStart'],
                        ['Year must be greater than 1000'])

    def test_form_clean_errors_future_date(self):
        form = ModelSearchFormEx()
        form._errors = {}
        form.cleaned_data = {}
        form.data = {
            'q': '',
            'footprintStart': 2080,
            'footprintEnd': 2080,
            'footprintRange': 'false',
            'pubStart': None,
            'pubEnd': None,
            'pubRange': False
        }

        form.clean()
        self.assertTrue(form._errors['footprintStart'], ['No future year'])
        self.assertTrue(form._errors['footprintEnd'], ['No future year'])

    def test_form_clean_errors_past_date(self):
        form = ModelSearchFormEx()
        form._errors = {}
        form.cleaned_data = {}
        form.data = {
            'q': '',
            'footprintStart': 999,
            'footprintEnd': 999,
            'pubStart': 999,
            'pubEnd': 999
        }

        form.clean()
        self.assertTrue(form._errors['footprintStart'],
                        ['Year must be greater than 1000'])
        self.assertTrue(form._errors['footprintEnd'],
                        ['Year must be greater than 1000'])
        self.assertTrue(form._errors['pubStart'],
                        ['Year must be greater than 1000'])
        self.assertTrue(form._errors['pubEnd'],
                        ['Year must be greater than 1000'])

    def test_form_clean_range(self):
        form = ModelSearchFormEx()
        form._errors = {}
        form.cleaned_data = {}
        form.data = {
            'q': '',
            'footprintRange': True,
            'footprintStart': 2016,
            'footprintEnd': 1740,
            'pubStart': None,
            'pubEnd': None
        }

        form.clean()
        self.assertTrue(form._errors['footprintStart'],
                        ['Start year must be less than end year'])

    def test_form_clean_single_year_valid(self):
        form = ModelSearchFormEx()
        form._errors = {}
        form.cleaned_data = {}
        form.data = {
            'q': '',
            'footprintRange': False,
            'footprintStart': 1740,
            'footprintEnd': None,
            'pubStart': 1740,
            'pubEnd': None
        }

        form.clean()
        self.assertEqual(len(form._errors.keys()), 0)

    def test_form_clean_range_valid(self):
        form = ModelSearchFormEx()
        form._errors = {}
        form.cleaned_data = {}
        form.data = {
            'q': '',
            'footprintRange': 'true',
            'footprintStart': None,
            'footprintEnd': 1740,
            'pubStart': None,
            'pubEnd': 1740
        }

        form.clean()
        self.assertEqual(len(form._errors.keys()), 0)


SAMPLE_CLEANED_DATA = {
    'q': 'Foo',
    'work': 12,
    'imprint': 13,
    'footprint_range': True,
    'footprint_start': 1910,
    'footprint_end': 1940,
    'pub_start': 1800,
    'pub_end': 1820,
    'pub_range': False,
    'imprint_location': 14,
    'footprint_location': 15,
    'actor': 16
}


class BookCopySearchFormTest(TestCase):

    def test_arguments(self):
        form = BookCopySearchForm()
        form.cleaned_data = SAMPLE_CLEANED_DATA

        args, kwargs = form.arguments()
        self.assertEqual(kwargs['django_ct'], 'main.bookcopy')
        self.assertEqual(kwargs['work_id'], 12)
        self.assertEqual(kwargs['imprint_id'], 13)
        self.assertEqual(kwargs['imprint_location'], 14)
        self.assertEqual(kwargs['footprint_location'], 15)
        self.assertEqual(args[0], Q(actor_exact__in=[16]))
        self.assertEqual(kwargs['pub_start_date__gte'], date(1800, 1, 1))
        self.assertEqual(
            kwargs['pub_start_date__lte'], date(1800, 12, 31))


class ImprintSearchFormTest(TestCase):

    def test_arguments(self):
        form = ImprintSearchForm()
        form.cleaned_data = SAMPLE_CLEANED_DATA

        args, kwargs = form.arguments()
        self.assertEqual(kwargs['django_ct'], 'main.imprint')
        self.assertEqual(kwargs['content'], 'Foo')
        self.assertEqual(kwargs['work_id'], 12)
        self.assertFalse('imprint_id' in kwargs)
        self.assertEqual(kwargs['imprint_location'], 14)
        self.assertEqual(kwargs['footprint_location'], 15)
        self.assertEqual(args[0], Q(actor_exact__in=[16]))
        self.assertEqual(kwargs['pub_start_date__gte'], date(1800, 1, 1))
        self.assertEqual(
            kwargs['pub_start_date__lte'], date(1800, 12, 31))


class WrittenWorkSearchFormTest(TestCase):

    def test_arguments(self):
        form = WrittenWorkSearchForm()
        form.cleaned_data = SAMPLE_CLEANED_DATA

        args, kwargs = form.arguments()
        self.assertEqual(kwargs['django_ct'], 'main.writtenwork')
        self.assertEqual(kwargs['content'], 'Foo')
        self.assertFalse('work_id' in kwargs)
        self.assertFalse('imprint_id' in kwargs)
        self.assertEqual(kwargs['imprint_location'], 14)
        self.assertEqual(kwargs['footprint_location'], 15)
        self.assertEqual(args[0], Q(actor_exact__in=[16]))
        self.assertEqual(kwargs['pub_start_date__gte'], date(1800, 1, 1))
        self.assertEqual(
            kwargs['pub_start_date__lte'], date(1800, 12, 31))


class ActorSearchFormTest(TestCase):

    def test_arguments(self):
        form = ActorSearchForm()
        form.cleaned_data = SAMPLE_CLEANED_DATA

        args, kwargs = form.arguments('main.writtenwork')
        self.assertEqual(kwargs['django_ct'], 'main.writtenwork')
        self.assertFalse('content' in kwargs)
        self.assertEqual(args[0], Q(actor_title_exact__contains='Foo'))
        self.assertEqual(kwargs['work_id'], 12)
        self.assertEqual(kwargs['imprint_id'], 13)
        self.assertEqual(kwargs['imprint_location'], 14)
        self.assertEqual(kwargs['footprint_location'], 15)
        self.assertEqual(kwargs['pub_start_date__gte'], date(1800, 1, 1))
        self.assertEqual(
            kwargs['pub_start_date__lte'], date(1800, 12, 31))
