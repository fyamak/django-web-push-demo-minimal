import json
from pathlib import Path

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model, login
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.db.models import Count, Prefetch
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_GET, require_POST, require_http_methods

from .forms import SignUpForm
from .models import Notification, NotificationCategory, PushSubscription, UserNotificationPreference
from .services import send_push_to_user


def _json_body(request):
    try:
        return json.loads(request.body.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return None


def _read_public_key():
    path = Path(settings.VAPID_PUBLIC_KEY_PATH)
    return path.read_text(encoding="utf-8").strip() if path.exists() else ""


def _preference_items(user):
    categories = list(NotificationCategory.objects.filter(is_active=True))
    enabled_ids = set(
        UserNotificationPreference.objects.filter(
            user=user,
            category__in=categories,
            enabled=True,
        ).values_list("category_id", flat=True)
    )
    return [
        {
            "id": category.pk,
            "name": category.name,
            "description": category.description,
            "enabled": category.pk in enabled_ids,
        }
        for category in categories
    ]


@require_http_methods(["GET", "POST"])
def signup(request):
    if request.user.is_authenticated:
        return redirect("notifications:home")

    form = SignUpForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        return redirect("notifications:home")

    return render(request, "registration/signup.html", {"form": form})


@login_required
def home(request):
    if request.user.is_staff:
        return redirect("notifications:admin_home")
    return redirect("notifications:notification_settings")


@login_required
def admin_home(request):
    if not request.user.is_staff:
        raise PermissionDenied

    User = get_user_model()
    enabled_preferences = Prefetch(
        "notification_preferences",
        queryset=UserNotificationPreference.objects.filter(
            enabled=True,
            category__is_active=True,
        ).select_related("category").order_by("category__sort_order", "category__name"),
        to_attr="enabled_notification_preferences",
    )

    users = (
        User.objects.filter(is_active=True, is_staff=False)
        .annotate(subscription_count=Count("push_subscriptions", distinct=True))
        .prefetch_related(enabled_preferences)
        .order_by("username")
    )

    if request.method == "POST":
        send_to_all = request.POST.get("send_to_all") == "on"
        selected_ids = request.POST.getlist("user_ids")
        title = request.POST.get("title", "").strip()[:120]
        body = request.POST.get("body", "").strip()[:500]
        url = request.POST.get("url", "/").strip()[:500]

        if not title or not body:
            messages.error(request, "Başlık ve mesaj zorunludur.")
            return redirect("notifications:admin_home")

        if not url.startswith("/") or url.startswith("//"):
            url = "/"

        targets = users if send_to_all else users.filter(pk__in=selected_ids)
        if not send_to_all and not selected_ids:
            messages.error(request, "En az bir kullanıcı seçin.")
            return redirect("notifications:admin_home")

        result = {"selected": 0, "sent_users": 0, "sent_devices": 0, "failed_devices": 0, "skipped": 0}

        for user in targets:
            result["selected"] += 1
            if user.subscription_count == 0:
                result["skipped"] += 1
                continue

            push = send_push_to_user(
                user,
                title=title,
                body=body,
                url=url,
                category=None,
                respect_preferences=False,
            )
            result["sent_devices"] += push["sent"]
            result["failed_devices"] += push["failed"]
            if push["sent"]:
                result["sent_users"] += 1

        messages.success(
            request,
            f"Seçilen: {result['selected']} | Kullanıcıya gönderildi: {result['sent_users']} | "
            f"Başarılı cihaz: {result['sent_devices']} | Başarısız cihaz: {result['failed_devices']} | "
            f"Bildirim kapalı: {result['skipped']}",
        )
        return redirect("notifications:admin_home")

    return render(request, "notifications/admin_home.html", {"users": users})


@login_required
@require_http_methods(["GET", "POST"])
def notification_settings(request):
    if request.user.is_staff:
        return redirect("notifications:admin_home")

    if request.method == "POST":
        enabled_ids = set()
        for value in request.POST.getlist("category_ids"):
            try:
                enabled_ids.add(int(value))
            except ValueError:
                pass

        categories = list(NotificationCategory.objects.filter(is_active=True))
        valid_ids = {category.pk for category in categories}
        enabled_ids &= valid_ids

        with transaction.atomic():
            for category in categories:
                UserNotificationPreference.objects.update_or_create(
                    user=request.user,
                    category=category,
                    defaults={"enabled": category.pk in enabled_ids},
                )

        messages.success(request, "Bildirim tercihleri kaydedildi.")
        return redirect("notifications:notification_settings")

    subscriptions = PushSubscription.objects.filter(user=request.user)
    return render(
        request,
        "notifications/notification_settings.html",
        {
            "vapid_public_key": _read_public_key(),
            "preference_items": _preference_items(request.user),
            "subscriptions": subscriptions,
            "subscription_count": subscriptions.count(),
        },
    )


@login_required
@require_POST
def subscribe(request):
    data = _json_body(request) or {}
    keys = data.get("keys") or {}
    endpoint = data.get("endpoint")
    p256dh = keys.get("p256dh")
    auth = keys.get("auth")

    if not endpoint or not p256dh or not auth:
        return JsonResponse({"ok": False, "error": "Subscription alanları eksik."}, status=400)

    subscription, created = PushSubscription.objects.update_or_create(
        endpoint=endpoint,
        defaults={
            "user": request.user,
            "p256dh": p256dh,
            "auth": auth,
            "user_agent": request.headers.get("User-Agent", "")[:1000],
        },
    )
    return JsonResponse({"ok": True, "created": created, "id": subscription.pk})


@login_required
@require_POST
def unsubscribe(request):
    endpoint = (_json_body(request) or {}).get("endpoint")
    if not endpoint:
        return JsonResponse({"ok": False, "error": "Endpoint gerekli."}, status=400)

    PushSubscription.objects.filter(user=request.user, endpoint=endpoint).delete()
    return JsonResponse({"ok": True})


@login_required
@require_POST
def send_test(request):
    result = send_push_to_user(
        request.user,
        title="Test bildirimi",
        body="Bildirim sisteminiz başarıyla çalışıyor.",
        url="/",
        category=None,
        respect_preferences=False,
    )

    if result["sent"]:
        messages.success(request, f"Test bildirimi {result['sent']} cihaza gönderildi.")
    else:
        messages.error(request, "Test bildirimi gönderilemedi. Aktif bir bildirim cihazı olduğundan emin olun.")

    return redirect("notifications:notification_settings")


@login_required
@require_GET
def open_notification(request, notification_id):
    notification = get_object_or_404(Notification, pk=notification_id, user=request.user)
    if notification.read_at is None:
        notification.read_at = timezone.now()
        notification.save(update_fields=["read_at"])

    target = notification.url
    if not target.startswith("/") or target.startswith("//"):
        target = "/"
    return HttpResponseRedirect(target)


@require_GET
def manifest(request):
    return JsonResponse(
        {
            "id": "/",
            "name": "Notification Demo",
            "short_name": "Notifications",
            "start_url": "/",
            "scope": "/",
            "display": "standalone",
            "background_color": "#ffffff",
            "theme_color": "#111827",
            "icons": [
                {"src": "/static/notifications/icons/icon-192.png", "sizes": "192x192", "type": "image/png"},
                {"src": "/static/notifications/icons/icon-512.png", "sizes": "512x512", "type": "image/png"},
            ],
        }
    )


@require_GET
def service_worker(request):
    response = render(request, "notifications/service-worker.js", content_type="application/javascript")
    response["Service-Worker-Allowed"] = "/"
    response["Cache-Control"] = "no-cache"
    return response
