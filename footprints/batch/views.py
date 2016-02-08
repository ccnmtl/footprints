import csv

from django.core.urlresolvers import reverse, reverse_lazy
from django.views.generic.detail import DetailView
from django.views.generic.edit import FormView, DeleteView

from footprints.batch.forms import CreateBatchJobForm
from footprints.batch.models import BatchJob, BatchRow
from footprints.mixins import LoggedInStaffMixin


class BatchJobListView(LoggedInStaffMixin, FormView):
    template_name = 'batch/batchjob_list.html'
    form_class = CreateBatchJobForm

    def get_context_data(self, **kwargs):
        context = super(BatchJobListView, self).get_context_data(**kwargs)
        context['jobs'] = BatchJob.objects.all()
        return context

    def get_success_url(self):
        return reverse('batchjob-detail-view', kwargs={'pk': self.job.id})

    def form_valid(self, form):
        self.job = BatchJob.objects.create(created_by=self.request.user)
        table = csv.reader(form.cleaned_data['csvfile'])
        table.next()  # skip the header row
        for row in table:
            batch_row = BatchRow(job=self.job)
            for idx, col in enumerate(row):
                setattr(batch_row, BatchRow.FIELD_MAPPING[idx], col)
            batch_row.save()

        return super(BatchJobListView, self).form_valid(form)


class BatchJobDetailView(LoggedInStaffMixin, DetailView):
    model = BatchJob

    def get_context_data(self, **kwargs):
        context = super(BatchJobDetailView, self).get_context_data(**kwargs)
        context['fields'] = BatchRow.FIELD_MAPPING
        return context


class BatchJobDeleteView(LoggedInStaffMixin, DeleteView):
    model = BatchJob
    success_url = reverse_lazy('batchjob-list-view')
