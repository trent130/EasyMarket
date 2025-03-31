from django.contrib import admin
from .models import UserProfile, Student, CustomUser
from django.contrib.admin.exceptions import NotRegistered

# Register your models here.
@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'username', 'user_type')
    list_filter = ('user_type', 'date_joined', )
    search_fields = ('first_name', 'last_name', 'username')
    ordering = ('-date_joined',)

class StudentAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email')
    search_fields = ['first_name', 'last_name', 'email']

try:
    admin.site.unregister(Student)
except NotRegistered:
    pass
admin.site.register(Student, StudentAdmin)

admin.site.register(UserProfile)

