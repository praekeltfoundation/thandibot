# -*- coding: utf-8 -*-
# Generated by Django 1.9.13 on 2017-06-23 16:23
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0006_record_record_identifier'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subscription',
            name='friday',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='subscription',
            name='monday',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='subscription',
            name='thursday',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='subscription',
            name='tuesday',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='subscription',
            name='wednesday',
            field=models.BooleanField(default=False),
        ),
    ]
