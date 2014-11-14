# flake8: noqa
# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'Contributor.alternate_name'
        db.delete_column(u'main_contributor', 'alternate_name_id')

        # Adding field 'Contributor.alternate_last_name'
        db.add_column(u'main_contributor', 'alternate_last_name',
                      self.gf('django.db.models.fields.CharField')(max_length=256, null=True, blank=True),
                      keep_default=False)

        # Adding field 'Contributor.alternate_first_name'
        db.add_column(u'main_contributor', 'alternate_first_name',
                      self.gf('django.db.models.fields.CharField')(max_length=256, null=True, blank=True),
                      keep_default=False)

        # Adding field 'Contributor.alternate_middle_name'
        db.add_column(u'main_contributor', 'alternate_middle_name',
                      self.gf('django.db.models.fields.CharField')(max_length=256, null=True, blank=True),
                      keep_default=False)

        # Adding field 'Contributor.alternate_suffix'
        db.add_column(u'main_contributor', 'alternate_suffix',
                      self.gf('django.db.models.fields.CharField')(max_length=256, null=True, blank=True),
                      keep_default=False)

        # Deleting field 'Person.name'
        db.delete_column(u'main_person', 'name_id')

        # Adding field 'Person.last_name'
        db.add_column(u'main_person', 'last_name',
                      self.gf('django.db.models.fields.CharField')(default='example', max_length=256),
                      keep_default=False)

        # Adding field 'Person.first_name'
        db.add_column(u'main_person', 'first_name',
                      self.gf('django.db.models.fields.CharField')(max_length=256, null=True, blank=True),
                      keep_default=False)

        # Adding field 'Person.middle_name'
        db.add_column(u'main_person', 'middle_name',
                      self.gf('django.db.models.fields.CharField')(max_length=256, null=True, blank=True),
                      keep_default=False)

        # Adding field 'Person.suffix'
        db.add_column(u'main_person', 'suffix',
                      self.gf('django.db.models.fields.CharField')(max_length=256, null=True, blank=True),
                      keep_default=False)

        # Adding field 'Person.date_of_death'
        db.add_column(u'main_person', 'date_of_death',
                      self.gf('django.db.models.fields.CharField')(max_length=256, null=True, blank=True),
                      keep_default=False)


        # Renaming column for 'Person.date_of_birth' to match new field type.
        db.rename_column(u'main_person', 'date_of_birth_id', 'date_of_birth')
        # Changing field 'Person.date_of_birth'
        db.alter_column(u'main_person', 'date_of_birth', self.gf('django.db.models.fields.CharField')(max_length=256, null=True))
        # Removing index on 'Person', fields ['date_of_birth']
        db.delete_index(u'main_person', ['date_of_birth_id'])


        # Renaming column for 'Imprint.publication_date' to match new field type.
        db.rename_column(u'main_imprint', 'publication_date_id', 'publication_date')
        # Changing field 'Imprint.publication_date'
        db.alter_column(u'main_imprint', 'publication_date', self.gf('django.db.models.fields.CharField')(max_length=256, null=True))
        # Removing index on 'Imprint', fields ['publication_date']
        db.delete_index(u'main_imprint', ['publication_date_id'])


        # Renaming column for 'Footprint.recorded_date' to match new field type.
        db.rename_column(u'main_footprint', 'recorded_date_id', 'recorded_date')
        # Changing field 'Footprint.recorded_date'
        db.alter_column(u'main_footprint', 'recorded_date', self.gf('django.db.models.fields.CharField')(max_length=256, null=True))
        # Removing index on 'Footprint', fields ['recorded_date']
        db.delete_index(u'main_footprint', ['recorded_date_id'])


    def backwards(self, orm):
        # Adding index on 'Footprint', fields ['recorded_date']
        db.create_index(u'main_footprint', ['recorded_date_id'])

        # Adding index on 'Imprint', fields ['publication_date']
        db.create_index(u'main_imprint', ['publication_date_id'])

        # Adding index on 'Person', fields ['date_of_birth']
        db.create_index(u'main_person', ['date_of_birth_id'])

        # Adding field 'Contributor.alternate_name'
        db.add_column(u'main_contributor', 'alternate_name',
                      self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.Name'], null=True, blank=True),
                      keep_default=False)

        # Deleting field 'Contributor.alternate_last_name'
        db.delete_column(u'main_contributor', 'alternate_last_name')

        # Deleting field 'Contributor.alternate_first_name'
        db.delete_column(u'main_contributor', 'alternate_first_name')

        # Deleting field 'Contributor.alternate_middle_name'
        db.delete_column(u'main_contributor', 'alternate_middle_name')

        # Deleting field 'Contributor.alternate_suffix'
        db.delete_column(u'main_contributor', 'alternate_suffix')

        # Adding field 'Person.name'
        db.add_column(u'main_person', 'name',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=1, to=orm['main.Name']),
                      keep_default=False)

        # Deleting field 'Person.last_name'
        db.delete_column(u'main_person', 'last_name')

        # Deleting field 'Person.first_name'
        db.delete_column(u'main_person', 'first_name')

        # Deleting field 'Person.middle_name'
        db.delete_column(u'main_person', 'middle_name')

        # Deleting field 'Person.suffix'
        db.delete_column(u'main_person', 'suffix')

        # Deleting field 'Person.date_of_death'
        db.delete_column(u'main_person', 'date_of_death')


        # Renaming column for 'Person.date_of_birth' to match new field type.
        db.rename_column(u'main_person', 'date_of_birth', 'date_of_birth_id')
        # Changing field 'Person.date_of_birth'
        db.alter_column(u'main_person', 'date_of_birth_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.ExtendedDateFormat'], null=True))

        # Renaming column for 'Imprint.publication_date' to match new field type.
        db.rename_column(u'main_imprint', 'publication_date', 'publication_date_id')
        # Changing field 'Imprint.publication_date'
        db.alter_column(u'main_imprint', 'publication_date_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.ExtendedDateFormat'], null=True))

        # Renaming column for 'Footprint.recorded_date' to match new field type.
        db.rename_column(u'main_footprint', 'recorded_date', 'recorded_date_id')
        # Changing field 'Footprint.recorded_date'
        db.alter_column(u'main_footprint', 'recorded_date_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.ExtendedDateFormat'], null=True))

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
            'contributor': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['main.Contributor']", 'null': 'True', 'blank': 'True'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'created_by': ('audit_log.models.fields.CreatingUserField', [], {'related_name': "'collection_created_by'", 'to': u"orm['auth.User']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_modified_by': ('audit_log.models.fields.LastUserField', [], {'related_name': "'collection_last_modified_by'", 'to': u"orm['auth.User']"}),
            'modified_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '512'}),
            'notes': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'})
        },
        u'main.contributor': {
            'Meta': {'object_name': 'Contributor'},
            'alternate_first_name': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'alternate_last_name': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'alternate_middle_name': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'alternate_suffix': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'created_by': ('audit_log.models.fields.CreatingUserField', [], {'related_name': "'contributor_created_by'", 'to': u"orm['auth.User']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_modified_by': ('audit_log.models.fields.LastUserField', [], {'related_name': "'contributor_last_modified_by'", 'to': u"orm['auth.User']"}),
            'modified_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
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
            'book_copy': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['main.BookCopy']"}),
            'call_number': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'collection': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['main.Collection']", 'null': 'True', 'blank': 'True'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'created_by': ('audit_log.models.fields.CreatingUserField', [], {'related_name': "'footprint_created_by'", 'to': u"orm['auth.User']"}),
            'digital_object': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['main.DigitalObject']", 'null': 'True', 'blank': 'True'}),
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
            'contributor': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['main.Contributor']", 'null': 'True', 'blank': 'True'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'created_by': ('audit_log.models.fields.CreatingUserField', [], {'related_name': "'imprint_created_by'", 'to': u"orm['auth.User']"}),
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
            'Meta': {'ordering': "['last_name']", 'object_name': 'Name'},
            'created_by': ('audit_log.models.fields.CreatingUserField', [], {'related_name': "'name_created_by'", 'to': u"orm['auth.User']"}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_modified_by': ('audit_log.models.fields.LastUserField', [], {'related_name': "'name_last_modified_by'", 'to': u"orm['auth.User']"}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'middle_name': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'suffix': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'})
        },
        u'main.person': {
            'Meta': {'ordering': "['last_name', 'first_name']", 'object_name': 'Person'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'created_by': ('audit_log.models.fields.CreatingUserField', [], {'related_name': "'person_created_by'", 'to': u"orm['auth.User']"}),
            'date_of_birth': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'date_of_death': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'digital_object': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['main.DigitalObject']", 'null': 'True', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_modified_by': ('audit_log.models.fields.LastUserField', [], {'related_name': "'person_last_modified_by'", 'to': u"orm['auth.User']"}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'middle_name': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'modified_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
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
            'author': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['main.Contributor']", 'null': 'True', 'blank': 'True'}),
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