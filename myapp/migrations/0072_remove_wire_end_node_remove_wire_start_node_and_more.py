# Generated by Django 5.1.1 on 2024-10-11 11:46

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0071_node_wire_canvas'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='wire',
            name='end_node',
        ),
        migrations.RemoveField(
            model_name='wire',
            name='start_node',
        ),
        migrations.DeleteModel(
            name='Canvas',
        ),
        migrations.DeleteModel(
            name='Node',
        ),
        migrations.DeleteModel(
            name='Wire',
        ),
    ]