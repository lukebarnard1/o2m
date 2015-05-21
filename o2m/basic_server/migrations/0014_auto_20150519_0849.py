# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('basic_server', '0013_auto_20150426_1649'),
    ]

    operations = [
        migrations.RenameField(
            model_name='notification',
            old_name='objid',
            new_name='obj_id',
        ),
        migrations.RenameField(
            model_name='notificationtype',
            old_name='objtype',
            new_name='obj_type',
        ),
        migrations.RemoveField(
            model_name='notification',
            name='friend',
        ),
        migrations.RemoveField(
            model_name='notification',
            name='link',
        ),
        migrations.AddField(
            model_name='notification',
            name='obj_creator',
            field=models.ForeignKey(related_name='creator', default=1, to='basic_server.Friend'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='notification',
            name='obj_server',
            field=models.ForeignKey(related_name='server', default=1, to='basic_server.Friend'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='friend',
            name='address',
            field=models.GenericIPAddressField(),
        ),
        migrations.AlterField(
            model_name='link',
            name='creation_time',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='notificationtype',
            name='title',
            field=models.CharField(max_length=64),
        ),
    ]
