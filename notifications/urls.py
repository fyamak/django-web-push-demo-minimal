from django.urls import path

from . import views

app_name = "notifications"

urlpatterns = [
    path("", views.home, name="home"),
    path("signup/", views.signup, name="signup"),
    path("admin-home/", views.admin_home, name="admin_home"),
    
    path("notification-settings/", views.notification_settings, name="notification_settings"),
    
    path("api/push/subscribe/", views.subscribe, name="subscribe"),
    path("api/push/unsubscribe/", views.unsubscribe, name="unsubscribe"),
    path("api/push/send-test/", views.send_test, name="send_test"),
    path("notifications/<int:notification_id>/open/", views.open_notification, name="open_notification"),
    path("manifest.json", views.manifest, name="manifest"),
    path("service-worker.js", views.service_worker, name="service_worker"),
]
