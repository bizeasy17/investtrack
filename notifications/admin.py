from django.contrib import admin
from .models import Notification

# Register your models here.
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('recipient', 'actor', 'verb', 'unread')
    list_filter = ('recipient', 'unread')


admin.site.register(Notification, NotificationAdmin)
