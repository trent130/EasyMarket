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
    list_display = ('user', 'student_id', 'university', 'two_factor_enabled', 'created_at')
    list_filter = ('two_factor_enabled', 'university', 'created_at')
    search_fields = ['user__first_name', 'user__last_name', 'user__email', 'student_id', 'university']
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Student Information', {
            'fields': ('user', 'student_id', 'university', 'bio', 'phone_number', 'date_of_birth')
        }),
        ('Two-Factor Authentication', {
            'fields': ('two_factor_enabled', 'two_factor_verified', 'two_factor_secret', 'backup_codes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')

try:
    admin.site.unregister(Student)
except NotRegistered:
    pass
admin.site.register(Student, StudentAdmin)

admin.site.register(UserProfile)

