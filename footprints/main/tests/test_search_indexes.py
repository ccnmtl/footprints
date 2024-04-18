from django.test.testcases import TestCase
from django.utils.encoding import smart_str

from footprints.main.search_indexes import FootprintIndex, BookCopyIndex, \
    WrittenWorkIndex, ImprintIndex
from footprints.main.tests.factories import FootprintFactory


class TestFootprintIndex(TestCase):

    def test_prepare_actor(self):
        fp = FootprintFactory()

        actors = FootprintIndex().prepare_actor(fp)
        self.assertTrue(fp.actor.first().id in actors)
        self.assertTrue(fp.book_copy.imprint.work.actor.first().id
                        in actors)

    def test_prepare_actor_title(self):
        fp = FootprintFactory()

        actors = FootprintIndex().prepare_actor_title(fp)
        self.assertTrue(smart_str(fp.actor.first()) in actors)
        self.assertTrue(smart_str(fp.book_copy.imprint.work.actor.first())
                        in actors)


class TestBookCopyIndex(TestCase):

    def test_prepare_footprint_locations(self):
        fp = FootprintFactory()
        places = BookCopyIndex().prepare_footprint_location(fp.book_copy)
        self.assertTrue(fp.place.canonical_place.id in places)

    def test_prepare_actor(self):
        fp = FootprintFactory()

        actors = BookCopyIndex().prepare_actor(fp.book_copy)
        self.assertTrue(fp.actor.first().id in actors)
        self.assertTrue(fp.book_copy.imprint.work.actor.first().id
                        in actors)

    def test_prepare_actor_title(self):
        fp = FootprintFactory()

        actors = BookCopyIndex().prepare_actor_title(fp.book_copy)
        self.assertTrue(smart_str(fp.actor.first()) in actors)
        self.assertTrue(smart_str(fp.book_copy.imprint.work.actor.first())
                        in actors)


class TestImprintIndex(TestCase):

    def test_prepare_footprint_location(self):
        fp = FootprintFactory()
        places = ImprintIndex().prepare_footprint_location(
            fp.book_copy.imprint)
        self.assertTrue(fp.place.canonical_place.id in places)

    def test_prepare_actor(self):
        fp = FootprintFactory()

        actors = ImprintIndex().prepare_actor(fp.book_copy.imprint)
        self.assertTrue(fp.book_copy.imprint.actor.first().id in actors)

    def test_prepare_actor_title(self):
        fp = FootprintFactory()

        actors = ImprintIndex().prepare_actor_title(fp.book_copy.imprint)
        self.assertTrue(smart_str(fp.book_copy.imprint.actor.first())
                        in actors)


class TestWrittenWorkIndex(TestCase):

    def test_prepare_footprint_location(self):
        fp = FootprintFactory()
        places = WrittenWorkIndex().prepare_footprint_location(
            fp.book_copy.imprint.work)
        self.assertTrue(fp.place.canonical_place.id in places)

    def test_prepare_imprint_location(self):
        fp = FootprintFactory()
        places = WrittenWorkIndex().prepare_imprint_location(
            fp.book_copy.imprint.work)
        self.assertTrue(
            fp.book_copy.imprint.place.canonical_place.id in places)

    def test_prepare_actor(self):
        fp = FootprintFactory()

        actors = WrittenWorkIndex().prepare_actor(fp.book_copy.imprint.work)
        self.assertTrue(fp.book_copy.imprint.work.actor.first().id
                        in actors)

    def test_prepare_actor_title(self):
        fp = FootprintFactory()

        actors = WrittenWorkIndex().prepare_actor_title(
            fp.book_copy.imprint.work)
        self.assertTrue(smart_str(fp.book_copy.imprint.work.actor.first())
                        in actors)
