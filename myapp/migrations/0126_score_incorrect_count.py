# Generated by Django 5.1.1 on 2024-11-18 17:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0125_score'),
    ]

    operations = [
        migrations.AddField(
            model_name='score',
            name='incorrect_count',
            field=models.IntegerField(default=0),
        ),
    ]
