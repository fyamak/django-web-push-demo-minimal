from django.contrib import admin

from .models import Notification, NotificationCategory, PushSubscription, UserNotificationPreference

admin.site.register(NotificationCategory)
admin.site.register(PushSubscription)
admin.site.register(UserNotificationPreference)
admin.site.register(Notification)
