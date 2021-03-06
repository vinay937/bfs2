# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2018-03-03 06:52
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [("feedback", "0002_feedbackform_active")]

    operations = [
        migrations.AlterField(
            model_name="question",
            name="form",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="question",
                to="feedback.FeedbackForm",
            ),
        )
    ]
