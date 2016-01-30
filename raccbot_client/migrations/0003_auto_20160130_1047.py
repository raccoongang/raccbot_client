# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('raccbot_client', '0002_auto_20160130_1043'),
    ]

    operations = [
        migrations.AlterField(
            model_name='teleramreg',
            name='tel_name',
            field=models.CharField(unique=True, max_length=50, blank=True),
        ),
        migrations.AlterField(
            model_name='teleramreg',
            name='verified',
            field=models.BooleanField(default=False, db_index=True),
        ),
    ]
