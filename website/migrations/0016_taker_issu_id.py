# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0015_solution_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='taker',
            name='issu_id',
            field=models.CharField(max_length=255, null=True, blank=True),
        ),
    ]
