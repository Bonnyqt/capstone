# Generated by Django 5.1.1 on 2024-09-12 14:39

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0016_remove_customuser_new_field_customuser_is_verified'),
    ]

    operations = [
        migrations.DeleteModel(
            name='CustomUser',
        ),
    ]