# Generated by Django 5.1.1 on 2024-10-11 12:37

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0077_networkvisualization'),
    ]

    operations = [
        migrations.CreateModel(
            name='Node',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('icon_class', models.CharField(max_length=100)),
                ('ip_address', models.CharField(blank=True, max_length=100, null=True)),
                ('tooltip', models.TextField(blank=True, null=True)),
                ('vulnerability', models.CharField(blank=True, max_length=100, null=True)),
                ('title', models.CharField(blank=True, max_length=100, null=True)),
                ('position_x', models.IntegerField(default=0)),
                ('position_y', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Wire',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('end_node', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='end', to='myapp.node')),
                ('start_node', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='start', to='myapp.node')),
            ],
        ),
        migrations.DeleteModel(
            name='NetworkVisualization',
        ),
    ]
