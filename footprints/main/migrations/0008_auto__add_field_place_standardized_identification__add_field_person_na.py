# flake8: noqa
# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Place.standardized_identification'
        db.add_column(u'main_place', 'standardized_identification',
                      self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.StandardizedIdentification'], null=True, blank=True),
                      keep_default=False)

        # Adding field 'Person.name'
        db.add_column(u'main_person', 'name',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=1, related_name='person_name', to=orm['main.Name']),
                      keep_default=False)

        # Adding field 'Person.alternate_spellings'
        db.add_column(u'main_person', 'alternate_spellings',
                      self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='person_alternate_spellings', null=True, to=orm['main.Name']),
                      keep_default=False)

        # Adding field 'Person.birth_date'
        db.add_column(u'main_person', 'birth_date',
                      self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='birth_date', null=True, to=orm['main.ExtendedDateFormat']),
                      keep_default=False)

        # Adding field 'Person.death_date'
        db.add_column(u'main_person', 'death_date',
                      self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='death_date', null=True, to=orm['main.ExtendedDateFormat']),
                      keep_default=False)

        # Adding field 'Imprint.date_of_publication'
        db.add_column(u'main_imprint', 'date_of_publication',
                      self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.ExtendedDateFormat'], null=True, blank=True),
                      keep_default=False)

        # Adding field 'Footprint.document_type'
        db.add_column(u'main_footprint', 'document_type',
                      self.gf('django.db.models.fields.CharField')(max_length=256, null=True, blank=True),
                      keep_default=False)

        # Adding field 'Footprint.associated_date'
        db.add_column(u'main_footprint', 'associated_date',
                      self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.ExtendedDateFormat'], null=True, blank=True),
                      keep_default=False)

        # Deleting field 'Name.last_name'
        db.delete_column(u'main_name', 'last_name')

        # Deleting field 'Name.first_name'
        db.delete_column(u'main_name', 'first_name')

        # Deleting field 'Name.middle_name'
        db.delete_column(u'main_name', 'middle_name')

        # Deleting field 'Name.suffix'
        db.delete_column(u'main_name', 'suffix')

        # Adding field 'Name.name'
        db.add_column(u'main_name', 'name',
                      self.gf('django.db.models.fields.TextField')(default=datetime.datetime(2014, 11, 24, 0, 0)),
                      keep_default=False)

        # Adding field 'Name.sort_by'
        db.add_column(u'main_name', 'sort_by',
                      self.gf('django.db.models.fields.TextField')(default=datetime.datetime(2014, 11, 24, 0, 0)),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Place.standardized_identification'
        db.delete_column(u'main_place', 'standardized_identification_id')

        # Deleting field 'Person.name'
        db.delete_column(u'main_person', 'name_id')

        # Deleting field 'Person.alternate_spellings'
        db.delete_column(u'main_person', 'alternate_spellings_id')

        # Deleting field 'Person.birth_date'
        db.delete_column(u'main_person', 'birth_date_id')

        # Deleting field 'Person.death_date'
        db.delete_column(u'main_person', 'death_date_id')

        # Deleting field 'Imprint.date_of_publication'
        db.delete_column(u'main_imprint', 'date_of_publication_id')

        # Deleting field 'Footprint.document_type'
        db.delete_column(u'main_footprint', 'document_type')

        # Deleting field 'Footprint.associated_date'
        db.delete_column(u'main_footprint', 'associated_date_id')

        # Adding field 'Name.last_name'
        db.add_column(u'main_name', 'last_name',
                      self.gf('django.db.models.fields.CharField')(default=datetime.datetime(2014, 11, 24, 0, 0), max_length=256),
                      keep_default=False)

        # Adding field 'Name.first_name'
        db.add_column(u'main_name', 'first_name',
                      self.gf('django.db.models.fields.CharField')(max_length=256, null=True, blank=True),
                      keep_default=False)

        # Adding field 'Name.middle_name'
        db.add_column(u'main_name', 'middle_name',
                      self.gf('django.db.models.fields.CharField')(max_length=256, null=True, blank=True),
                      keep_default=False)

        # Adding field 'Name.suffix'
        db.add_column(u'main_name', 'suffix',
                      self.gf('django.db.models.fields.CharField')(max_length=256, null=True, blank=True),
                      keep_default=False)

        # Deleting field 'Name.name'
        db.delete_column(u'main_name', 'name')

        # Deleting field 'Name.sort_by'
        db.delete_column(u'main_name', 'sort_by')


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'main.actor': {
            'Meta': {'object_name': 'Actor'},
            'alternate_first_name': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'alternate_last_name': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'alternate_middle_name': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'alternate_suffix': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'created_by': ('audit_log.models.fields.CreatingUserField', [], {'related_name': "'actor_created_by'", 'to': u"orm['auth.User']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_modified_by': ('audit_log.models.fields.LastUserField', [], {'related_name': "'actor_last_modified_by'", 'to': u"orm['auth.User']"}),
            'modified_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'person': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['main.Person']"}),
            'role': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['main.Role']"})
        },
        u'main.bookcopy': {
            'Meta': {'ordering': "['imprint']", 'object_name': 'BookCopy'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'created_by': ('audit_log.models.fields.CreatingUserField', [], {'related_name': "'bookcopy_created_by'", 'to': u"orm['auth.User']"}),
            'digital_object': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['main.DigitalObject']", 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'imprint': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['main.Imprint']"}),
            'last_modified_by': ('audit_log.models.fields.LastUserField', [], {'related_name': "'bookcopy_last_modified_by'", 'to': u"orm['auth.User']"}),
            'modified_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'notes': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'})
        },
        u'main.collection': {
            'Meta': {'ordering': "['name']", 'object_name': 'Collection'},
            'actor': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['main.Actor']", 'null': 'True', 'blank': 'True'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'created_by': ('audit_log.models.fields.CreatingUserField', [], {'related_name': "'collection_created_by'", 'to': u"orm['auth.User']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_modified_by': ('audit_log.models.fields.LastUserField', [], {'related_name': "'collection_last_modified_by'", 'to': u"orm['auth.User']"}),
            'modified_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '512'}),
            'notes': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'})
        },
        u'main.digitalformat': {
            'Meta': {'ordering': "['name']", 'object_name': 'DigitalFormat'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'})
        },
        u'main.digitalobject': {
            'Meta': {'ordering': "['name']", 'object_name': 'DigitalObject'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'created_by': ('audit_log.models.fields.CreatingUserField', [], {'related_name': "'digitalobject_created_by'", 'to': u"orm['auth.User']"}),
            'digital_format': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['main.DigitalFormat']"}),
            'file': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_modified_by': ('audit_log.models.fields.LastUserField', [], {'related_name': "'digitalobject_last_modified_by'", 'to': u"orm['auth.User']"}),
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
            'actor': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['main.Actor']", 'null': 'True', 'blank': 'True'}),
            'associated_date': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['main.ExtendedDateFormat']", 'null': 'True', 'blank': 'True'}),
            'book_copy': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['main.BookCopy']"}),
            'call_number': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'collection': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['main.Collection']", 'null': 'True', 'blank': 'True'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'created_by': ('audit_log.models.fields.CreatingUserField', [], {'related_name': "'footprint_created_by'", 'to': u"orm['auth.User']"}),
            'digital_object': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['main.DigitalObject']", 'null': 'True', 'blank': 'True'}),
            'document_type': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['main.Language']", 'null': 'True', 'blank': 'True'}),
            'last_modified_by': ('audit_log.models.fields.LastUserField', [], {'related_name': "'footprint_last_modified_by'", 'to': u"orm['auth.User']"}),
            'medium': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'modified_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'notes': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'place': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['main.Place']", 'null': 'True', 'blank': 'True'}),
            'provenance': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'recorded_date': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.TextField', [], {})
        },
        u'main.imprint': {
            'Meta': {'ordering': "['work']", 'object_name': 'Imprint'},
            'actor': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['main.Actor']", 'null': 'True', 'blank': 'True'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'created_by': ('audit_log.models.fields.CreatingUserField', [], {'related_name': "'imprint_created_by'", 'to': u"orm['auth.User']"}),
            'date_of_publication': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['main.ExtendedDateFormat']", 'null': 'True', 'blank': 'True'}),
            'digital_object': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['main.DigitalObject']", 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['main.Language']", 'null': 'True', 'blank': 'True'}),
            'last_modified_by': ('audit_log.models.fields.LastUserField', [], {'related_name': "'imprint_last_modified_by'", 'to': u"orm['auth.User']"}),
            'modified_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'notes': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'place': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['main.Place']", 'null': 'True', 'blank': 'True'}),
            'publication_date': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
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
            'Meta': {'ordering': "['sort_by', 'name']", 'object_name': 'Name'},
            'created_by': ('audit_log.models.fields.CreatingUserField', [], {'related_name': "'name_created_by'", 'to': u"orm['auth.User']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_modified_by': ('audit_log.models.fields.LastUserField', [], {'related_name': "'name_last_modified_by'", 'to': u"orm['auth.User']"}),
            'name': ('django.db.models.fields.TextField', [], {}),
            'sort_by': ('django.db.models.fields.TextField', [], {})
        },
        u'main.person': {
            'Meta': {'ordering': "['last_name', 'first_name']", 'object_name': 'Person'},
            'alternate_spellings': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'person_alternate_spellings'", 'null': 'True', 'to': u"orm['main.Name']"}),
            'birth_date': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'birth_date'", 'null': 'True', 'to': u"orm['main.ExtendedDateFormat']"}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'created_by': ('audit_log.models.fields.CreatingUserField', [], {'related_name': "'person_created_by'", 'to': u"orm['auth.User']"}),
            'date_of_birth': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'date_of_death': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'death_date': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'death_date'", 'null': 'True', 'to': u"orm['main.ExtendedDateFormat']"}),
            'digital_object': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['main.DigitalObject']", 'null': 'True', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_modified_by': ('audit_log.models.fields.LastUserField', [], {'related_name': "'person_last_modified_by'", 'to': u"orm['auth.User']"}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'middle_name': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'modified_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'person_name'", 'to': u"orm['main.Name']"}),
            'notes': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'standardized_identifier': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['main.StandardizedIdentification']", 'null': 'True', 'blank': 'True'}),
            'suffix': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'})
        },
        u'main.place': {
            'Meta': {'ordering': "['continent', 'region', 'country', 'city']", 'object_name': 'Place'},
            'city': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'continent': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            'country': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'created_by': ('audit_log.models.fields.CreatingUserField', [], {'related_name': "'place_created_by'", 'to': u"orm['auth.User']"}),
            'digital_object': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['main.DigitalObject']", 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_modified_by': ('audit_log.models.fields.LastUserField', [], {'related_name': "'place_last_modified_by'", 'to': u"orm['auth.User']"}),
            'modified_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'notes': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'position': ('geoposition.fields.GeopositionField', [], {'max_length': '42', 'null': 'True', 'blank': 'True'}),
            'region': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'standardized_identification': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['main.StandardizedIdentification']", 'null': 'True', 'blank': 'True'})
        },
        u'main.role': {
            'Meta': {'ordering': "['name']", 'object_name': 'Role'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '256'})
        },
        u'main.standardizedidentification': {
            'Meta': {'object_name': 'StandardizedIdentification'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'created_by': ('audit_log.models.fields.CreatingUserField', [], {'related_name': "'standardizedidentification_created_by'", 'to': u"orm['auth.User']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'identifier': ('django.db.models.fields.CharField', [], {'max_length': '512'}),
            'identifier_text': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'identifier_type': ('django.db.models.fields.CharField', [], {'max_length': '5'}),
            'last_modified_by': ('audit_log.models.fields.LastUserField', [], {'related_name': "'standardizedidentification_last_modified_by'", 'to': u"orm['auth.User']"}),
            'modified_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        u'main.writtenwork': {
            'Meta': {'ordering': "['standardized_title']", 'object_name': 'WrittenWork'},
            'actor': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['main.Actor']", 'null': 'True', 'blank': 'True'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'created_by': ('audit_log.models.fields.CreatingUserField', [], {'related_name': "'writtenwork_created_by'", 'to': u"orm['auth.User']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_modified_by': ('audit_log.models.fields.LastUserField', [], {'related_name': "'writtenwork_last_modified_by'", 'to': u"orm['auth.User']"}),
            'modified_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'notes': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'standardized_title': ('django.db.models.fields.TextField', [], {})
        }
    }

    complete_apps = ['main']