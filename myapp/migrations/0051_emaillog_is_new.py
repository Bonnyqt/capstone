# Generated by Django 5.1.1 on 2024-09-19 19:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0050_emaillog'),
    ]

    operations = [
        migrations.AddField(
            model_name='emaillog',
            name='is_new',
            field=models.BooleanField(default=True),
        ),
    ]
