import csv
import re
import time

from django.core.management.base import BaseCommand
from django.db.models.query_utils import Q

from footprints.main.models import (
    Imprint, StandardizedIdentificationType,
    Language, ExtendedDate, StandardizedIdentification,
    ImprintAlternateTitle, CanonicalPlace,
    Person, Actor, Role, WrittenWork, Place)


FIELD_BHB_NUMBER = 0
FIELD_LANGUAGE = 1
FIELD_AUTHOR = 2
FIELD_TITLE = 3
FIELD_WORK_TITLE = 4
FIELD_SUBTITLE = 5
FIELD_PLACE_MURKY = 6
FIELD_PUBLICATION_PLACE = 7
FIELD_LOCSTATUS = 8  # unused
FIELD_PRINTER_MURKEY = 9  # unused
FIELD_PUBLISHER = 10
FIELD_YEAR_MURKY = 11  # unused
FIELD_PUBLICATION_YEAR = 12
FIELD_DATE_STATUS = 13  # unused
FIELD_RANGE_FORM = 14  # unused
FIELD_RANGE_TO = 15  # unused
FIELD_DECADE = 16  # unused
FIELD_HASKAMA = 17  # unused
FIELD_NOTE = 18


class Command(BaseCommand):
    help = 'Import additional data for existing imprints'

    def add_arguments(self, parser):
        parser.add_argument('filename')

    def clean(self, s):
        s = re.sub(r'\[!\]', '', s)
        s = re.sub(r'\?', '', s)
        s = re.sub(r'^\(', '', s)
        s = re.sub(r'\)$', '', s)
        s = re.sub(r'^\[', '', s)
        s = re.sub(r'\]$', '', s)
        return s.strip()

    def format_bhb_number(self, bhb):
        if len(bhb) > 0 and len(bhb) < 9:
            bhb = bhb.rjust(9, '0')
        return bhb

    def handle_language(self, imprint, row):
        language = Language.objects.get(marc_code=row[FIELD_LANGUAGE])
        imprint.language.add(language)

    def handle_title(self, imprint, row, bhb_number):
        title = self.clean(row[FIELD_TITLE])
        if imprint.title == title:
            return

        language = Language.objects.get(marc_code=row[FIELD_LANGUAGE])

        try:
            ImprintAlternateTitle.objects.get(
                standardized_identifier__identifier=bhb_number,
                alternate_title=title,
                language=language)
        except ImprintAlternateTitle.DoesNotExist:
            bhb_type = StandardizedIdentificationType.objects.bhb()
            si = StandardizedIdentification.objects.filter(
                identifier_type=bhb_type, identifier=bhb_number).first()
            if not si:
                si = StandardizedIdentification.objects.create(
                    identifier_type=bhb_type, identifier=bhb_number)

            ImprintAlternateTitle.objects.create(
                standardized_identifier=si,
                alternate_title=title,
                language=language)

    def handle_publication_date(self, imprint, row):
        if imprint.publication_date:
            return

        dt = ExtendedDate.objects.create_from_string(
            row[FIELD_PUBLICATION_YEAR])
        imprint.publication_date = dt

    def handle_place(self, imprint, row):
        place_name = row[FIELD_PUBLICATION_PLACE]
        alt_place_name = self.clean(row[FIELD_PLACE_MURKY])

        if imprint.place:
            imprint.place.alternate_name = alt_place_name
            imprint.place.save()
        else:
            # all imprints in the spreadsheet have a matching canonical place
            cp = CanonicalPlace.objects.filter(
                Q(canonical_name__startswith=place_name) |
                Q(place__alternate_name__startswith=place_name) |
                Q(place__alternate_name__startswith=alt_place_name)).first()

            imprint.place = Place.objects.filter(
                canonical_place=cp, alternate_name=alt_place_name).first()
            if not imprint.place:
                imprint.place = Place.objects.create(
                    canonical_place=cp, alternate_name=alt_place_name)

    def get_or_create_actor(self, role, name):
        name = name.strip()
        if not name or len(name) < 1:
            return None

        # is there an existing actor or person with this name?
        actor = Actor.objects.filter(
            Q(alias=name) | Q(person__name=name)).first()
        person = Person.objects.filter(name=name).first()

        if not actor and not person:
            person = Person.objects.create(name=name)
            actor = Actor.objects.create(person=person, role=role, alias=name)
        elif not actor:
            actor = Actor.objects.create(person=person, role=role, alias=name)

        return actor

    def handle_actors(self, imprint, row):
        author_name = row[FIELD_AUTHOR]
        role = Role.objects.get(name=Role.AUTHOR)
        actor = self.get_or_create_actor(role, author_name)
        if actor:
            imprint.work.actor.add(actor)

        publisher_name = row[FIELD_PUBLISHER]
        role = Role.objects.get(name=Role.PUBLISHER)
        actor = self.get_or_create_actor(role, publisher_name)
        if actor:
            imprint.actor.add(actor)

    def handle_notes(self, imprint, row):
        fields = []
        if imprint.notes:
            fields.append(imprint.notes)
        if row[FIELD_SUBTITLE]:
            fields.append('Subtitle: ' + row[FIELD_SUBTITLE])
        if row[FIELD_NOTE]:
            fields.append('BHB note: ' + row[FIELD_NOTE])
        imprint.notes = '<br />'.join(fields)

    def create_imprint(self, row, bhb_number):
        # get or create the written work
        title = self.clean(row[FIELD_WORK_TITLE])
        work, created = WrittenWork.objects.get_or_create(title=title)

        # create the imprint
        title = self.clean(row[FIELD_TITLE])
        imprint = Imprint.objects.create(work=work, title=title)

        # attach the bhb number
        bhb = StandardizedIdentificationType.objects.bhb()
        si = StandardizedIdentification.objects.create(
            identifier_type=bhb, identifier=bhb_number)
        imprint.standardized_identifier.add(si)

        # add language
        self.handle_language(imprint, row)

        # add the published date
        self.handle_publication_date(imprint, row)

        # add a canonical place and/or place name alias
        self.handle_place(imprint, row)

        # add the written work author and the imprint publisher
        self.handle_actors(imprint, row)

        # Add information to the notes field
        self.handle_notes(imprint, row)

        # Save anything that needs saved
        imprint.save()

        return imprint

    def update_imprint(self, imprint, row, bhb_number):
        # add a title alias if the imprint title does not match
        self.handle_title(imprint, row, bhb_number)

        # add language
        self.handle_language(imprint, row)

        # add the published date if the imprint does not have one
        self.handle_publication_date(imprint, row)

        # add a canonical place and/or place name alias
        self.handle_place(imprint, row)

        # add the written work author and the imprint publisher
        self.handle_actors(imprint, row)

        # Add information to the notes field
        self.handle_notes(imprint, row)

        # Save anything that needs saved
        imprint.save()

    def log_entry(self, row_idx, imprint, status):
        publishers = [str(actor) for actor in imprint.publishers()]
        authors = [str(actor) for actor in imprint.work.authors()]

        alternate_place_name = ''
        canonical_place_name = ''
        if imprint.place:
            alternate_place_name = imprint.place.alternate_name
            canonical_place_name = \
                imprint.place.canonical_place.canonical_name

        fields = [
            str(row_idx + 1),
            status,
            imprint.get_bhb_number().identifier,
            str(imprint.id),
            imprint.title,
            ' | '.join(imprint.get_alternate_titles()),
            imprint.work.title,
            ' | '.join(imprint.language.values_list('name', flat=True)),
            str(imprint.publication_date),
            alternate_place_name,
            canonical_place_name,
            ' | '.join(publishers),
            ' | '.join(authors),
            imprint.notes or '',
        ]
        return ','.join('"{0}"'.format(fld) for fld in fields)

    def handle(self, *args, **options):
        created = 0
        updated = 0

        csv_file = open(options['filename'])
        reader = csv.reader(csv_file)

        bhb = StandardizedIdentificationType.objects.bhb()
        for idx, row in enumerate(reader):
            if idx == 0:
                continue

            bhb_number = self.format_bhb_number(str(row[FIELD_BHB_NUMBER]))
            imprints = Imprint.objects.filter(
                standardized_identifier__identifier_type=bhb,
                standardized_identifier__identifier=bhb_number).distinct()

            if imprints.count() < 1:
                created += 1
                imprint = self.create_imprint(row, bhb_number)
                print(self.log_entry(idx, imprint, 'created'))
            else:
                updated += imprints.count()
                for imprint in imprints:
                    print(self.log_entry(idx, imprint, 'existing'))
                    self.update_imprint(imprint, row, bhb_number)
                    print(self.log_entry(idx, imprint, 'updated'))

            # take a breath
            time.sleep(0.2)

        csv_file.close()
        print('updated {}, created {}'.format(updated, created))
