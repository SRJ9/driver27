# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-10-02 16:27
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('driver27', '0014_auto_20161002_1606'),
    ]

    operations = [
        migrations.AddField(
            model_name='race',
            name='alter_punctuation',
            field=models.CharField(blank=True, choices=[('double', 'Double'), ('half', 'Half')], default=None, max_length=6, null=True),
        ),
        migrations.AddField(
            model_name='season',
            name='punctuation',
            field=models.CharField(default=None, max_length=20, null=True),
        ),
    ]