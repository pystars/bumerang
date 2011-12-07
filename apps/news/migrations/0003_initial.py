# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'NewsCategory'
        db.create_table('news_newscategory', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('news', ['NewsCategory'])

        # Adding model 'NewsItem'
        db.create_table('news_newsitem', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('category', self.gf('django.db.models.fields.related.ForeignKey')(related_name='category', to=orm['news.NewsCategory'])),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=50, db_index=True)),
            ('preview_text', self.gf('django.db.models.fields.TextField')()),
            ('text', self.gf('django.db.models.fields.TextField')()),
            ('creation_date', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2011, 12, 6, 20, 54, 4, 732438))),
        ))
        db.send_create_signal('news', ['NewsItem'])


    def backwards(self, orm):
        
        # Deleting model 'NewsCategory'
        db.delete_table('news_newscategory')

        # Deleting model 'NewsItem'
        db.delete_table('news_newsitem')


    models = {
        'news.newscategory': {
            'Meta': {'object_name': 'NewsCategory'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'news.newsitem': {
            'Meta': {'object_name': 'NewsItem'},
            'category': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'category'", 'to': "orm['news.NewsCategory']"}),
            'creation_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2011, 12, 6, 20, 54, 4, 732438)'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'preview_text': ('django.db.models.fields.TextField', [], {}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'db_index': 'True'}),
            'text': ('django.db.models.fields.TextField', [], {}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        }
    }

    complete_apps = ['news']
