# Generated by Django 5.0.2 on 2024-06-19 13:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('marketplace', '0014_alter_userprofile_avatar'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='avatar',
            field=models.ImageField(default='avatars/default.png', upload_to='avatars/'),
        ),
    ]