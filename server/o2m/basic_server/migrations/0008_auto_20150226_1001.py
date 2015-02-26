# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import mptt.fields


class Migration(migrations.Migration):

    dependencies = [
        ('basic_server', '0007_friend_port'),
    ]

    operations = [
        migrations.DeleteModel(
            name='LinkEdge',
        ),
        migrations.AddField(
            model_name='link',
            name='level',
            field=models.PositiveIntegerField(default=0, editable=False, db_index=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='link',
            name='lft',
            field=models.PositiveIntegerField(default=2, editable=False, db_index=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='link',
            name='parent',
            field=mptt.fields.TreeForeignKey(related_name='children', blank=True, to='basic_server.Link', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='link',
            name='rght',
            field=models.PositiveIntegerField(default=2, editable=False, db_index=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='link',
            name='tree_id',
            field=models.PositiveIntegerField(default=2, editable=False, db_index=True),
            preserve_default=False,
        ),
    ]
