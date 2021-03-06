from django.conf.urls import url

from footprints.batch.views import BatchJobDetailView, BatchJobListView, \
    BatchJobDeleteView, BatchRowUpdateView, BatchRowDeleteView, \
    BatchJobUpdateView


urlpatterns = [
    url(r'^$',
        BatchJobListView.as_view(), name='batchjob-list-view'),
    url(r'job/(?P<pk>\d+)/$',
        BatchJobDetailView.as_view(), name='batchjob-detail-view'),
    url(r'job/delete/(?P<pk>\d+)/$',
        BatchJobDeleteView.as_view(), name='batchjob-delete-view'),
    url(r'job/update/(?P<pk>\d+)/$',
        BatchJobUpdateView.as_view(), name='batchjob-update-view'),
    url(r'row/update/(?P<pk>\d+)/$',
        BatchRowUpdateView.as_view(), name='batchrow-update-view'),
    url(r'row/delete/(?P<pk>\d+)/$',
        BatchRowDeleteView.as_view(), name='batchrow-delete-view'),
]
