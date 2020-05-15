from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.measure import D
from django.core.management.base import BaseCommand

from footprints.main.models import CanonicalPlace


class Command(BaseCommand):

    def handle(self, *app_labels, **options):
        processed = []
        for cplace in CanonicalPlace.objects.filter():
            if cplace.id in processed:
                continue

            # find matching places based on name and proximity
            pnt = cplace.latlng
            matches = CanonicalPlace.objects.exclude(id=cplace.id).filter(
                canonical_name=cplace.canonical_name,
                latlng__distance_lte=(pnt, D(mi=35))
                ).annotate(d=Distance('latlng', pnt))

            if matches.count() == 0:
                continue

            print('{}: {}'.format(cplace.id, cplace.canonical_name))
            for match in matches:
                print('    {}: {} {:.2f}'.format(
                    match.id, match.canonical_name, match.d.mi))

                for place in match.place_set.all():
                    # detach references to this canonical place
                    place.canonical_place = cplace
                    place.save()

                match.save()
                processed.append(match.id)

        # delete all deprecated canonical places
        dups = CanonicalPlace.objects.filter(id__in=processed)
        self.stdout.write('Removing {} duplicates'.format(dups.count()))
        dups.delete()
