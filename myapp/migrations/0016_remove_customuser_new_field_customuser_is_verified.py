# Generated by Django 5.1.1 on 2024-09-12 14:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0015_remove_customuser_verification_customuser_new_field_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customuser',
            name='new_field',
        ),
        migrations.AddField(
            model_name='customuser',
            name='is_verified',
            field=models.BooleanField(default=False),
        ),
    ]
