from PyZ3950 import zoom  # http://zoom.z3950.org/bind/python/
from PyZ3950.zmarc import MARC
from django.core.management.base import BaseCommand


# on a fresh bootstrap, ply/ccl.py needs to be tweaked to work properly
class Command(BaseCommand):

    def handle(self, *app_labels, **options):

        # conn = zoom.Connection('z3950.loc.gov', 7090)
        conn = zoom.Connection('clio-db.cc.columbia.edu', 7090)

        conn.databaseName = 'Voyager'
        conn.preferredRecordSyntax = 'USMARC'

        # query = zoom.Query('CCL', 'isbn=0253333490')
        query = zoom.Query('CCL', 'title=Dinosaur')

        res = conn.search(query)
        marc = MARC(MARC=res[0].data)

        print marc.toMODS()

        conn.close()
