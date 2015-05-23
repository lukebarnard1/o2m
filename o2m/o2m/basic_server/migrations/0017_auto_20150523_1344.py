# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('basic_server', '0016_friend_photo_content_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='friend',
            name='photo_content_id',
            field=models.IntegerField(default=1),
        ),
    ]
