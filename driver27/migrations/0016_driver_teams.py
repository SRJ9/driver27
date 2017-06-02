# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-06-02 14:50
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('driver27', '0015_auto_20170602_1447'),
    ]

    operations = [
        migrations.AddField(
            model_name='driver',
            name='teams',
            field=models.ManyToManyField(related_name='drivers', through='driver27.Seat', to='driver27.Team', verbose_name='teams'),
        ),
    ]
