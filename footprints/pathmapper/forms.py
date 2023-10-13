from datetime import date, datetime

from django import forms
from django.db.models.query_utils import Q
from django.utils.encoding import smart_str
from haystack.forms import ModelSearchForm

from footprints.main.models import (
    BookCopy, Imprint, WrittenWork, Place, Actor, Footprint)
from footprints.main.utils import camel_to_snake, snake_to_camel


class ModelSearchFormEx(ModelSearchForm):
    q = forms.CharField(required=False)

    work = forms.IntegerField(required=False)
    imprint = forms.IntegerField(required=False)

    footprint_start = forms.IntegerField(required=False, min_value=1000)
    footprint_end = forms.IntegerField(required=False, min_value=1000)
    footprint_range = forms.BooleanField(
        required=False, widget=forms.HiddenInput())

    pub_start = forms.IntegerField(required=False, min_value=1000)
    pub_end = forms.IntegerField(required=False, min_value=1000)
    pub_range = forms.BooleanField(
        required=False, widget=forms.HiddenInput())

    imprint_location = forms.IntegerField(required=False)
    footprint_location = forms.IntegerField(required=False)

    actor = forms.CharField(required=False)

    censored = forms.BooleanField(required=False)
    expurgated = forms.BooleanField(required=False)

    def transform_data(self):
        for key, value in self.data.items():
            snake_key = camel_to_snake(key)
            self.cleaned_data[snake_key] = value

    def transform_errors(self):
        errors = {}
        for key, value in self.errors.items():
            snake_key = snake_to_camel(key)
            errors[snake_key] = value
        self.errors.update(errors)

    def clean_year(self, fieldname):
        year = self.cleaned_data.get(fieldname, '')

        if isinstance(year, str):
            try:
                self.cleaned_data[fieldname] = int(year)
            except ValueError:
                return
        elif not isinstance(year, int):
            return

        now = datetime.now()
        if self.cleaned_data[fieldname] > now.year:
            self._errors[fieldname] = self.error_class([
                'No future year'])
        if self.cleaned_data[fieldname] < 1000:
            self._errors[fieldname] = self.error_class([
                'Year must be greater than 1000'])

    def clean_range(self, fieldname):
        val = self.cleaned_data.get(fieldname, False)
        self.cleaned_data[fieldname] = val in [True, 'true']

    def handle_single_year(self, field_name, start_year):
        kwargs = {}
        start_year = int(start_year)
        kwargs['{}__gte'.format(field_name)] = date(
            start_year, 1, 1)
        kwargs['{}__lte'.format(field_name)] = date(
            start_year, 12, 31)
        return kwargs

    def handle_range(self, field_name1, field_name2, start_year, end_year):
        kwargs = {}
        if start_year:
            start_year = int(start_year)
            kwargs['{}__gte'.format(field_name1)] = date(
                start_year, 1, 1)
        if end_year:
            end_year = int(end_year)
            kwargs['{}__lte'.format(field_name2)] = date(
                end_year, 12, 31)
        return kwargs

    def handle_footprint_year(self):
        kwargs = {}
        start_year = self.cleaned_data.get('footprint_start')
        end_year = self.cleaned_data.get('footprint_end')
        ranged = self.cleaned_data.get('footprint_range')

        if ranged:
            kwargs.update(self.handle_range(
                'footprint_start_date', 'footprint_end_date',
                start_year, end_year))
        elif start_year:
            kwargs.update(self.handle_single_year(
                'footprint_start_date', start_year))
        return kwargs

    def format_solr_date(self, dt):
        return dt.strftime('%Y-%m-%dT00:00:00Z')

    def format_footprint_year_query(self, fld, start_year, end_year, ranged):
        # Solr specific syntax to complete a self-join to footprint data
        q = '{{!join from={} to=django_id}}'\
            'django_ct:"main.footprint" AND footprint_start_date:[{} TO {}]'\
            ' AND footprint_end_date:[{} TO {}]'

        if ranged:
            if start_year:
                start = self.format_solr_date(date(start_year, 1, 1))
            else:
                start = '*'

            if end_year:
                end = self.format_solr_date(date(end_year, 12, 31))
            else:
                end = '*'
        else:
            start = self.format_solr_date(date(start_year, 1, 1))
            end = self.format_solr_date(date(start_year, 12, 31))

        return q.format(fld, start, end, start, end)

    def filter_by_footprint_year(self, fld, sqs):
        start_year = self.cleaned_data.get('footprint_start')
        end_year = self.cleaned_data.get('footprint_end')
        ranged = self.cleaned_data.get('footprint_range')

        if not start_year and not end_year:
            # nothing to filter by, return the query set intact
            return sqs

        q = self.format_footprint_year_query(fld, start_year, end_year, ranged)
        return sqs.narrow(q)

    def handle_pub_year(self):
        kwargs = {}
        start_year = self.cleaned_data.get('pub_start')
        end_year = self.cleaned_data.get('pub_end')
        ranged = self.cleaned_data.get('pub_range')

        if ranged:
            kwargs.update(self.handle_range(
                'pub_start_date', 'pub_end_date',
                start_year, end_year))
        elif start_year:
            kwargs.update(self.handle_single_year(
                'pub_start_date', start_year))
        return kwargs

    def handle_imprint_location(self):
        kwargs = {}
        loc = self.cleaned_data.get('imprint_location')
        if loc:
            kwargs['imprint_location'] = loc
        return kwargs

    def handle_imprint_location_title(self):
        args = []
        # narrow by imprint locqtions, if selected
        loc = self.cleaned_data.get('imprint_location')
        if loc:
            # @todo - this glosses over place data integrity issues
            place = Place.objects.get(id=loc)
            args.append(
                Q(imprint_location_title_exact__in=[smart_str(place)]))
        return args

    def handle_footprint_location(self):
        kwargs = {}
        loc = self.cleaned_data.get('footprint_location')
        if loc:
            kwargs['footprint_location'] = loc
        return kwargs

    def handle_footprint_location_title(self):
        args = []
        # narrow by imprint locqtions, if selected
        loc = self.cleaned_data.get('footprint_location')
        if loc:
            # @todo - this glosses over place data integrity issues
            place = Place.objects.get(id=loc)
            args.append(
                Q(footprint_location_title_exact__in=[smart_str(place)]))
        return args

    def handle_actor(self):
        args = []
        # narrow by imprint locqtions, if selected
        actor_id = self.cleaned_data.get('actor')
        if actor_id:
            # @todo - this glosses over place data integrity issues
            args.append(Q(actor_exact__in=[actor_id]))
        return args

    def handle_boolean(self, field_name):
        d = {}
        val = self.cleaned_data.get(field_name, '')
        if val == 'yes':
            d[field_name] = True
        elif val == 'no':
            d[field_name] = False
        return d

    def clean(self):
        self.transform_data()
        cleaned_data = super().clean()

        self.clean_year('footprint_start')
        self.clean_year('footprint_end')

        if (cleaned_data.get('footprint_start', None) and
            cleaned_data.get('footprint_end', None) and
            cleaned_data['footprint_start'] >
                cleaned_data['footprint_end']):
            self._errors['footprint_start'] = self.error_class([
                'Start year must be less than end year'])

        self.clean_year('pub_start')
        self.clean_year('pub_end')

        self.clean_range('pub_range')
        self.clean_range('footprint_range')

        if (cleaned_data.get('pub_start', None) and
            cleaned_data.get('pub_end', None) and
            cleaned_data['pub_start'] >
                cleaned_data['pub_end']):
            self._errors['pub_start'] = self.error_class([
                'Start year must be less than end year'])

        self.transform_errors()


class BookCopySearchForm(ModelSearchFormEx):
    class Meta:
        model = BookCopy

    def arguments(self):
        args = []
        kwargs = {
            'django_ct': 'main.bookcopy',
        }

        work_id = self.cleaned_data.get('work')
        if work_id:
            kwargs['work_id'] = work_id

        imprint_id = self.cleaned_data.get('imprint')
        if imprint_id:
            kwargs['imprint_id'] = imprint_id

        kwargs.update(self.handle_imprint_location())
        kwargs.update(self.handle_footprint_location())
        args += self.handle_actor()

        kwargs.update(self.handle_boolean('censored'))
        kwargs.update(self.handle_boolean('expurgated'))

        kwargs.update(self.handle_pub_year())
        return args, kwargs

    def search(self):
        args, kwargs = self.arguments()
        sqs = self.searchqueryset.filter(*args, **kwargs)
        sqs = self.filter_by_footprint_year('book_copy_id', sqs)
        return sqs


class BookCopyFootprintsForm(ModelSearchForm):
    ''' Given a list of bookcopies, retrieve the associated footprints'''
    class Meta:
        model = Footprint

    def search(self, copies):
        args = [Q(book_copy_id__in=copies)]
        kwargs = {
            'django_ct': 'main.footprint',
        }
        sqs = self.searchqueryset.filter(*args, **kwargs)
        return sqs


class ImprintSearchForm(ModelSearchFormEx):
    class Meta:
        model = Imprint

    def arguments(self):
        args = []
        kwargs = {'django_ct': 'main.imprint'}

        q = self.cleaned_data.get('q', '')
        if q:
            kwargs['content'] = q

        work_id = self.cleaned_data.get('work')
        if work_id:
            kwargs['work_id'] = work_id

        imprint_id = self.cleaned_data.get('selected')
        if imprint_id:
            kwargs['object_id'] = imprint_id

        kwargs.update(self.handle_imprint_location())
        kwargs.update(self.handle_footprint_location())
        args += self.handle_actor()

        kwargs.update(self.handle_pub_year())
        return args, kwargs

    def search(self):
        args, kwargs = self.arguments()
        sqs = self.searchqueryset.filter(*args, **kwargs)
        sqs = self.filter_by_footprint_year('imprint_id', sqs)
        return sqs


class WrittenWorkSearchForm(ModelSearchFormEx):

    class Meta:
        model = WrittenWork

    def arguments(self):
        args = []
        kwargs = {
            'django_ct': 'main.writtenwork',
        }

        q = self.cleaned_data.get('q', '')
        if q:
            kwargs['content'] = q

        work_id = self.cleaned_data.get('selected')
        if work_id:
            kwargs['object_id'] = work_id

        kwargs.update(self.handle_imprint_location())
        kwargs.update(self.handle_footprint_location())
        args += self.handle_actor()

        kwargs.update(self.handle_pub_year())
        return args, kwargs

    def search(self):
        args, kwargs = self.arguments()
        sqs = self.searchqueryset.filter(*args, **kwargs)
        sqs = self.filter_by_footprint_year('work_id', sqs)
        return sqs


SEARCH_FOR_IMPRINT_LOCATION = 'imprint'
SEARCH_FOR_FOOTPRINT_LOCATION = 'footprint'
PLACE_SEARCH_CHOICES = (
    (SEARCH_FOR_IMPRINT_LOCATION, 'Search by Imprint Location'),
    (SEARCH_FOR_FOOTPRINT_LOCATION, 'Search by Footprint Location'),
)


class PlaceSearchForm(ModelSearchFormEx):
    q = forms.CharField(required=False)
    search_for = forms.ChoiceField(
        choices=PLACE_SEARCH_CHOICES, required=False)

    class Meta:
        model = Place

    def search_for_footprint_locations(self, args, kwargs):
        kwargs['django_ct'] = 'main.footprint'

        imprint_id = self.cleaned_data.get('imprint')
        if imprint_id:
            kwargs['imprint_id'] = imprint_id

        kwargs.update(self.handle_imprint_location())
        kwargs.update(self.handle_footprint_year())

        sqs = self.searchqueryset.filter(*args, **kwargs)

        counts = sqs.facet('footprint_location').facet_counts()
        return [c[0] for c in counts['fields']['footprint_location']
                if c[1] > 0]

    def search_for_imprint_locations(self, args, kwargs):
        kwargs['django_ct'] = 'main.imprint'

        imprint_id = self.cleaned_data.get('imprint')
        if imprint_id:
            kwargs['object_id'] = imprint_id

        kwargs.update(self.handle_footprint_location())

        sqs = self.searchqueryset.filter(*args, **kwargs)
        sqs = self.filter_by_footprint_year('imprint_id', sqs)

        counts = sqs.facet('imprint_location').facet_counts()
        return [c[0] for c in counts['fields']['imprint_location'] if c[1] > 0]

    def search(self):
        args = []
        kwargs = {}

        work_id = self.cleaned_data.get('work')
        if work_id:
            kwargs['work_id'] = work_id

        kwargs.update(self.handle_pub_year())
        args += self.handle_actor()

        search_for = self.cleaned_data.get('search_for', '')
        if search_for == SEARCH_FOR_FOOTPRINT_LOCATION:
            return self.search_for_footprint_locations(args, kwargs)
        else:
            return self.search_for_imprint_locations(args, kwargs)


class ActorSearchForm(ModelSearchFormEx):

    class Meta:
        model = Actor

    def arguments(self, django_ct):
        args = []
        kwargs = {'django_ct': django_ct}

        q = self.cleaned_data.get('q', '')
        if q:
            args.append(Q(actor_title_exact__contains=q))

        work_id = self.cleaned_data.get('work')
        if work_id:
            kwargs['work_id'] = work_id

        imprint_id = self.cleaned_data.get('imprint')
        if imprint_id:
            kwargs['imprint_id'] = imprint_id

        kwargs.update(self.handle_imprint_location())
        kwargs.update(self.handle_footprint_location())
        kwargs.update(self.handle_pub_year())
        return args, kwargs

    def search_by_writtenwork(self):
        args, kwargs = self.arguments('main.writtenwork')
        sqs = self.searchqueryset.filter(*args, **kwargs)
        sqs = self.filter_by_footprint_year('work_id', sqs)
        counts = sqs.facet('actor').facet_counts()
        return {c[0] for c in counts['fields']['actor'] if c[1] > 0}

    def search_by_imprint(self):
        args, kwargs = self.arguments('main.imprint')
        sqs = self.searchqueryset.filter(*args, **kwargs)
        sqs = self.filter_by_footprint_year('work_id', sqs)
        counts = sqs.facet('actor').facet_counts()
        return {c[0] for c in counts['fields']['actor'] if c[1] > 0}

    def search_by_footprint(self):
        args, kwargs = self.arguments('main.footprint')
        kwargs.update(self.handle_footprint_year())
        sqs = self.searchqueryset.filter(*args, **kwargs)
        counts = sqs.facet('actor').facet_counts()
        return {c[0] for c in counts['fields']['actor'] if c[1] > 0}

    def search(self):
        actors = self.search_by_writtenwork()
        actors.update(self.search_by_imprint())
        actors.update(self.search_by_footprint())
        return actors
