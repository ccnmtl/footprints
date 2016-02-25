import csv
import urllib2

from django.conf import settings
from django.contrib import messages
from django.core.urlresolvers import reverse, reverse_lazy
from django.db import transaction
from django.http.response import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.views.generic.base import View
from django.views.generic.detail import DetailView
from django.views.generic.edit import FormView, DeleteView

from footprints.batch.forms import CreateBatchJobForm
from footprints.batch.models import BatchJob, BatchRow
from footprints.batch.templatetags.batchrowtags import validate_field_value
from footprints.main.models import Imprint, BookCopy, Footprint, \
    Role, ExtendedDate, Actor, Place
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

    @transaction.atomic
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


class BatchJobUpdateView(LoggedInStaffMixin, View):

    def add_place(self, obj, location):
        obj.place, created = Place.objects.get_or_create_from_string(
            location)

        if created:
            # reverse geocode the lat/long
            url = settings.GOOGLE_MAPS_GEOCODE
            response = urllib2.urlopen(url.format(location))
            the_json = response.read()

            components = the_json['results'][0]['address_components']

            for component in components:
                if component['types'] == 'locality':
                    obj.place.city = component['long_name']
                if component['types'] == 'country':
                    obj.place.country = component['long_name']

    def add_author(self, record, work):
        author, created = Actor.objects.get_or_create_by_attributes(
            record.writtenwork_author, record.writtenwork_author_viaf,
            Role.objects.get_author_role(),
            record.writtenwork_author_birth_date,
            record.writtenwork_author_death_date)
        work.actor.add(author)

    def add_publisher(self, record, imprint):
        publisher, created = Actor.objects.get_or_create_by_attributes(
            record.publisher, record.publisher_viaf,
            Role.objects.get_publisher_role(), None, None)

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

    def get_or_create_copy(self, call_number, imprint):
        q = {'call_number': call_number, 'book_copy__imprint': imprint}
        footprint = Footprint.objects.filter(**q).first()
        if footprint:
            copy = footprint.book_copy
        else:
            copy = BookCopy.objects.create(imprint=imprint)

        return copy

    def create_footprint(self, record, copy):
        fp = Footprint.objects.create(
            title=record.imprint_title,
            book_copy=copy, medium=record.medium,
            provenance=record.provenance, call_number=record.call_number,
            notes=record.aggregate_notes())

        if record.footprint_date:
            fp.associated_date = ExtendedDate.objects.create(
                edtf_format=record.footprint_date)

        if record.footprint_location:
            self.addPlace(record.footprint_location)

        fp.save()
        return fp

    @transaction.atomic
    def post(self, *args, **kwargs):
        pk = kwargs.get('pk', None)
        job = get_object_or_404(BatchJob, pk=pk)

        footprints = []
        for record in job.batchrow_set.all():
            imprint, created = Imprint.objects.get_or_create_by_attributes(
                record.bhb_number, record.get_writtenwork_title(),
                record.imprint_title, record.publication_date,
                record.publication_location)

            self.add_author(record, imprint.work)
            self.add_publisher(record, imprint)

            copy = self.get_or_create_copy(record.call_number, imprint)

            footprint = self.create_footprint(record, copy)
            self.add_actor(record, footprint)

            footprints.append(footprint)

        job.processed = True
        job.save()

        msg = 'Batch job processed. {} footprints created'.format(
            len(footprints))
        messages.add_message(self.request, messages.INFO, msg)

        return HttpResponseRedirect(
            reverse('batchjob-detail-view', kwargs={'pk': pk}))


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
            if fld.name in self.request.POST:
                value = self.request.POST.get(fld.name)
                setattr(row, fld.name, value)
                errors[fld.name] = validate_field_value(fld, value)

        row.save()

        return self.render_to_json_response({
            'errors': errors
        })


class BatchRowDeleteView(LoggedInStaffMixin, DeleteView):
    model = BatchRow

    def get_success_url(self):
        msg = 'Record {} deleted'.format(self.object.id)
        messages.add_message(self.request, messages.INFO, msg)

        return reverse_lazy('batchjob-detail-view',
                            kwargs={'pk': self.object.job.id})
