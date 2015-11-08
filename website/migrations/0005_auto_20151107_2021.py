# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0004_auto_20151107_1952'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='payment_service_email',
            field=models.EmailField(default=b'', max_length=255, null=True, blank=True),
            preserve_default=True,
        ),
    ]
