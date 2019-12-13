from django.contrib.auth.models import User
from smoketest import SmokeTest

from footprints.pathmapper.forms import BookCopySearchForm


class DBConnectivity(SmokeTest):

    def test_retrieve(self):
        cnt = User.objects.all().count()
        # all we care about is not getting an exception
        self.assertTrue(cnt > -1)


class SolrConnectivity(SmokeTest):

    def test_retrieve(self):
        form = BookCopySearchForm({})
        if form.is_valid():
            sqs = form.search()
            self.assertTrue(sqs.count() > 1000)
