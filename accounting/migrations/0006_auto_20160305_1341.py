# -*- coding: utf-8 -*-
# Generated by Django 1.9.3 on 2016-03-05 12:41
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounting', '0005_remove_purchaseitem_price'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='purchase',
            options={'ordering': ['-date', 'account']},
        ),
        migrations.RemoveField(
            model_name='product',
            name='price',
        ),
        migrations.AddField(
            model_name='price',
            name='product',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='price_history', to='accounting.Product'),
        ),
        migrations.AlterField(
            model_name='price',
            name='date',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]