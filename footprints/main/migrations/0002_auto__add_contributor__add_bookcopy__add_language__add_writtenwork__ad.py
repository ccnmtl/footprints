# flake8: noqa
# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Contributor'
        db.create_table(u'main_contributor', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('person', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.Person'])),
            ('role', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.Role'])),
            ('alternate_name', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.Name'], null=True, blank=True)),
        ))
        db.send_create_signal(u'main', ['Contributor'])

        # Adding model 'BookCopy'
        db.create_table(u'main_bookcopy', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('imprint', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.Imprint'])),
            ('notes', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('modified_at', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal(u'main', ['BookCopy'])

        # Adding M2M table for field digital_object on 'BookCopy'
        m2m_table_name = db.shorten_name(u'main_bookcopy_digital_object')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('bookcopy', models.ForeignKey(orm[u'main.bookcopy'], null=False)),
            ('digitalobject', models.ForeignKey(orm[u'main.digitalobject'], null=False))
        ))
        db.create_unique(m2m_table_name, ['bookcopy_id', 'digitalobject_id'])

        # Adding model 'Language'
        db.create_table(u'main_language', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=100)),
        ))
        db.send_create_signal(u'main', ['Language'])

        # Adding model 'WrittenWork'
        db.create_table(u'main_writtenwork', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('standardized_title', self.gf('django.db.models.fields.TextField')()),
            ('notes', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('modified_at', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal(u'main', ['WrittenWork'])

        # Adding M2M table for field author on 'WrittenWork'
        m2m_table_name = db.shorten_name(u'main_writtenwork_author')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('writtenwork', models.ForeignKey(orm[u'main.writtenwork'], null=False)),
            ('contributor', models.ForeignKey(orm[u'main.contributor'], null=False))
        ))
        db.create_unique(m2m_table_name, ['writtenwork_id', 'contributor_id'])

        # Adding model 'DigitalFormat'
        db.create_table(u'main_digitalformat', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=100)),
        ))
        db.send_create_signal(u'main', ['DigitalFormat'])

        # Adding model 'ExtendedDateFormat'
        db.create_table(u'main_extendeddateformat', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('edtf_format', self.gf('django.db.models.fields.CharField')(max_length=256)),
        ))
        db.send_create_signal(u'main', ['ExtendedDateFormat'])

        # Adding model 'Person'
        db.create_table(u'main_person', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.Name'])),
            ('date_of_birth', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.ExtendedDateFormat'], null=True, blank=True)),
            ('standardized_identifier', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.StandardizedIdentification'], null=True, blank=True)),
            ('notes', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('modified_at', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal(u'main', ['Person'])

        # Adding M2M table for field digital_object on 'Person'
        m2m_table_name = db.shorten_name(u'main_person_digital_object')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('person', models.ForeignKey(orm[u'main.person'], null=False)),
            ('digitalobject', models.ForeignKey(orm[u'main.digitalobject'], null=False))
        ))
        db.create_unique(m2m_table_name, ['person_id', 'digitalobject_id'])

        # Adding model 'Collection'
        db.create_table(u'main_collection', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=512)),
            ('notes', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('modified_at', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal(u'main', ['Collection'])

        # Adding M2M table for field contributor on 'Collection'
        m2m_table_name = db.shorten_name(u'main_collection_contributor')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('collection', models.ForeignKey(orm[u'main.collection'], null=False)),
            ('contributor', models.ForeignKey(orm[u'main.contributor'], null=False))
        ))
        db.create_unique(m2m_table_name, ['collection_id', 'contributor_id'])

        # Adding model 'Place'
        db.create_table(u'main_place', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('continent', self.gf('django.db.models.fields.CharField')(max_length=2)),
            ('region', self.gf('django.db.models.fields.CharField')(max_length=256, null=True, blank=True)),
            ('country', self.gf('django.db.models.fields.CharField')(max_length=256, null=True, blank=True)),
            ('city', self.gf('django.db.models.fields.CharField')(max_length=256, null=True, blank=True)),
            ('notes', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('modified_at', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal(u'main', ['Place'])

        # Adding M2M table for field digital_object on 'Place'
        m2m_table_name = db.shorten_name(u'main_place_digital_object')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('place', models.ForeignKey(orm[u'main.place'], null=False)),
            ('digitalobject', models.ForeignKey(orm[u'main.digitalobject'], null=False))
        ))
        db.create_unique(m2m_table_name, ['place_id', 'digitalobject_id'])

        # Adding model 'DigitalObject'
        db.create_table(u'main_digitalobject', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=500)),
            ('digital_format', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.DigitalFormat'])),
            ('file', self.gf('django.db.models.fields.files.FileField')(max_length=100)),
            ('source_url', self.gf('django.db.models.fields.URLField')(max_length=200, null=True, blank=True)),
            ('notes', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('modified_at', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal(u'main', ['DigitalObject'])

        # Adding model 'Imprint'
        db.create_table(u'main_imprint', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('work', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.WrittenWork'])),
            ('title', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('language', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.Language'], null=True, blank=True)),
            ('publication_date', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.ExtendedDateFormat'], null=True, blank=True)),
            ('place', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.Place'], null=True, blank=True)),
            ('notes', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('modified_at', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal(u'main', ['Imprint'])

        # Adding M2M table for field contributor on 'Imprint'
        m2m_table_name = db.shorten_name(u'main_imprint_contributor')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('imprint', models.ForeignKey(orm[u'main.imprint'], null=False)),
            ('contributor', models.ForeignKey(orm[u'main.contributor'], null=False))
        ))
        db.create_unique(m2m_table_name, ['imprint_id', 'contributor_id'])

        # Adding M2M table for field standardized_identifier on 'Imprint'
        m2m_table_name = db.shorten_name(u'main_imprint_standardized_identifier')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('imprint', models.ForeignKey(orm[u'main.imprint'], null=False)),
            ('standardizedidentification', models.ForeignKey(orm[u'main.standardizedidentification'], null=False))
        ))
        db.create_unique(m2m_table_name, ['imprint_id', 'standardizedidentification_id'])

        # Adding M2M table for field digital_object on 'Imprint'
        m2m_table_name = db.shorten_name(u'main_imprint_digital_object')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('imprint', models.ForeignKey(orm[u'main.imprint'], null=False)),
            ('digitalobject', models.ForeignKey(orm[u'main.digitalobject'], null=False))
        ))
        db.create_unique(m2m_table_name, ['imprint_id', 'digitalobject_id'])

        # Adding model 'Role'
        db.create_table(u'main_role', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=256)),
        ))
        db.send_create_signal(u'main', ['Role'])

        # Adding model 'Name'
        db.create_table(u'main_name', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('last_name', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('first_name', self.gf('django.db.models.fields.CharField')(max_length=256, null=True, blank=True)),
            ('middle_name', self.gf('django.db.models.fields.CharField')(max_length=256, null=True, blank=True)),
            ('suffix', self.gf('django.db.models.fields.CharField')(max_length=256, null=True, blank=True)),
        ))
        db.send_create_signal(u'main', ['Name'])

        # Adding model 'Footprint'
        db.create_table(u'main_footprint', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('book_copy', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.BookCopy'])),
            ('medium', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('provenance', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('title', self.gf('django.db.models.fields.TextField')()),
            ('language', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.Language'], null=True, blank=True)),
            ('place', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.Place'], null=True, blank=True)),
            ('recorded_date', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.ExtendedDateFormat'], null=True, blank=True)),
            ('call_number', self.gf('django.db.models.fields.CharField')(max_length=256, null=True, blank=True)),
            ('collection', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.Collection'], null=True, blank=True)),
            ('notes', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('modified_at', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal(u'main', ['Footprint'])

        # Adding M2M table for field digital_object on 'Footprint'
        m2m_table_name = db.shorten_name(u'main_footprint_digital_object')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('footprint', models.ForeignKey(orm[u'main.footprint'], null=False)),
            ('digitalobject', models.ForeignKey(orm[u'main.digitalobject'], null=False))
        ))
        db.create_unique(m2m_table_name, ['footprint_id', 'digitalobject_id'])

        # Adding model 'StandardizedIdentification'
        db.create_table(u'main_standardizedidentification', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('identifier', self.gf('django.db.models.fields.CharField')(max_length=512)),
            ('identifier_type', self.gf('django.db.models.fields.CharField')(max_length=5)),
            ('identifier_text', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('modified_at', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal(u'main', ['StandardizedIdentification'])


    def backwards(self, orm):
        # Deleting model 'Contributor'
        db.delete_table(u'main_contributor')

        # Deleting model 'BookCopy'
        db.delete_table(u'main_bookcopy')

        # Removing M2M table for field digital_object on 'BookCopy'
        db.delete_table(db.shorten_name(u'main_bookcopy_digital_object'))

        # Deleting model 'Language'
        db.delete_table(u'main_language')

        # Deleting model 'WrittenWork'
        db.delete_table(u'main_writtenwork')

        # Removing M2M table for field author on 'WrittenWork'
        db.delete_table(db.shorten_name(u'main_writtenwork_author'))

        # Deleting model 'DigitalFormat'
        db.delete_table(u'main_digitalformat')

        # Deleting model 'ExtendedDateFormat'
        db.delete_table(u'main_extendeddateformat')

        # Deleting model 'Person'
        db.delete_table(u'main_person')

        # Removing M2M table for field digital_object on 'Person'
        db.delete_table(db.shorten_name(u'main_person_digital_object'))

        # Deleting model 'Collection'
        db.delete_table(u'main_collection')

        # Removing M2M table for field contributor on 'Collection'
        db.delete_table(db.shorten_name(u'main_collection_contributor'))

        # Deleting model 'Place'
        db.delete_table(u'main_place')

        # Removing M2M table for field digital_object on 'Place'
        db.delete_table(db.shorten_name(u'main_place_digital_object'))

        # Deleting model 'DigitalObject'
        db.delete_table(u'main_digitalobject')

        # Deleting model 'Imprint'
        db.delete_table(u'main_imprint')

        # Removing M2M table for field contributor on 'Imprint'
        db.delete_table(db.shorten_name(u'main_imprint_contributor'))

        # Removing M2M table for field standardized_identifier on 'Imprint'
        db.delete_table(db.shorten_name(u'main_imprint_standardized_identifier'))

        # Removing M2M table for field digital_object on 'Imprint'
        db.delete_table(db.shorten_name(u'main_imprint_digital_object'))

        # Deleting model 'Role'
        db.delete_table(u'main_role')

        # Deleting model 'Name'
        db.delete_table(u'main_name')

        # Deleting model 'Footprint'
        db.delete_table(u'main_footprint')

        # Removing M2M table for field digital_object on 'Footprint'
        db.delete_table(db.shorten_name(u'main_footprint_digital_object'))

        # Deleting model 'StandardizedIdentification'
        db.delete_table(u'main_standardizedidentification')


    models = {
        u'main.bookcopy': {
            'Meta': {'ordering': "['imprint']", 'object_name': 'BookCopy'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'digital_object': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['main.DigitalObject']", 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'imprint': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['main.Imprint']"}),
            'modified_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'notes': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'})
        },
        u'main.collection': {
            'Meta': {'ordering': "['name']", 'object_name': 'Collection'},
            'contributor': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['main.Contributor']", 'null': 'True', 'blank': 'True'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '512'}),
            'notes': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'})
        },
        u'main.contributor': {
            'Meta': {'object_name': 'Contributor'},
            'alternate_name': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['main.Name']", 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'person': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['main.Person']"}),
            'role': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['main.Role']"})
        },
        u'main.digitalformat': {
            'Meta': {'ordering': "['name']", 'object_name': 'DigitalFormat'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'})
        },
        u'main.digitalobject': {
            'Meta': {'ordering': "['name']", 'object_name': 'DigitalObject'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'digital_format': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['main.DigitalFormat']"}),
            'file': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'notes': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'source_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'})
        },
        u'main.extendeddateformat': {
            'Meta': {'object_name': 'ExtendedDateFormat'},
            'edtf_format': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'main.footprint': {
            'Meta': {'ordering': "['title']", 'object_name': 'Footprint'},
            'book_copy': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['main.BookCopy']"}),
            'call_number': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'collection': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['main.Collection']", 'null': 'True', 'blank': 'True'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'digital_object': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['main.DigitalObject']", 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['main.Language']", 'null': 'True', 'blank': 'True'}),
            'medium': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'modified_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'notes': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'place': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['main.Place']", 'null': 'True', 'blank': 'True'}),
            'provenance': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'recorded_date': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['main.ExtendedDateFormat']", 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.TextField', [], {})
        },
        u'main.imprint': {
            'Meta': {'ordering': "['work']", 'object_name': 'Imprint'},
            'contributor': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['main.Contributor']", 'null': 'True', 'blank': 'True'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'digital_object': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['main.DigitalObject']", 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['main.Language']", 'null': 'True', 'blank': 'True'}),
            'modified_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'notes': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'place': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['main.Place']", 'null': 'True', 'blank': 'True'}),
            'publication_date': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['main.ExtendedDateFormat']", 'null': 'True', 'blank': 'True'}),
            'standardized_identifier': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['main.StandardizedIdentification']", 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'work': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['main.WrittenWork']"})
        },
        u'main.language': {
            'Meta': {'ordering': "['name']", 'object_name': 'Language'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'})
        },
        u'main.name': {
            'Meta': {'ordering': "['last_name']", 'object_name': 'Name'},
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'middle_name': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'suffix': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'})
        },
        u'main.person': {
            'Meta': {'ordering': "['name']", 'object_name': 'Person'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_of_birth': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['main.ExtendedDateFormat']", 'null': 'True', 'blank': 'True'}),
            'digital_object': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['main.DigitalObject']", 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['main.Name']"}),
            'notes': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'standardized_identifier': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['main.StandardizedIdentification']", 'null': 'True', 'blank': 'True'})
        },
        u'main.place': {
            'Meta': {'ordering': "['continent', 'region', 'country', 'city']", 'object_name': 'Place'},
            'city': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'continent': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            'country': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'digital_object': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['main.DigitalObject']", 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'notes': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'region': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'})
        },
        u'main.role': {
            'Meta': {'ordering': "['name']", 'object_name': 'Role'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '256'})
        },
        u'main.standardizedidentification': {
            'Meta': {'object_name': 'StandardizedIdentification'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'identifier': ('django.db.models.fields.CharField', [], {'max_length': '512'}),
            'identifier_text': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'identifier_type': ('django.db.models.fields.CharField', [], {'max_length': '5'}),
            'modified_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        u'main.writtenwork': {
            'Meta': {'ordering': "['standardized_title']", 'object_name': 'WrittenWork'},
            'author': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['main.Contributor']", 'null': 'True', 'blank': 'True'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'notes': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'standardized_title': ('django.db.models.fields.TextField', [], {})
        }
    }

    complete_apps = ['main']