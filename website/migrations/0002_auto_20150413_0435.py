# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='coin',
            name='user',
        ),
        migrations.DeleteModel(
            name='Coin',
        ),
        migrations.AlterField(
            model_name='issue',
            name='notified_user',
            field=models.BooleanField(default=None),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='watcher',
            name='bounty',
            field=models.BooleanField(default=None),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='watcher',
            name='status',
            field=models.BooleanField(default=None),
            preserve_default=True,
        ),
    ]
