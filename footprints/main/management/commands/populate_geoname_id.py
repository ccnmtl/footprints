from django.conf import settings
from django.core.management.base import BaseCommand
from django.db.utils import IntegrityError
import requests

from footprints.main.models import CanonicalPlace


class Command(BaseCommand):

    def get_match(self, lat, lng):
        nearbyUrl = ('https://secure.geonames.org/findNearby?'
                     'featureClass=P&featureClass=A&'
                     'username={}&type=json&lat={}&lng={}').format(
                         settings.GEONAMES_KEY, lat, lng)
        results = requests.get(nearbyUrl)
        the_json = results.json()
        if 'geonames' in the_json:
            return the_json['geonames'][0]

    def handle(self, *app_labels, **options):
        for cplace in CanonicalPlace.objects.filter(geoname_id=None)[:100]:
            # query the geonames api and retrieve a matching id
            match = self.get_match(cplace.latitude(), cplace.longitude())
            if not match:
                # geonames has a limit of 1,000 tries per hour
                # exit gracefully
                print('Hourly limit exceeded. Try again later')
                break

            name = match['name']
            if match['adminName1']:
                name += ', ' + match['adminName1']
            name += ', ' + match['countryName']

            # write out the match
            print('{}:{} >> {}'.format(
                cplace.id, cplace.canonical_name, name))

            try:
                # update canonical name to match and stash the geoname id
                cplace.canonical_name = name
                cplace.geoname_id = match['geonameId']
                cplace.save()
            except IntegrityError:
                # geonames are unique. ignore duplicates
                continue
