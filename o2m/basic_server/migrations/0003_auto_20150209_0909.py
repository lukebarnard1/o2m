# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('basic_server', '0002_auto_20150209_0856'),
    ]

    operations = [
        migrations.AlterField(
            model_name='content',
            name='file_path',
            field=models.FilePathField(path=b'/', recursive=True),
            preserve_default=True,
        ),
    ]
