# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0005_auto_20151107_2021'),
    ]

    operations = [
        migrations.AddField(
            model_name='issue',
            name='views',
            field=models.IntegerField(default=1),
        ),
    ]
