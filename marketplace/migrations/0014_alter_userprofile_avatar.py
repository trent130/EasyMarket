# Generated by Django 5.0.2 on 2024-06-19 13:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('marketplace', '0013_customuser'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='avatar',
            field=models.ImageField(default='avatars/default.jpeg', upload_to='avatars/'),
        ),
    ]