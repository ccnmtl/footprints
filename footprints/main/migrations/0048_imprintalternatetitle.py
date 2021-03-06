# Generated by Django 2.2.15 on 2020-08-30 13:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0047_language_marc_code'),
    ]

    operations = [
        migrations.CreateModel(
            name='ImprintAlternateTitle',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('alternate_title', models.TextField()),
                ('language', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='main.Language')),
                ('standardized_identifier', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.StandardizedIdentification')),
            ],
            options={
                'unique_together': {('alternate_title', 'standardized_identifier')},
            },
        ),
    ]
