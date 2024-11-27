from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('marketplace', '0004_alter_review_unique_together'),
    ]

    operations = [
        migrations.AddField(
            model_name='student',
            name='two_factor_enabled',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='student',
            name='two_factor_secret',
            field=models.CharField(blank=True, max_length=32, null=True),
        ),
        migrations.AddField(
            model_name='student',
            name='two_factor_verified',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='student',
            name='backup_codes',
            field=models.JSONField(blank=True, default=list),
        ),
    ]
