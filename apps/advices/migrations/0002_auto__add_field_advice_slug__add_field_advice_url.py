# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding field 'Advice.slug'
        db.add_column('advices_advice', 'slug', self.gf('django.db.models.fields.SlugField')(default=datetime.date(2011, 12, 7), max_length=50, db_index=True), keep_default=False)

        # Adding field 'Advice.url'
        db.add_column('advices_advice', 'url', self.gf('django.db.models.fields.CharField')(default=datetime.date(2011, 12, 7), max_length=1024), keep_default=False)


    def backwards(self, orm):
        
        # Deleting field 'Advice.slug'
        db.delete_column('advices_advice', 'slug')

        # Deleting field 'Advice.url'
        db.delete_column('advices_advice', 'url')


    models = {
        'advices.advice': {
            'Meta': {'object_name': 'Advice'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'}),
            'parent': ('mptt.fields.TreeForeignKey', [], {'blank': 'True', 'related_name': "'children'", 'null': 'True', 'to': "orm['advices.Advice']"}),
            'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'db_index': 'True'}),
            'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '1024'})
        }
    }

    complete_apps = ['advices']
