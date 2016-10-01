# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-09-29 21:53
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('driver27', '0009_auto_20160929_2125'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='grandprix',
            options={'verbose_name_plural': 'grands prix'},
        ),
        migrations.AlterField(
            model_name='teamseasonrel',
            name='sponsor_name',
            field=models.CharField(blank=True, default=None, max_length=75, null=True),
        ),
        migrations.AlterUniqueTogether(
            name='teamseasonrel',
            unique_together=set([('season', 'team')]),
        ),
    ]