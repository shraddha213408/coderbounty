# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0003_auto_20151021_1455'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='delta',
            name='user',
        ),
        migrations.DeleteModel(
            name='Delta',
        ),
        migrations.AlterUniqueTogether(
            name='userservice',
            unique_together=None,
        ),
        migrations.RemoveField(
            model_name='userservice',
            name='service',
        ),
        migrations.RemoveField(
            model_name='userservice',
            name='user',
        ),
        migrations.DeleteModel(
            name='UserService',
        ),
        migrations.RemoveField(
            model_name='watcher',
            name='issue',
        ),
        migrations.RemoveField(
            model_name='watcher',
            name='user',
        ),
        migrations.DeleteModel(
            name='Watcher',
        ),
        migrations.RemoveField(
            model_name='xp',
            name='user',
        ),
        migrations.DeleteModel(
            name='XP',
        ),
        migrations.AlterModelOptions(
            name='issue',
            options={'ordering': ['-created']},
        ),
        migrations.RemoveField(
            model_name='userprofile',
            name='coins',
        ),
        migrations.AlterField(
            model_name='bounty',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='issue',
            name='language',
            field=models.CharField(blank=True, max_length=255, choices=[(b'Java', b'Java'), (b'C', b'C'), (b'C++', b'C++'), (b'PHP', b'PHP'), (b'VB', b'VB'), (b'Python', b'Python'), (b'C#', b'C#'), (b'JavaScript', b'JavaScript'), (b'Perl', b'Perl'), (b'Ruby', b'Ruby'), (b'HTML', b'HTML')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='issue',
            name='notified_user',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='issue',
            name='number',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='issue',
            name='service',
            field=models.ForeignKey(related_name='+', default=None, to='website.Service'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='user',
            field=models.OneToOneField(related_name='userprofile', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
    ]