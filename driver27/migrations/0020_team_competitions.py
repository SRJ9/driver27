# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-06-02 15:33
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('driver27', '0019_remove_team_competitions'),
    ]

    operations = [
        migrations.AddField(
            model_name='team',
            name='competitions',
            field=models.ManyToManyField(related_name='teams', through='driver27.CompetitionTeam', to='driver27.Competition', verbose_name='competitions'),
        ),
    ]