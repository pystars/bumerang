# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Adding field 'EncodeJob.object_id'
        db.add_column(u'converting_encodejob', 'object_id',
                      self.gf('django.db.models.fields.PositiveIntegerField')(default='1'),
                      keep_default=False)
        for obj in orm['EncodeJob'].objects.all():
            obj.object_id = obj.object_pk
            obj.save()

        # Deleting field 'EncodeJob.object_pk'
        db.delete_column(u'converting_encodejob', 'object_pk')

    def backwards(self, orm):
        # Adding field 'EncodeJob.object_pk'
        db.add_column(u'converting_encodejob', 'object_pk',
                      self.gf('django.db.models.fields.PositiveIntegerField')(default=1),
                      keep_default=False)
        for obj in orm['EncodeJob'].objects.all():
            obj.object_pk = obj.object_id
            obj.save()

        # Deleting field 'EncodeJob.object_id'
        db.delete_column(u'converting_encodejob', 'object_id')


    models = {
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'converting.convertoptions': {
            'Meta': {'object_name': 'ConvertOptions'},
            'abitrate': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'frame_rate': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'height': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'preset': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'quality': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'sample_rate': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'vbitrate': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'width': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'x264opts': ('django.db.models.fields.CharField', [], {'default': "'ref=2:bframes=2:subq=6:mixed-refs=0:weightb=0:8x8dct=0:trellis=0'", 'max_length': '400', 'null': 'True', 'blank': 'True'})
        },
        u'converting.encodejob': {
            'Meta': {'object_name': 'EncodeJob'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'job_id': ('django.db.models.fields.CharField', [], {'max_length': '100', 'primary_key': 'True', 'db_index': 'True'}),
            'last_modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'message': ('django.db.models.fields.TextField', [], {}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'state': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0', 'db_index': 'True'})
        }
    }

    complete_apps = ['converting']