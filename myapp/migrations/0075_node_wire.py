# Generated by Django 5.1.1 on 2024-10-11 11:53

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0074_remove_node_canvas_remove_wire_canvas_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Node',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('ip_address', models.GenericIPAddressField()),
                ('tooltip_description', models.TextField()),
                ('vulnerability', models.TextField()),
                ('position_x', models.FloatField()),
                ('position_y', models.FloatField()),
                ('icon', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Wire',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('end_node', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='end_node', to='myapp.node')),
                ('start_node', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='start_node', to='myapp.node')),
            ],
        ),
    ]