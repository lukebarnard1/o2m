# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('basic_server', '0017_auto_20150523_1344'),
    ]

    operations = [
        migrations.AlterField(
            model_name='content',
            name='file_path',
            field=models.FilePathField(path=b'/Users/lukebarnard/o2m/content', recursive=True),
        ),
    ]
