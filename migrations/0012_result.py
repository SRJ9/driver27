# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-10-01 14:23
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('driver27', '0011_auto_20161001_1405'),
    ]

    operations = [
        migrations.CreateModel(
            name='Result',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('qualifying', models.IntegerField(blank=True, default=None, null=True)),
                ('finish', models.IntegerField(blank=True, default=None, null=True)),
                ('comment', models.CharField(blank=True, default=None, max_length=250, null=True)),
                ('contender', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='results', to='driver27.DriverCompetitionTeam')),
                ('race', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='results', to='driver27.Race')),
            ],
        ),
    ]
