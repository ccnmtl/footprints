import csv

from django.core.management.base import BaseCommand

from footprints.main.models import Imprint, StandardizedIdentificationType


class Command(BaseCommand):
    help = 'Import additional data for existing imprints'

    def add_arguments(self, parser):
        parser.add_argument('filename')

    def csvfile_reader(self, filename):
        csv_file = open(filename)
        return csv.reader(csv_file)

    def handle(self, *args, **options):
        x = 0
        y = 0
        z = 0
        reader = self.csvfile_reader(options['filename'])
        bhb = StandardizedIdentificationType.objects.bhb()
        for (idx, row) in enumerate(reader):
            try:
                Imprint.objects.get(
                    standardized_identifier__identifier_type=bhb,
                    standardized_identifier__identifier__endswith=row[0])
                x += 1
            except Imprint.DoesNotExist:
                y += 1
            except Imprint.MultipleObjectsReturned:
                z += 1

        print('found {}, found multiple {}, not found {}'.format(x, z, y))
