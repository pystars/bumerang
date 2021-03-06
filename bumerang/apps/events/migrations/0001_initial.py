# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Event'
        db.create_table(u'events_event', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('parent', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='contest_set', null=True, on_delete=models.SET_NULL, to=orm['events.Event'])),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(related_name='owned_events', to=orm['accounts.CustomUser'])),
            ('type', self.gf('django.db.models.fields.IntegerField')()),
            ('is_approved', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('publish_winners', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('logo', self.gf('django.db.models.fields.files.ImageField')(max_length=100, null=True, blank=True)),
            ('min_logo', self.gf('django.db.models.fields.files.ImageField')(max_length=100, null=True, blank=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('opened', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('start_date', self.gf('django.db.models.fields.DateField')()),
            ('end_date', self.gf('django.db.models.fields.DateField')()),
            ('requesting_till', self.gf('django.db.models.fields.DateField')()),
            ('hold_place', self.gf('django.db.models.fields.TextField')()),
            ('description', self.gf('django.db.models.fields.TextField')()),
            ('participant_conditions', self.gf('django.db.models.fields.TextField')()),
            ('contacts_raw_text', self.gf('django.db.models.fields.TextField')()),
            ('rules_document', self.gf('django.db.models.fields.files.FileField')(max_length=255, null=True, blank=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
        ))
        db.send_create_signal(u'events', ['Event'])

        # Adding model 'Juror'
        db.create_table(u'events_juror', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('event', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['events.Event'])),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['accounts.CustomUser'])),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75)),
            ('info_second_name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('info_name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('info_middle_name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('description', self.gf('django.db.models.fields.TextField')()),
            ('min_avatar', self.gf('django.db.models.fields.files.ImageField')(max_length=100, null=True)),
        ))
        db.send_create_signal(u'events', ['Juror'])

        # Adding unique constraint on 'Juror', fields ['event', 'user']
        db.create_unique(u'events_juror', ['event_id', 'user_id'])

        # Adding model 'GeneralRule'
        db.create_table(u'events_generalrule', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('event', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['events.Event'])),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('description', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal(u'events', ['GeneralRule'])

        # Adding model 'NewsPost'
        db.create_table(u'events_newspost', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('event', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['events.Event'])),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('description', self.gf('django.db.models.fields.TextField')()),
            ('creation_date', self.gf('django.db.models.fields.DateField')(default=datetime.datetime.now)),
        ))
        db.send_create_signal(u'events', ['NewsPost'])

        # Adding model 'Nomination'
        db.create_table(u'events_nomination', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('event', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['events.Event'])),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('age_from', self.gf('django.db.models.fields.PositiveSmallIntegerField')(null=True, blank=True)),
            ('age_to', self.gf('django.db.models.fields.PositiveSmallIntegerField')(null=True, blank=True)),
            ('sort_order', self.gf('django.db.models.fields.PositiveSmallIntegerField')()),
        ))
        db.send_create_signal(u'events', ['Nomination'])

        # Adding model 'Participant'
        db.create_table(u'events_participant', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['accounts.CustomUser'])),
            ('event', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['events.Event'])),
            ('index_number', self.gf('django.db.models.fields.IntegerField')()),
            ('is_accepted', self.gf('django.db.models.fields.BooleanField')(default=False, db_index=True)),
        ))
        db.send_create_signal(u'events', ['Participant'])

        # Adding unique constraint on 'Participant', fields ['owner', 'event']
        db.create_unique(u'events_participant', ['owner_id', 'event_id'])

        # Adding unique constraint on 'Participant', fields ['event', 'index_number']
        db.create_unique(u'events_participant', ['event_id', 'index_number'])

        # Adding model 'ParticipantVideo'
        db.create_table(u'events_participantvideo', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('participant', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['events.Participant'])),
            ('nomination', self.gf('django.db.models.fields.related.ForeignKey')(related_name='user_selected_participantvideo_set', to=orm['events.Nomination'])),
            ('age', self.gf('django.db.models.fields.PositiveSmallIntegerField')()),
            ('video', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['video.Video'], on_delete=models.PROTECT)),
            ('is_accepted', self.gf('django.db.models.fields.BooleanField')(default=False, db_index=True)),
        ))
        db.send_create_signal(u'events', ['ParticipantVideo'])

        # Adding unique constraint on 'ParticipantVideo', fields ['participant', 'video']
        db.create_unique(u'events_participantvideo', ['participant_id', 'video_id'])

        # Adding model 'VideoNomination'
        db.create_table(u'events_videonomination', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('participant_video', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['events.ParticipantVideo'])),
            ('nomination', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['events.Nomination'])),
            ('result', self.gf('django.db.models.fields.PositiveSmallIntegerField')(db_index=True, null=True, blank=True)),
        ))
        db.send_create_signal(u'events', ['VideoNomination'])

        # Adding model 'ParticipantVideoScore'
        db.create_table(u'events_participantvideoscore', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['accounts.CustomUser'])),
            ('participant_video', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['events.ParticipantVideo'])),
            ('score', self.gf('django.db.models.fields.SmallIntegerField')()),
        ))
        db.send_create_signal(u'events', ['ParticipantVideoScore'])


    def backwards(self, orm):
        # Removing unique constraint on 'ParticipantVideo', fields ['participant', 'video']
        db.delete_unique(u'events_participantvideo', ['participant_id', 'video_id'])

        # Removing unique constraint on 'Participant', fields ['event', 'index_number']
        db.delete_unique(u'events_participant', ['event_id', 'index_number'])

        # Removing unique constraint on 'Participant', fields ['owner', 'event']
        db.delete_unique(u'events_participant', ['owner_id', 'event_id'])

        # Removing unique constraint on 'Juror', fields ['event', 'user']
        db.delete_unique(u'events_juror', ['event_id', 'user_id'])

        # Deleting model 'Event'
        db.delete_table(u'events_event')

        # Deleting model 'Juror'
        db.delete_table(u'events_juror')

        # Deleting model 'GeneralRule'
        db.delete_table(u'events_generalrule')

        # Deleting model 'NewsPost'
        db.delete_table(u'events_newspost')

        # Deleting model 'Nomination'
        db.delete_table(u'events_nomination')

        # Deleting model 'Participant'
        db.delete_table(u'events_participant')

        # Deleting model 'ParticipantVideo'
        db.delete_table(u'events_participantvideo')

        # Deleting model 'VideoNomination'
        db.delete_table(u'events_videonomination')

        # Deleting model 'ParticipantVideoScore'
        db.delete_table(u'events_participantvideoscore')


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
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
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
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'}),
            'views_count': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'work_company': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'work_type': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'})
        },
        u'albums.videoalbum': {
            'Meta': {'object_name': 'VideoAlbum'},
            'cover': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['video.Video']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['accounts.CustomUser']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100'})
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
        },
        u'events.event': {
            'Meta': {'ordering': "('start_date', 'end_date')", 'object_name': 'Event'},
            'contacts_raw_text': ('django.db.models.fields.TextField', [], {}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'end_date': ('django.db.models.fields.DateField', [], {}),
            'hold_place': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_approved': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'jurors': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'juror_events'", 'symmetrical': 'False', 'through': u"orm['events.Juror']", 'to': u"orm['accounts.CustomUser']"}),
            'logo': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'min_logo': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'opened': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'owned_events'", 'to': u"orm['accounts.CustomUser']"}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'contest_set'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['events.Event']"}),
            'participant_conditions': ('django.db.models.fields.TextField', [], {}),
            'publish_winners': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'requesting_till': ('django.db.models.fields.DateField', [], {}),
            'rules_document': ('django.db.models.fields.files.FileField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'start_date': ('django.db.models.fields.DateField', [], {}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'type': ('django.db.models.fields.IntegerField', [], {})
        },
        u'events.generalrule': {
            'Meta': {'object_name': 'GeneralRule'},
            'description': ('django.db.models.fields.TextField', [], {}),
            'event': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['events.Event']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'events.juror': {
            'Meta': {'unique_together': "(('event', 'user'),)", 'object_name': 'Juror'},
            'description': ('django.db.models.fields.TextField', [], {}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'event': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['events.Event']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'info_middle_name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'info_name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'info_second_name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'min_avatar': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['accounts.CustomUser']"})
        },
        u'events.newspost': {
            'Meta': {'ordering': "('creation_date',)", 'object_name': 'NewsPost'},
            'creation_date': ('django.db.models.fields.DateField', [], {'default': 'datetime.datetime.now'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'event': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['events.Event']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'events.nomination': {
            'Meta': {'ordering': "('sort_order',)", 'object_name': 'Nomination'},
            'age_from': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'age_to': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'event': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['events.Event']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'sort_order': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'events.participant': {
            'Meta': {'unique_together': "(('owner', 'event'), ('event', 'index_number'))", 'object_name': 'Participant'},
            'event': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['events.Event']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'index_number': ('django.db.models.fields.IntegerField', [], {}),
            'is_accepted': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['accounts.CustomUser']"}),
            'videos': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['video.Video']", 'through': u"orm['events.ParticipantVideo']", 'symmetrical': 'False'})
        },
        u'events.participantvideo': {
            'Meta': {'unique_together': "(('participant', 'video'),)", 'object_name': 'ParticipantVideo'},
            'age': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_accepted': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'nomination': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'user_selected_participantvideo_set'", 'to': u"orm['events.Nomination']"}),
            'nominations': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['events.Nomination']", 'through': u"orm['events.VideoNomination']", 'symmetrical': 'False'}),
            'participant': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['events.Participant']"}),
            'video': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['video.Video']", 'on_delete': 'models.PROTECT'})
        },
        u'events.participantvideoscore': {
            'Meta': {'object_name': 'ParticipantVideoScore'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['accounts.CustomUser']"}),
            'participant_video': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['events.ParticipantVideo']"}),
            'score': ('django.db.models.fields.SmallIntegerField', [], {})
        },
        u'events.videonomination': {
            'Meta': {'object_name': 'VideoNomination'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nomination': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['events.Nomination']"}),
            'participant_video': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['events.ParticipantVideo']"}),
            'result': ('django.db.models.fields.PositiveSmallIntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'})
        },
        u'video.video': {
            'Meta': {'ordering': "('-id',)", 'object_name': 'Video'},
            'access': ('django.db.models.fields.IntegerField', [], {'default': '1', 'null': 'True', 'blank': 'True'}),
            'agency': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'album': ('django.db.models.fields.related.ForeignKey', [], {'max_length': '255', 'to': u"orm['albums.VideoAlbum']", 'null': 'True', 'blank': 'True'}),
            'authors': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['video.VideoCategory']", 'null': 'True', 'blank': 'True'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'country': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'duration': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'festivals': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'genre': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['video.VideoGenre']", 'null': 'True', 'blank': 'True'}),
            'hq_file': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_in_broadcast_lists': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'manager': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'original_file': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['accounts.CustomUser']"}),
            'published_in_archive': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'rating_score': ('django.db.models.fields.IntegerField', [], {'default': '0', 'blank': 'True'}),
            'rating_votes': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '12', 'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'teachers': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'views_count': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'year': ('django.db.models.fields.IntegerField', [], {'default': '2012', 'null': 'True', 'blank': 'True'})
        },
        u'video.videocategory': {
            'Meta': {'ordering': "('sort_order', 'title')", 'object_name': 'VideoCategory'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50'}),
            'sort_order': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'video.videogenre': {
            'Meta': {'ordering': "('sort_order', 'title')", 'object_name': 'VideoGenre'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50'}),
            'sort_order': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        }
    }

    complete_apps = ['events']