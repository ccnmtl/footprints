import factory

from footprints.batch.models import BatchJob, BatchRow
from footprints.main.tests.factories import UserFactory


class BatchJobFactory(factory.DjangoModelFactory):
    class Meta:
        model = BatchJob

    created_by = factory.SubFactory(UserFactory)


class BatchRowFactory(factory.DjangoModelFactory):
    class Meta:
        model = BatchRow

    job = factory.SubFactory(BatchJobFactory)

    catalog_url = 'http://clio.columbia.edu/catalog/11262981'
    bhb_number = '106200'
    imprint_title = 'Sefer Leshon limudim she-hiber David Yahya.'
    writtenwork_title = 'Leshon Limudim'
    writtenwork_author = 'David ben Solomon Ibn Yahya'
    writtenwork_author_viaf = '7742556'
    writtenwork_author_birth_date = '1702'
    writtenwork_author_death_date = '1789'

    # imprint publisher/printer information
    publisher = 'Eliezer Soncino'
    publisher_viaf = '297361612'
    publication_location = '41.0136,28.9550'
    publication_date = '1542'

    medium = 'Library Catalog/Union Catalog'
    provenance = 'Columbia University, New York, New York'
    call_number = 'B893.14 Y11'

    footprint_actor = 'Nicolo Maria Castaldi'
    footprint_actor_viaf = ''
    footprint_actor_role = 'Expurgator'
    footprint_actor_birth_date = ''
    footprint_actor_death_date = ''
    footprint_notes = 'Levita, Elijah.'
    footprint_location = '41.0136,28.9550'
    footprint_date = '1989'
