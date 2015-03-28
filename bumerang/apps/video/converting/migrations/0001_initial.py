# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'ConvertOptions'
        db.create_table(u'converting_convertoptions', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('sample_rate', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('abitrate', self.gf('django.db.models.fields.PositiveIntegerField')(null=True, blank=True)),
            ('preset', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('vbitrate', self.gf('django.db.models.fields.PositiveIntegerField')(null=True, blank=True)),
            ('frame_rate', self.gf('django.db.models.fields.CharField')(max_length=10, null=True, blank=True)),
            ('width', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('height', self.gf('django.db.models.fields.PositiveIntegerField')(null=True, blank=True)),
            ('quality', self.gf('django.db.models.fields.PositiveIntegerField')(null=True, blank=True)),
            ('x264opts', self.gf('django.db.models.fields.CharField')(default='ref=2:bframes=2:subq=6:mixed-refs=0:weightb=0:8x8dct=0:trellis=0', max_length=400, null=True, blank=True)),
        ))
        db.send_create_signal(u'converting', ['ConvertOptions'])


    def backwards(self, orm):
        # Deleting model 'ConvertOptions'
        db.delete_table(u'converting_convertoptions')


    models = {
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
        }
    }

    complete_apps = ['converting']