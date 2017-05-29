# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-05-29 22:32
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('driver27', '0011_remove_contender_teams'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='seat',
            options={'ordering': ['driver__last_name', 'team'], 'verbose_name': 'Seat', 'verbose_name_plural': 'Seats'},
        ),
        migrations.AlterUniqueTogether(
            name='seat',
            unique_together=set([('team', 'driver')]),
        ),
    ]
