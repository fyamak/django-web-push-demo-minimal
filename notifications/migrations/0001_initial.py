from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


def seed_categories(apps, schema_editor):
    Category = apps.get_model("notifications", "NotificationCategory")
    for code, name, description, order in [
        ("general", "Genel", "Genel uygulama bildirimleri.", 10),
        ("orders", "Siparişler", "Sipariş ve işlem bildirimleri.", 20),
        ("campaigns", "Kampanyalar", "Kampanya ve tanıtım bildirimleri.", 30),
        ("system", "Sistem", "Sistem ve hesap bildirimleri.", 40),
    ]:
        Category.objects.get_or_create(
            code=code,
            defaults={"name": name, "description": description, "sort_order": order},
        )


class Migration(migrations.Migration):
    initial = True

    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL)]

    operations = [
        migrations.CreateModel(
            name="NotificationCategory",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("code", models.SlugField(max_length=50, unique=True)),
                ("name", models.CharField(max_length=100)),
                ("description", models.CharField(blank=True, max_length=250)),
                ("is_active", models.BooleanField(default=True)),
                ("sort_order", models.PositiveIntegerField(default=0)),
            ],
            options={"ordering": ["sort_order", "name"]},
        ),
        migrations.CreateModel(
            name="PushSubscription",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("endpoint", models.TextField(unique=True)),
                ("p256dh", models.TextField()),
                ("auth", models.TextField()),
                ("user_agent", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="push_subscriptions", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["-updated_at"]},
        ),
        migrations.CreateModel(
            name="UserNotificationPreference",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("enabled", models.BooleanField(default=False)),
                ("category", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="user_preferences", to="notifications.notificationcategory")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="notification_preferences", to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name="Notification",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=120)),
                ("body", models.TextField(max_length=500)),
                ("url", models.CharField(default="/", max_length=500)),
                ("sent_count", models.PositiveIntegerField(default=0)),
                ("failed_count", models.PositiveIntegerField(default=0)),
                ("read_at", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("category", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="notifications", to="notifications.notificationcategory")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="notifications", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["-created_at"]},
        ),
        migrations.AddConstraint(
            model_name="usernotificationpreference",
            constraint=models.UniqueConstraint(fields=("user", "category"), name="unique_user_notification_category_preference"),
        ),
        migrations.RunPython(seed_categories, migrations.RunPython.noop),
    ]
