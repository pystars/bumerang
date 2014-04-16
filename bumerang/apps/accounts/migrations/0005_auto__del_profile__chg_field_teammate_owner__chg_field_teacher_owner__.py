# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting model 'Profile'
        db.delete_table(u'accounts_profile')


        # Changing field 'Teammate.owner'
        db.alter_column(u'accounts_teammate', 'owner_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['accounts.CustomUser']))

        # Changing field 'Teacher.owner'
        db.alter_column(u'accounts_teacher', 'owner_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['accounts.CustomUser']))

        # Changing field 'Faculty.owner'
        db.alter_column(u'accounts_faculty', 'owner_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['accounts.CustomUser']))

        # Changing field 'Service.owner'
        db.alter_column(u'accounts_service', 'owner_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['accounts.CustomUser']))

    def backwards(self, orm):
        # Adding model 'Profile'
        db.create_table(u'accounts_profile', (
            ('info_address', self.gf('django.db.models.fields.TextField')()),
            (u'user_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['auth.User'], unique=True, primary_key=True)),
            ('work_company', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('views_count', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('friends_count', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('fav_books', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('work_type', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('info_organization', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('info_name', self.gf('django.db.models.fields.CharField')(max_length=100, null=True)),
            ('birthday', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('fav_music', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('schools', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('avatar_coords', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('nickname', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('fav_movies', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('info_postal_address', self.gf('django.db.models.fields.TextField')()),
            ('city', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('info_email', self.gf('django.db.models.fields.EmailField')(max_length=75)),
            ('activation_code_expire', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('info_second_name', self.gf('django.db.models.fields.CharField')(max_length=100, null=True)),
            ('country', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('region', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('info_phone', self.gf('django.db.models.fields.CharField')(max_length=40)),
            ('info_middle_name', self.gf('django.db.models.fields.CharField')(max_length=100, null=True)),
            ('info_mobile_phone', self.gf('django.db.models.fields.CharField')(max_length=12, null=True, blank=True)),
            ('info_organization_form', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('courses', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('min_avatar', self.gf('django.db.models.fields.files.ImageField')(max_length=100, null=True, blank=True)),
            ('avatar', self.gf('django.db.models.fields.files.ImageField')(max_length=100, null=True, blank=True)),
            ('gender', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('hobby', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('activation_code', self.gf('django.db.models.fields.CharField')(max_length=32, null=True, blank=True)),
            ('type', self.gf('django.db.models.fields.IntegerField')(default=1, db_index=True)),
        ))
        db.send_create_signal(u'accounts', ['Profile'])


        # Changing field 'Teammate.owner'
        db.alter_column(u'accounts_teammate', 'owner_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User']))

        # Changing field 'Teacher.owner'
        db.alter_column(u'accounts_teacher', 'owner_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User']))

        # Changing field 'Faculty.owner'
        db.alter_column(u'accounts_faculty', 'owner_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User']))

        # Changing field 'Service.owner'
        db.alter_column(u'accounts_service', 'owner_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User']))

    models = {
        u'accounts.customuser': {
            'Meta': {'object_name': 'CustomUser'},
            'activation_code': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'}),
            'activation_code_expire': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'avatar': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'avatar_coords': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'birthday': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'country': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'courses': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'fav_books': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'fav_movies': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'fav_music': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'friends_count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'gender': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'hobby': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'info_address': ('django.db.models.fields.TextField', [], {}),
            'info_email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'info_middle_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True'}),
            'info_mobile_phone': ('django.db.models.fields.CharField', [], {'max_length': '12', 'null': 'True', 'blank': 'True'}),
            'info_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True'}),
            'info_organization': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'info_organization_form': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'info_phone': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'info_postal_address': ('django.db.models.fields.TextField', [], {}),
            'info_second_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'min_avatar': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'nickname': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'region': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'schools': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'type': ('django.db.models.fields.IntegerField', [], {'default': '1', 'db_index': 'True'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'}),
            'views_count': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'work_company': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'work_type': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'})
        },
        u'accounts.faculty': {
            'Meta': {'object_name': 'Faculty'},
            'description': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['accounts.CustomUser']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'accounts.service': {
            'Meta': {'object_name': 'Service'},
            'description': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['accounts.CustomUser']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'accounts.teacher': {
            'Meta': {'object_name': 'Teacher'},
            'description': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['accounts.CustomUser']"}),
            'photo': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            'photo_min': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'blank': 'True'})
        },
        u'accounts.teammate': {
            'Meta': {'object_name': 'Teammate'},
            'description': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['accounts.CustomUser']"}),
            'photo': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            'photo_min': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'blank': 'True'})
        },
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
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['accounts']