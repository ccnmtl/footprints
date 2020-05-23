from _io import StringIO

from django.core.management import call_command
from django.test import TestCase

from footprints.main.models import Place
from footprints.main.tests.factories import (
    CanonicalPlaceFactory, PlaceFactory, ImprintFactory, FootprintFactory)


class ConsolidateCanonicalPlaces(TestCase):

    def test_command(self):
        cpMoscowRussia = CanonicalPlaceFactory(
            canonical_name='Moscow, Russia',
            position='55.755826,37.6173')

        # These places should collapse into pMoscow1
        pMoscow1 = PlaceFactory(alternate_name='Moscow',
                                canonical_place=cpMoscowRussia)
        imprint1 = ImprintFactory(place=pMoscow1)
        footprint1 = FootprintFactory(place=pMoscow1)

        pMoscow2 = PlaceFactory(alternate_name='Moscow',
                                canonical_place=cpMoscowRussia)
        imprint2 = ImprintFactory(place=pMoscow2)
        imprint3 = ImprintFactory(place=pMoscow2)
        footprint2 = FootprintFactory(place=pMoscow2)

        pMoscow3 = PlaceFactory(alternate_name='Moscow',
                                canonical_place=cpMoscowRussia)
        imprint4 = ImprintFactory(place=pMoscow3)
        imprint5 = ImprintFactory(place=pMoscow3)
        footprint3 = FootprintFactory(place=pMoscow3)
        footprint4 = FootprintFactory(place=pMoscow3)

        # This one should stay the same
        pMoscow4 = PlaceFactory(alternate_name='Moscova',
                                canonical_place=cpMoscowRussia)

        # These should remain untouched
        cpMoscowIdaho = CanonicalPlaceFactory(
            canonical_name='Moscow, Idaho, United States',
            position='46.73239, -117.00017')
        pMoscow5 = PlaceFactory(
            alternate_name='Moscow', canonical_place=cpMoscowIdaho)

        self.assertEquals(cpMoscowRussia.place_set.count(), 4)

        out = StringIO()
        call_command('consolidate_places', stdout=out)
        self.assertIn('Removing 2 duplicates', out.getvalue())

        self.assertEqual(cpMoscowRussia.place_set.count(), 2)
        self.assertTrue(pMoscow1 in cpMoscowRussia.place_set.all())
        self.assertTrue(pMoscow4 in cpMoscowRussia.place_set.all())

        self.assertEqual(cpMoscowIdaho.place_set.count(), 1)
        self.assertTrue(pMoscow5 in cpMoscowIdaho.place_set.all())

        with self.assertRaises(Place.DoesNotExist):
            Place.objects.get(id=pMoscow2.id)
        with self.assertRaises(Place.DoesNotExist):
            Place.objects.get(id=pMoscow3.id)

        qs = pMoscow1.imprint_set.all()
        self.assertTrue(imprint1 in qs)
        self.assertTrue(imprint2 in qs)
        self.assertTrue(imprint3 in qs)
        self.assertTrue(imprint4 in qs)
        self.assertTrue(imprint5 in qs)

        qs = pMoscow1.footprint_set.all()
        self.assertTrue(footprint1 in qs)
        self.assertTrue(footprint2 in qs)
        self.assertTrue(footprint3 in qs)
        self.assertTrue(footprint4 in qs)
