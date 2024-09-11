from django.contrib import messages
from django.db import transaction
from django.http.response import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls.base import reverse, reverse_lazy
from django.views.generic.base import View
from django.views.generic.detail import DetailView
from django.views.generic.edit import FormView, DeleteView

from footprints.batch.forms import CreateBatchJobForm
from footprints.batch.models import BatchJob, BatchRow
from footprints.batch.templatetags.batchrowtags import validate_field_value
from footprints.main.models import Imprint, BookCopy, Footprint, \
    Role, ExtendedDate, Actor
from footprints.mixins import (LoggedInMixin, BatchAccessMixin)
from footprints.main.utils import GeonameUtil


class BatchJobListView(LoggedInMixin, BatchAccessMixin, FormView):
    template_name = 'batch/batchjob_list.html'
    form_class = CreateBatchJobForm

    def get_context_data(self, **kwargs):
        context = super(BatchJobListView, self).get_context_data(**kwargs)
        context['jobs'] = BatchJob.objects.all().order_by('-created_at')
        return context

    def get_success_url(self):
        return reverse('batchjob-detail-view', kwargs={'pk': self.job.id})

    @transaction.atomic
    def form_valid(self, form):
        self.job = BatchJob.objects.create(created_by=self.request.user)
        table = form.csvfile_reader()
        next(table)  # skip the header row
        for row in table:
            batch_row = BatchRow(job=self.job)
            for idx, col in enumerate(row):
                setattr(batch_row, BatchRow.FIELD_MAPPING[idx], col.strip())
            batch_row.save()

        return super(BatchJobListView, self).form_valid(form)


class BatchJobDetailView(LoggedInMixin, BatchAccessMixin, DetailView):
    model = BatchJob

    def get_context_data(self, **kwargs):
        context = super(BatchJobDetailView, self).get_context_data(**kwargs)
        context['fields'] = BatchRow.imported_fields()
        return context


class BatchJobUpdateView(LoggedInMixin, BatchAccessMixin, View):

    INVALID_LOCATION = (
        'Location [{}] lookup failed at the {} level [id={}]')

    def add_place(self, obj, geoname_id):
        print('Adding place for {}'.format(geoname_id))
        obj.place = GeonameUtil().get_or_create_place(geoname_id)
        obj.save()

    def add_author(self, record, work):
        role, created = Role.objects.get_or_create(name=Role.AUTHOR)

        author, created = Actor.objects.get_or_create_by_attributes(
            record.writtenwork_author, record.writtenwork_author_viaf, role,
            record.writtenwork_author_birth_date,
            record.writtenwork_author_death_date)
        work.actor.add(author)

    def add_publisher(self, record, imprint):
        role, created = Role.objects.get_or_create(name=Role.PUBLISHER)
        publisher, created = Actor.objects.get_or_create_by_attributes(
            record.publisher, record.publisher_viaf, role, None, None)

        imprint.actor.add(publisher)

    def add_actor(self, record, footprint):
        try:
            role = Role.objects.get(name=record.footprint_actor_role)
            actor, created = Actor.objects.get_or_create_by_attributes(
                record.footprint_actor, record.footprint_actor_viaf, role,
                record.footprint_actor_birth_date,
                record.footprint_actor_death_date)
            footprint.actor.add(actor)
        except Role.DoesNotExist:
            pass  # role must be specified to create the actor

    def get_or_create_imprint(self, record):
        imprint, created = Imprint.objects.get_or_create_by_attributes(
            record.bhb_number, record.get_writtenwork_title(),
            record.imprint_title, record.publication_date)

        if record.publication_location:
            self.add_place(imprint, record.publication_location)

        self.add_author(record, imprint.work)
        self.add_publisher(record, imprint)

        return imprint

    def get_or_create_copy(self, imprint, book_call_number):

        if book_call_number:
            try:
                # imprints were validated
                return BookCopy.objects.get(imprint=imprint,
                                            call_number=book_call_number)
            except BookCopy.DoesNotExist:
                pass  # not unexpected

        # If there is no matching BookCopy for the imprint/book_call_number
        # Create a new book copy for this imprint
        copy = BookCopy.objects.create(imprint=imprint)

        if book_call_number:
            copy.call_number = book_call_number
            copy.save()

        return copy

    def create_footprint(self, record, copy):
        fp = Footprint.objects.create(
            title=record.imprint_title,
            book_copy=copy, medium=record.medium,
            medium_description=record.medium_description,
            provenance=record.provenance, call_number=record.call_number,
            notes=record.aggregate_notes())

        if record.footprint_date:
            fp.associated_date = ExtendedDate.objects.create_from_string(
                record.footprint_date)

        if record.footprint_location:
            self.add_place(fp, record.footprint_location)

        if record.footprint_narrative:
            fp.narrative = record.footprint_narrative

        fp.save()

        self.add_actor(record, fp)

        return fp

    @transaction.atomic
    def post(self, *args, **kwargs):
        pk = kwargs.get('pk', None)
        job = get_object_or_404(BatchJob, pk=pk)

        n = 0
        for record in job.batchrow_set.all():
            imprint = self.get_or_create_imprint(record)
            copy = self.get_or_create_copy(
                imprint, record.book_copy_call_number)
            footprint = self.create_footprint(record, copy)
            record.footprint = footprint
            record.save()
            n += 1

        job.processed = True
        job.save()

        msg = 'Batch job processed. {} footprints created'.format(n)
        messages.add_message(self.request, messages.INFO, msg)

        return HttpResponseRedirect(
            reverse('batchjob-detail-view', kwargs={'pk': pk}))


class BatchJobDeleteView(LoggedInMixin, BatchAccessMixin, DeleteView):
    model = BatchJob
    success_url = reverse_lazy('batchjob-list-view')


class BatchRowUpdateView(LoggedInMixin, BatchAccessMixin, View):
    def post(self, *args, **kwargs):
        pk = kwargs.get('pk', None)
        row = get_object_or_404(BatchRow, pk=pk)

        errors = {}

        # validate all the fields
        for fld in BatchRow.imported_fields():
            if fld.name in self.request.POST:
                value = self.request.POST.get(fld.name)
                setattr(row, fld.name, value)
                errors[fld.name] = validate_field_value(row, fld, value)

        row.save()

        msg = 'Record {} updated'.format(row.id)
        messages.add_message(self.request, messages.INFO, msg)

        url = reverse('batchjob-detail-view', kwargs={'pk': row.job.id})
        url += '?selected={}'.format(row.id)
        return HttpResponseRedirect(url)


class BatchRowDeleteView(LoggedInMixin, BatchAccessMixin, DeleteView):
    model = BatchRow

    def get_success_url(self):
        msg = 'Record {} deleted'.format(self.object.id)
        messages.add_message(self.request, messages.INFO, msg)

        return reverse_lazy('batchjob-detail-view',
                            kwargs={'pk': self.object.job.id})
