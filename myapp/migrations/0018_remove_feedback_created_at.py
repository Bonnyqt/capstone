# Generated by Django 5.1.1 on 2024-09-12 18:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0017_delete_customuser'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='feedback',
            name='created_at',
        ),
    ]