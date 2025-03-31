from django.contrib import admin
from .models import UserProfile, Student, CustomUser

# Register your models here.
class StudentAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email')
    search_fields = ['first_name', 'last_name', 'email']

try:
    admin.site.unregister(Student)
except NotRegistered:
    pass
admin.site.register(Student, StudentAdmin)

admin.site.register(UserProfile)
admin.site.register(CustomUser)