from django.conf.urls import patterns, url

from footprints.batch.views import BatchJobDetailView, BatchJobListView


urlpatterns = patterns(
    '',
    url(r'^$',
        BatchJobListView.as_view(), name='batchjob-list-view'),
    url(r'job/(?P<pk>\d+)/$',
        BatchJobDetailView.as_view(), name='batchjob-detail-view'),
)
