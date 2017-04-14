from django.test.testcases import TestCase
from django.utils.encoding import smart_text

from footprints.main.search_indexes import FootprintIndex
from footprints.main.tests.factories import FootprintFactory


class TestFootprintIndex(TestCase):

    def test_prepare_actor(self):
        fp = FootprintFactory()

        actors = FootprintIndex().prepare_actor(fp)
        self.assertTrue(smart_text(fp.actor.first()) in actors)
        self.assertTrue(smart_text(fp.book_copy.imprint.work.actor.first())
                        in actors)
