from django.db import migrations
from django.conf import settings

def associate_users(apps, schema_editor):
    Student = apps.get_model('marketplace', 'Student')
    User = apps.get_model('auth', 'User')
    for student in Student.objects.all():
        user = User.objects.create(username=student.email, email=student.email)
        student.user = user
        student.save()

class Migration(migrations.Migration):

    dependencies = [
        ('marketplace', '0006_student_user'), migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        
    ]

    operations = [
        migrations.RunPython(associate_users),
    ]