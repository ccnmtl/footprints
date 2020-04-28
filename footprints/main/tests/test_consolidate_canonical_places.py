from _io import StringIO

from django.core.management import call_command
from django.test import TestCase

from footprints.main.models import CanonicalPlace
from footprints.main.tests.factories import CanonicalPlaceFactory, PlaceFactory


class ConsolidateCanonicalPlaces(TestCase):

    def test_command(self):
        cpMoscow1 = CanonicalPlaceFactory(
            canonical_name='Moscow', position='55.755826,37.6173')
        pMoscow1 = PlaceFactory(alternate_name='Moscow1',
                                canonical_place=cpMoscow1)
        cpMoscow2 = CanonicalPlaceFactory(
            canonical_name='Moscow', position='55.755826,37.6174')
        pMoscow2 = PlaceFactory(alternate_name='Moscow2',
                                canonical_place=cpMoscow2)
        cpMoscow3 = CanonicalPlaceFactory(
            canonical_name='Moscow', position='55.755826,37.6175')
        pMoscow3 = PlaceFactory(alternate_name='Moscow2',
                                canonical_place=cpMoscow3)
        cpMoscow4 = CanonicalPlaceFactory(
            canonical_name='Moscow', position='55.755826,38.6175')
        pMoscow4 = PlaceFactory(alternate_name='Moscow4',
                                canonical_place=cpMoscow4)
        cpMoskov1 = CanonicalPlaceFactory(
            canonical_name='Moskov', position='55.755826,37.6173')
        pMoskov1 = PlaceFactory(alternate_name='Moskov',
                                canonical_place=cpMoskov1)

        out = StringIO()
        call_command('consolidate_canonical_places', stdout=out)
        self.assertIn('Removing 2 duplicates', out.getvalue())
        self.assertEqual(cpMoscow1.place_set.count(), 3)

        with self.assertRaises(CanonicalPlace.DoesNotExist):
            CanonicalPlace.objects.get(id=cpMoscow2.id)

        with self.assertRaises(CanonicalPlace.DoesNotExist):
            CanonicalPlace.objects.get(id=cpMoscow3.id)

        pMoscow1.refresh_from_db()
        self.assertEqual(pMoscow1.canonical_place, cpMoscow1)
        pMoscow2.refresh_from_db()
        self.assertEqual(pMoscow2.canonical_place, cpMoscow1)
        pMoscow3.refresh_from_db()
        self.assertEqual(pMoscow3.canonical_place, cpMoscow1)
        pMoscow4.refresh_from_db()
        self.assertEqual(pMoscow4.canonical_place, cpMoscow4)
        pMoskov1.refresh_from_db()
        self.assertEqual(pMoskov1.canonical_place, cpMoskov1)
