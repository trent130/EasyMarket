from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_student_two_factor_enabled_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='reset_token',
            field=models.CharField(blank=True, default='', max_length=100),
        ),
        migrations.AddField(
            model_name='customuser',
            name='reset_token_expiry',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
