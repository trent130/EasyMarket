# Generated by Django 5.0 on 2024-12-02 12:13

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('marketplace', '0002_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='customuser',
            old_name='is_students',
            new_name='is_premium',
        ),
    ]