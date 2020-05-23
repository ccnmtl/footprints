from django.core.management.base import BaseCommand
from footprints.main.models import Place


class Command(BaseCommand):

    def handle(self, *app_labels, **options):
        processed = []
        for place in Place.objects.filter():
            if place.id in processed:
                continue

            matches = Place.objects.exclude(id=place.id).filter(
                canonical_place=place.canonical_place,
                alternate_name=place.alternate_name)

            if matches.count() == 0:
                continue

            print('{}: {}'.format(place.id, place.alternate_name))
            for match in matches:
                print('    {}: {}'.format(match.id, match.alternate_name))

                for imprint in match.imprint_set.all():
                    imprint.place = place
                    imprint.save()

                for footprint in match.footprint_set.all():
                    footprint.place = place
                    footprint.save()

                match.save()
                processed.append(match.id)

        # delete all deprecated places
        dups = Place.objects.filter(id__in=processed)
        self.stdout.write('Removing {} duplicates'.format(dups.count()))
        dups.delete()
