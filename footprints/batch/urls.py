from django.urls import path

from footprints.batch.views import BatchJobDetailView, BatchJobListView, \
    BatchJobDeleteView, BatchRowUpdateView, BatchRowDeleteView, \
    BatchJobUpdateView, BatchErrorView


urlpatterns = [
    path('',
         BatchJobListView.as_view(), name='batchjob-list-view'),
    path('job/<int:pk>/',
         BatchJobDetailView.as_view(), name='batchjob-detail-view'),
    path('job/delete/<int:pk>/',
         BatchJobDeleteView.as_view(), name='batchjob-delete-view'),
    path('job/update/<int:pk>/',
         BatchJobUpdateView.as_view(), name='batchjob-update-view'),
    path('row/update/<int:pk>/',
         BatchRowUpdateView.as_view(), name='batchrow-update-view'),
    path('row/delete/<int:pk>/',
         BatchRowDeleteView.as_view(), name='batchrow-delete-view'),
    path('job/error/<int:pk>/',
         BatchErrorView.as_view(), name='batchjob-error-view'),
]
