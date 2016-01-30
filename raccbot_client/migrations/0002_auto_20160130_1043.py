# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('raccbot_client', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='teleramreg',
            old_name='telname',
            new_name='tel_name',
        ),
        migrations.RemoveField(
            model_name='teleramreg',
            name='username',
        ),
        migrations.AddField(
            model_name='teleramreg',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
    ]
