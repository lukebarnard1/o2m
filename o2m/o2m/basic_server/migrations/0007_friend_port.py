# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('basic_server', '0006_auto_20150209_0947'),
    ]

    operations = [
        migrations.AddField(
            model_name='friend',
            name='port',
            field=models.IntegerField(default=8000),
            preserve_default=True,
        ),
    ]
