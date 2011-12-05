# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Deleting model 'NewsItem'
        db.delete_table('news_newsitem')


    def backwards(self, orm):
        
        # Adding model 'NewsItem'
        db.create_table('news_newsitem', (
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('text', self.gf('django.db.models.fields.TextField')()),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('creation_date', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2011, 11, 30, 18, 58, 15, 563073))),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=50, db_index=True)),
        ))
        db.send_create_signal('news', ['NewsItem'])


    models = {
        
    }

    complete_apps = ['news']
