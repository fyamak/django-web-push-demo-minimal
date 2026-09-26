# Minimal Django Web Push

Bu sürüm yalnızca temel akışı bırakır:

- Django kullanıcı girişi / kayıt
- `is_staff=True` kullanıcı için basit admin bildirim ekranı
- Kullanıcının Web Push aboneliğini açıp kapatması
- Kullanıcının kategori tercihlerini yönetmesi
- Kullanıcının bağlı push cihazlarını görmesi
- Sabit içerikli test bildirimi
- Adminin seçili kullanıcılara veya herkese manuel bildirim göndermesi
- Kategorili otonom bildirimler için `send_push_to_user()` servisi

## Dosya yapısı

```text
notifications/
  migrations/0001_initial.py
  templates/
  models.py
  services.py
  views.py
  urls.py
pushdemo/settings/
  base.py
  local.py
  test.py
keys/
docker-compose.local.yml
docker-compose.test.yml
entrypoint.sh
```

Eski demo ekranları, eski AJAX endpoint'leri, demo kullanıcı üretimi ve CLI push komutu kaldırılmıştır.

## PostgreSQL

PostgreSQL Docker dışında, host üzerinde çalışır.

Veritabanı ayarları doğrudan:

```text
pushdemo/settings/local.py
pushdemo/settings/test.py
```

dosyalarındadır.

Test Docker ağı:

```text
172.31.40.0/24
gateway: 172.31.40.1
```

Host PostgreSQL için örnek `pg_hba.conf` satırı:

```conf
host    notification    pushdemo    172.31.40.0/24    scram-sha-256
```

PostgreSQL bu Docker bridge adresinden dinleyebilmelidir. Örneğin `postgresql.conf` içinde uygun `listen_addresses` ayarı gerekir.

## VAPID anahtarları

Anahtarlar artık gizli Docker named volume içinde değildir.

İlk çalıştırmada şu klasörde oluşur:

```text
keys/vapid_private.pem
keys/vapid_public.txt
```

`keys/` klasörünü sunucu yedeğine dahil et. Başka sunucuya taşırken aynı VAPID anahtarlarını da taşı. Private key Git'e eklenmez.

## Local

```bash
docker-compose -f docker-compose.local.yml up --build
```

Uygulama:

```text
http://localhost:8000
```

Admin oluşturmak için:

```bash
docker-compose -f docker-compose.local.yml exec web python manage.py createsuperuser
```

`createsuperuser` kullanıcısı `is_staff=True` olduğu için uygulamanın admin bildirim ekranına gider.

Normal kullanıcı `/signup/` üzerinden kayıt olabilir.

## Test sunucusu

```bash
mkdir -p keys
sudo mkdir -p /var/www/platform_farmingo
docker-compose -f docker-compose.test.yml up -d --build
```

Gunicorn container içinde:

```text
0.0.0.0:8000
```

dinler. Docker bunu yalnızca host loopback'e yayınlar:

```text
127.0.0.1:5001 -> container:8000
```

Host Nginx upstream'i:

```nginx
proxy_pass http://127.0.0.1:5001;
```

Admin oluşturmak için:

```bash
docker-compose -f docker-compose.test.yml exec web python manage.py createsuperuser
```

## Bildirim davranışı

Admin manuel gönderiminde kategori tercihi kontrol edilmez. Kullanıcıda aktif `PushSubscription` varsa gönderilir.

Otonom/kategorili bildirimde kategori tercihi kontrol edilir:

```python
from notifications.models import NotificationCategory
from notifications.services import send_push_to_user

category = NotificationCategory.objects.get(code="system")

send_push_to_user(
    user,
    title="Sistem bildirimi",
    body="Örnek mesaj",
    url="/",
    category=category,
    respect_preferences=True,
)
```

Kullanıcı ilgili kategoriyi açmamışsa gönderim yapılmaz.
