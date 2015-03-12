# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('basic_server', '0008_auto_20150226_1001'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='content',
            name='creation_time',
        ),
        migrations.AddField(
            model_name='link',
            name='creation_time',
            field=models.DateTimeField(default=datetime.datetime.now, auto_now_add=True),
            preserve_default=True,
        ),
    ]
