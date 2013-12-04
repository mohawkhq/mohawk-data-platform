# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Application'
        db.create_table(u'data_application', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('date_created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, db_index=True, blank=True)),
            ('date_modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, db_index=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('external_id', self.gf('django.db.models.fields.CharField')(default=u'ewsmOrFZSt6ML5m0iOsa-A', max_length=255)),
            ('is_online', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal(u'data', ['Application'])

        # Adding unique constraint on 'Application', fields ['external_id']
        db.create_unique(u'data_application', ['external_id'])

        # Adding model 'File'
        db.create_table(u'data_file', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('date_created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, db_index=True, blank=True)),
            ('date_modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, db_index=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('file', self.gf('django.db.models.fields.files.FileField')(max_length=100)),
        ))
        db.send_create_signal(u'data', ['File'])

        # Adding model 'Model'
        db.create_table(u'data_model', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('date_created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, db_index=True, blank=True)),
            ('date_modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, db_index=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('external_id', self.gf('django.db.models.fields.CharField')(default=u'65R_H0wRQWqo3CnF2USqBg', max_length=255)),
            ('is_online', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal(u'data', ['Model'])

        # Adding unique constraint on 'Model', fields ['external_id']
        db.create_unique(u'data_model', ['external_id'])

        # Adding M2M table for field admin_users on 'Model'
        m2m_table_name = db.shorten_name(u'data_model_admin_users')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('model', models.ForeignKey(orm[u'data.model'], null=False)),
            ('user', models.ForeignKey(orm[u'auth.user'], null=False))
        ))
        db.create_unique(m2m_table_name, ['model_id', 'user_id'])

        # Adding M2M table for field admin_groups on 'Model'
        m2m_table_name = db.shorten_name(u'data_model_admin_groups')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('model', models.ForeignKey(orm[u'data.model'], null=False)),
            ('group', models.ForeignKey(orm[u'auth.group'], null=False))
        ))
        db.create_unique(m2m_table_name, ['model_id', 'group_id'])

        # Adding M2M table for field applications on 'Model'
        m2m_table_name = db.shorten_name(u'data_model_applications')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('model', models.ForeignKey(orm[u'data.model'], null=False)),
            ('application', models.ForeignKey(orm[u'data.application'], null=False))
        ))
        db.create_unique(m2m_table_name, ['model_id', 'application_id'])

        # Adding model 'Field'
        db.create_table(u'data_field', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('model', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['data.Model'])),
            ('type', self.gf('django.db.models.fields.CharField')(default='text', max_length=20)),
            ('type_params', self.gf('jsonfield.fields.JSONField')(default={}, blank=True)),
            ('order', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal(u'data', ['Field'])

        # Adding unique constraint on 'Field', fields ['model', 'name']
        db.create_unique(u'data_field', ['model_id', 'name'])

        # Adding model 'Instance'
        db.create_table(u'data_instance', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('date_created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, db_index=True, blank=True)),
            ('date_modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, db_index=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('external_id', self.gf('django.db.models.fields.CharField')(default=u'6socCRgbQWqKrTd9KyTwQA', max_length=255)),
            ('is_online', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('model', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['data.Model'])),
            ('data', self.gf('jsonfield.fields.JSONField')(default={})),
        ))
        db.send_create_signal(u'data', ['Instance'])

        # Adding unique constraint on 'Instance', fields ['model', 'external_id']
        db.create_unique(u'data_instance', ['model_id', 'external_id'])


    def backwards(self, orm):
        # Removing unique constraint on 'Instance', fields ['model', 'external_id']
        db.delete_unique(u'data_instance', ['model_id', 'external_id'])

        # Removing unique constraint on 'Field', fields ['model', 'name']
        db.delete_unique(u'data_field', ['model_id', 'name'])

        # Removing unique constraint on 'Model', fields ['external_id']
        db.delete_unique(u'data_model', ['external_id'])

        # Removing unique constraint on 'Application', fields ['external_id']
        db.delete_unique(u'data_application', ['external_id'])

        # Deleting model 'Application'
        db.delete_table(u'data_application')

        # Deleting model 'File'
        db.delete_table(u'data_file')

        # Deleting model 'Model'
        db.delete_table(u'data_model')

        # Removing M2M table for field admin_users on 'Model'
        db.delete_table(db.shorten_name(u'data_model_admin_users'))

        # Removing M2M table for field admin_groups on 'Model'
        db.delete_table(db.shorten_name(u'data_model_admin_groups'))

        # Removing M2M table for field applications on 'Model'
        db.delete_table(db.shorten_name(u'data_model_applications'))

        # Deleting model 'Field'
        db.delete_table(u'data_field')

        # Deleting model 'Instance'
        db.delete_table(u'data_instance')


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
        u'data.application': {
            'Meta': {'ordering': "('-date_modified',)", 'unique_together': "(('external_id',),)", 'object_name': 'Application'},
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'db_index': 'True', 'blank': 'True'}),
            'date_modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'db_index': 'True', 'blank': 'True'}),
            'external_id': ('django.db.models.fields.CharField', [], {'default': "u'tc149D0dQB6Bivm2OpVZ-Q'", 'max_length': '255'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_online': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        u'data.field': {
            'Meta': {'ordering': "('order', 'pk')", 'unique_together': "(('model', 'name'),)", 'object_name': 'Field'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['data.Model']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'order': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'type': ('django.db.models.fields.CharField', [], {'default': "'text'", 'max_length': '20'}),
            'type_params': ('jsonfield.fields.JSONField', [], {'default': '{}', 'blank': 'True'})
        },
        u'data.file': {
            'Meta': {'ordering': "('-date_modified',)", 'object_name': 'File'},
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'db_index': 'True', 'blank': 'True'}),
            'date_modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'db_index': 'True', 'blank': 'True'}),
            'file': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        u'data.instance': {
            'Meta': {'ordering': "('-date_modified',)", 'unique_together': "(('model', 'external_id'),)", 'object_name': 'Instance'},
            'data': ('jsonfield.fields.JSONField', [], {'default': '{}'}),
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'db_index': 'True', 'blank': 'True'}),
            'date_modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'db_index': 'True', 'blank': 'True'}),
            'external_id': ('django.db.models.fields.CharField', [], {'default': "u'xw6wVzFnT9ST7Uqyl3-YEw'", 'max_length': '255'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_online': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'model': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['data.Model']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        u'data.model': {
            'Meta': {'ordering': "('-date_modified',)", 'unique_together': "(('external_id',),)", 'object_name': 'Model'},
            'admin_groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'admin_users': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.User']", 'symmetrical': 'False', 'blank': 'True'}),
            'applications': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['data.Application']", 'symmetrical': 'False', 'blank': 'True'}),
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'db_index': 'True', 'blank': 'True'}),
            'date_modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'db_index': 'True', 'blank': 'True'}),
            'external_id': ('django.db.models.fields.CharField', [], {'default': "u'yt15Z2M7RLi_q3eefQppxw'", 'max_length': '255'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_online': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        }
    }

    complete_apps = ['data']