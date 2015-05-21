# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('basic_server', '0012_notificationtype_link'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='notificationtype',
            name='link',
        ),
        migrations.AddField(
            model_name='notification',
            name='link',
            field=models.CharField(default='', max_length=64),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='notificationtype',
            name='title',
            field=models.CharField(max_length=100),
            preserve_default=True,
        ),
    ]
