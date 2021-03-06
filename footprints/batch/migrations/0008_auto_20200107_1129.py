# Generated by Django 2.2.9 on 2020-01-07 16:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('batch', '0007_batchrow_footprint_narrative'),
    ]

    operations = [
        migrations.AlterField(
            model_name='batchrow',
            name='bhb_number',
            field=models.TextField(help_text='This field is required. Please enter a numeric BHB identifier.', verbose_name='BHB Number'),
        ),
        migrations.AlterField(
            model_name='batchrow',
            name='book_copy_call_number',
            field=models.CharField(blank=True, max_length=256, null=True, verbose_name='Book Copy Call Number'),
        ),
        migrations.AlterField(
            model_name='batchrow',
            name='call_number',
            field=models.TextField(blank=True, null=True, verbose_name='Evidence Call Number'),
        ),
        migrations.AlterField(
            model_name='batchrow',
            name='catalog_url',
            field=models.TextField(blank=True, help_text='Please enter a valid url format.', null=True, verbose_name='Catalog Link'),
        ),
        migrations.AlterField(
            model_name='batchrow',
            name='footprint_actor',
            field=models.TextField(blank=True, help_text='An actor name is required when a role is specified.', null=True, verbose_name='Footprint Actor'),
        ),
        migrations.AlterField(
            model_name='batchrow',
            name='footprint_actor_birth_date',
            field=models.TextField(blank=True, help_text="This value is invalid. See <a target='_blank' href='https://github.com/ccnmtl/footprints/wiki/Batch-Import-Format'>date formats</a> for rules.", null=True, verbose_name='Footprint Actor Birth Date'),
        ),
        migrations.AlterField(
            model_name='batchrow',
            name='footprint_actor_death_date',
            field=models.TextField(blank=True, help_text="This value is invalid. See <a target='_blank' href='https://github.com/ccnmtl/footprints/wiki/Batch-Import-Format'>date formats</a> for rules.", null=True, verbose_name='Footprint Actor Death Date'),
        ),
        migrations.AlterField(
            model_name='batchrow',
            name='footprint_actor_role',
            field=models.TextField(blank=True, help_text="A role is required when an actor's name is specified. The value is invalid or missing. See <a target='_blank' href='https://github.com/ccnmtl/footprints/wiki/Batch-Import-Format'>roles</a> for a list of choices.", null=True, verbose_name='Footprint Actor Role'),
        ),
        migrations.AlterField(
            model_name='batchrow',
            name='footprint_actor_viaf',
            field=models.TextField(blank=True, help_text='This value is invalid. Please enter a numeric VIAF identifier.', null=True, verbose_name='Footprint Actor VIAF'),
        ),
        migrations.AlterField(
            model_name='batchrow',
            name='footprint_date',
            field=models.TextField(blank=True, help_text="This value is invalid. See <a target='_blank' href='https://github.com/ccnmtl/footprints/wiki/Batch-Import-Format'>date formats</a> for rules.", null=True, verbose_name='Footprint Date'),
        ),
        migrations.AlterField(
            model_name='batchrow',
            name='footprint_location',
            field=models.TextField(blank=True, help_text='This value is invalid. Please enter a geocode, e.g. 51.752021,-1.2577.', null=True, verbose_name='Footprint Location'),
        ),
        migrations.AlterField(
            model_name='batchrow',
            name='footprint_narrative',
            field=models.TextField(blank=True, null=True, verbose_name='Footprint Narrative'),
        ),
        migrations.AlterField(
            model_name='batchrow',
            name='footprint_notes',
            field=models.TextField(blank=True, null=True, verbose_name='Footprint Notes'),
        ),
        migrations.AlterField(
            model_name='batchrow',
            name='imprint_title',
            field=models.TextField(help_text='This field is required.', verbose_name='Imprint'),
        ),
        migrations.AlterField(
            model_name='batchrow',
            name='medium',
            field=models.TextField(help_text='This field is required.', verbose_name='Evidence Type'),
        ),
        migrations.AlterField(
            model_name='batchrow',
            name='provenance',
            field=models.TextField(help_text='This field is required.', verbose_name='Evidence Location'),
        ),
        migrations.AlterField(
            model_name='batchrow',
            name='publication_date',
            field=models.TextField(blank=True, help_text="This value is invalid. See <a target='_blank' href='https://github.com/ccnmtl/footprints/wiki/Batch-Import-Format'>date formats</a> for rules.", null=True, verbose_name='Publication Date'),
        ),
        migrations.AlterField(
            model_name='batchrow',
            name='publication_location',
            field=models.TextField(blank=True, help_text='This value is invalid. Please enter a geocode, e.g. 51.752021,-1.2577.', null=True, verbose_name='Publication Location'),
        ),
        migrations.AlterField(
            model_name='batchrow',
            name='publisher',
            field=models.TextField(blank=True, null=True, verbose_name='Publisher'),
        ),
        migrations.AlterField(
            model_name='batchrow',
            name='publisher_viaf',
            field=models.TextField(blank=True, help_text='This value is invalid. Please enter a numeric VIAF identifier.', null=True, verbose_name='Publisher VIAF'),
        ),
        migrations.AlterField(
            model_name='batchrow',
            name='writtenwork_author',
            field=models.TextField(blank=True, null=True, verbose_name='Literary Work Author'),
        ),
        migrations.AlterField(
            model_name='batchrow',
            name='writtenwork_author_birth_date',
            field=models.TextField(blank=True, help_text="This value is invalid. See <a target='_blank' href='https://github.com/ccnmtl/footprints/wiki/Batch-Import-Format'>date formats</a> for rules.", null=True, verbose_name='Literary Work Author Birth Date'),
        ),
        migrations.AlterField(
            model_name='batchrow',
            name='writtenwork_author_death_date',
            field=models.TextField(blank=True, help_text="This value is invalid. See <a target='_blank' href='https://github.com/ccnmtl/footprints/wiki/Batch-Import-Format'>date formats</a> for rules.", null=True, verbose_name='Literary Work Author Death Date'),
        ),
        migrations.AlterField(
            model_name='batchrow',
            name='writtenwork_author_viaf',
            field=models.TextField(blank=True, help_text='This value is invalid. Please enter a numeric VIAF identifier.', null=True, verbose_name='Literary Work Author VIAF'),
        ),
        migrations.AlterField(
            model_name='batchrow',
            name='writtenwork_title',
            field=models.TextField(blank=True, null=True, verbose_name='Literary Work'),
        ),
    ]
