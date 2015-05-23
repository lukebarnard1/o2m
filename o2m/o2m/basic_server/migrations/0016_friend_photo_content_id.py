# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('basic_server', '0015_auto_20150522_1544'),
    ]

    operations = [
        migrations.AddField(
            model_name='friend',
            name='photo_content_id',
            field=models.IntegerField(default=None),
        ),
    ]
