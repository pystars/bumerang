# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'NewsItem'
        db.create_table('news_newsitem', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=50, db_index=True)),
            ('text', self.gf('django.db.models.fields.TextField')()),
            ('creation_date', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2011, 11, 30, 18, 58, 15, 563073))),
        ))
        db.send_create_signal('news', ['NewsItem'])


    def backwards(self, orm):
        
        # Deleting model 'NewsItem'
        db.delete_table('news_newsitem')


    models = {
        'news.newsitem': {
            'Meta': {'object_name': 'NewsItem'},
            'creation_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2011, 11, 30, 18, 58, 15, 563073)'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'db_index': 'True'}),
            'text': ('django.db.models.fields.TextField', [], {}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        }
    }

    complete_apps = ['news']
