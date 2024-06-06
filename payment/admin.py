from django.contrib import admin
from .models import Transaction

# Register your models here.
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'timestamp','status')
    list_filter = ('status', 'timestamp')
    search_fields = ['user__username', 'status']

admin.site.register(Transaction, TransactionAdmin)


