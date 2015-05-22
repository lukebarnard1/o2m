# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('basic_server', '0014_auto_20150519_0849'),
    ]

    operations = [
        migrations.AlterField(
            model_name='content',
            name='file_path',
            field=models.FilePathField(path=b'/Users/lukebarnard/Documents/Development/PersonalProjects/o2m/development_1/o2m/social', recursive=True),
        ),
    ]
