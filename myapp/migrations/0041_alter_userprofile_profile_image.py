# Generated by Django 5.1.1 on 2024-09-15 14:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0040_alter_userprofile_profile_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='profile_image',
            field=models.ImageField(blank=True, default='profile_images/default_QBRSs97.jpg', null=True, upload_to='profile_images/'),
        ),
    ]
