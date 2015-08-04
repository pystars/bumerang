# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'NewsCategory.site'
        db.add_column(u'news_newscategory', 'site',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=1, to=orm['sites.Site']),
                      keep_default=False)

        # Adding unique constraint on 'NewsCategory', fields ['slug', 'site']
        db.create_unique(u'news_newscategory', ['slug', 'site_id'])


    def backwards(self, orm):
        # Removing unique constraint on 'NewsCategory', fields ['slug', 'site']
        db.delete_unique(u'news_newscategory', ['slug', 'site_id'])

        # Deleting field 'NewsCategory.site'
        db.delete_column(u'news_newscategory', 'site_id')


    models = {
        u'news.newscategory': {
            'Meta': {'ordering': "('sort_order', 'id')", 'unique_together': "(('slug', 'site'),)", 'object_name': 'NewsCategory'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'default': '1', 'to': u"orm['sites.Site']"}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50'}),
            'sort_order': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'news.newsitem': {
            'Meta': {'ordering': "('-creation_date',)", 'object_name': 'NewsItem'},
            'category': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'news'", 'to': u"orm['news.NewsCategory']"}),
            'creation_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'preview_text': ('django.db.models.fields.TextField', [], {}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50'}),
            'text': ('django.db.models.fields.TextField', [], {}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'sites.site': {
            'Meta': {'ordering': "(u'domain',)", 'object_name': 'Site', 'db_table': "u'django_site'"},
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        }
    }

    complete_apps = ['news']