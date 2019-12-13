from django.test.testcases import TestCase
from django.utils.encoding import smart_text

from footprints.main.search_indexes import FootprintIndex, BookCopyIndex, \
    WrittenWorkIndex, ImprintIndex
from footprints.main.tests.factories import FootprintFactory


class TestFootprintIndex(TestCase):

    def test_prepare_actor(self):
        fp = FootprintFactory()

        actors = FootprintIndex().prepare_actor(fp)
        self.assertTrue(smart_text(fp.actor.first()) in actors)
        self.assertTrue(smart_text(fp.book_copy.imprint.work.actor.first())
                        in actors)


class TestBookCopyIndex(TestCase):

    def test_prepare_footprint_locations(self):
        fp = FootprintFactory()
        places = BookCopyIndex().prepare_footprint_locations(fp.book_copy)
        self.assertTrue(fp.place.id in places)

    def test_prepare_actor(self):
        fp = FootprintFactory()

        actors = BookCopyIndex().prepare_actor(fp.book_copy)
        self.assertTrue(fp.actor.first().id in actors)
        self.assertTrue(fp.book_copy.imprint.work.actor.first().id in actors)


class TestImprintIndex(TestCase):

    def test_prepare_footprint_locations(self):
        fp = FootprintFactory()
        places = ImprintIndex().prepare_footprint_locations(
            fp.book_copy.imprint)
        self.assertTrue(fp.place.id in places)

    def test_prepare_actor(self):
        fp = FootprintFactory()

        actors = ImprintIndex().prepare_actor(fp.book_copy.imprint)
        self.assertTrue(fp.book_copy.imprint.actor.first().id in actors)


class TestWrittenWorkIndex(TestCase):

    def test_prepare_footprint_locations(self):
        fp = FootprintFactory()
        places = WrittenWorkIndex().prepare_footprint_locations(
            fp.book_copy.imprint.work)
        self.assertTrue(fp.place.id in places)

    def test_prepare_imprint_locations(self):
        fp = FootprintFactory()
        places = WrittenWorkIndex().prepare_imprint_locations(
            fp.book_copy.imprint.work)
        self.assertTrue(fp.book_copy.imprint.place.id in places)

    def test_prepare_actor(self):
        fp = FootprintFactory()

        actors = WrittenWorkIndex().prepare_actor(fp.book_copy.imprint.work)
        self.assertTrue(fp.book_copy.imprint.work.actor.first().id in actors)
