const ICON = "/static/notifications/icons/icon-192.png";

self.addEventListener("install", () => self.skipWaiting());
self.addEventListener("activate", event => event.waitUntil(self.clients.claim()));

self.addEventListener("push", event => {
  let data = {title: "Bildirim", body: "Yeni bir bildiriminiz var.", url: "/"};
  if (event.data) {
    try { data = {...data, ...event.data.json()}; }
    catch (_) { data.body = event.data.text(); }
  }
  event.waitUntil(self.registration.showNotification(data.title, {
    body: data.body,
    icon: ICON,
    badge: ICON,
    tag: data.tag || `notification-${data.notification_id || Date.now()}`,
    data: {url: data.url || "/"},
  }));
});

self.addEventListener("notificationclick", event => {
  event.notification.close();
  event.waitUntil(self.clients.openWindow(event.notification.data?.url || "/"));
});
