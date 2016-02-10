import csv

from django.core.urlresolvers import reverse, reverse_lazy
from django.shortcuts import get_object_or_404
from django.views.generic.base import View
from django.views.generic.detail import DetailView
from django.views.generic.edit import FormView, DeleteView

from footprints.batch.forms import CreateBatchJobForm
from footprints.batch.models import BatchJob, BatchRow
from footprints.batch.templatetags.batchrowtags import validate_field_value
from footprints.mixins import LoggedInStaffMixin, JSONResponseMixin


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
                setattr(batch_row, BatchRow.FIELD_MAPPING[idx], col.strip())
            batch_row.save()

        return super(BatchJobListView, self).form_valid(form)


class BatchJobDetailView(LoggedInStaffMixin, DetailView):
    model = BatchJob

    def get_context_data(self, **kwargs):
        context = super(BatchJobDetailView, self).get_context_data(**kwargs)
        context['fields'] = BatchRow.imported_fields()
        return context


class BatchJobDeleteView(LoggedInStaffMixin, DeleteView):
    model = BatchJob
    success_url = reverse_lazy('batchjob-list-view')


class BatchRowUpdateView(LoggedInStaffMixin, JSONResponseMixin, View):
    def post(self, *args, **kwargs):
        pk = kwargs.get('pk', None)
        row = get_object_or_404(BatchRow, pk=pk)

        errors = {}

        # validate all the fields
        for fld in BatchRow.imported_fields():
            value = self.request.POST.get(fld.name, None)
            setattr(row, fld.name, value)
            errors[fld.name] = validate_field_value(fld, value)

        row.save()

        return self.render_to_json_response({
            'errors': errors
        })
