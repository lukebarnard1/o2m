# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('basic_server', '0005_auto_20150209_0925'),
    ]

    operations = [
        migrations.AlterField(
            model_name='content',
            name='file_path',
            field=models.FilePathField(path=b'/Users/lukebarnard/Documents/Development/PersonalProjects/o2m/server/o2m/social', recursive=True),
            preserve_default=True,
        ),
    ]
