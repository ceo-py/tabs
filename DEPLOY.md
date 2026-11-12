# Качване и обновяване на TABS 90

Сайтът е **изцяло статичен** — Caddy му обслужва файловете и нищо друго.
Няма Node, няма PHP, няма база данни, няма build на сървъра.

## Къде какво стои на VPS-а (Oriahovo)

```
/home/ceo/production/
├── tabs/              ← WEB ROOT, това се сервира (index.html в корена)
│   ├── index.html
│   ├── style.css
│   ├── app.js
│   ├── data/songs.json
│   ├── cards/*.webp   (72)
│   └── thumbs/*.webp  (72)
├── tabs-repo/         ← git clone на github.com/ceo-py/tabs.git
├── tabs-deploy.sh     ← скриптът, който дърпа репото и синхронизира site/ -> tabs/
└── deploy.log         ← логът му

/etc/caddy/
├── Caddyfile          ← глобален: admin off + import caddy.d/*.conf
└── caddy.d/
    ├── api-camera.conf
    ├── jellyfin.conf
    ├── nextcloud.conf
    ├── pi-hole.conf
    ├── ...
    └── tabs.conf      ← настройките за ТОЗИ сайт (нужен е sudo за копирането)
```

Всяка настройка на сайт е в **отделен файл** в `caddy.d/` — същата структура
като останалите сайтове. Скриптът `tabs-deploy.sh` е в user crontab-а и
дърпа репото на всеки 5 минути, така че `git push` в GitHub обновява живия
сайт автоматично.

## Първоначална инсталация на Caddy блока (само веднъж, иска sudo)

Файлът с настройките живее в репото: `deploy/tabs.conf`.

```bash
sudo cp /home/ceo/production/tabs-repo/deploy/tabs.conf /etc/caddy/caddy.d/tabs.conf \
  && sudo caddy validate --config /etc/caddy/Caddyfile \
  && sudo systemctl reload caddy
```

Caddy сам ще вземе TLS сертификата (DNS-ът вече сочи към VPS-а).

Проверка:

```bash
curl -sI https://tabs.ceo-py.eu/ | head -3
```

## Обновяване при нови карти

Локално (на машината с проекта):

```powershell
py -3.14 build_dist.py     # import_cards -> site_build -> dist/tabs90-site.zip
git add -A
git commit -m "new cards"
git push
```

VPS-ът го вижда до 5 минути (cron) и обновява `~/production/tabs`.
За незабавно обновяване — без да чакаш cron-а:

```bash
/home/ceo/production/tabs-deploy.sh && tail -3 /home/ceo/production/deploy.log
```

Ръчно качване през scp (без Git) също работи:

```bash
scp dist/tabs90-site.zip user@vps:/tmp/
ssh user@vps 'unzip -o /tmp/tabs90-site.zip -d /home/ceo/production/tabs'
```

## Локално пускане

```powershell
Set-Location site
py -3.14 -m http.server 8765 --bind 0.0.0.0
```

- този компютър: <http://127.0.0.1:8765/>
- телефон в същата мрежа: `http://<LAN-IP>:8765/`

---

## Важни бележки

- **Ембедването на YouTube** зависи от настройките на канала (embedding) и
  от браузъра на посетителя. Ако някое видео откаже да се пуска вътре в
  плеъра, картата все пак показва пълните табове, а бутонът
  **OPEN ON YOUTUBE** го отваря директно.
- **Шрифтовете** идват от Google Fonts — без изход към Google сайтът пада на
  системните шрифтове (всичко остава работещо).
- `data/songs.json` е с `no-cache`, за да се обнови веднага след нов deploy;
  картите и миниатюрите са с кеш 1 ден.
- `Caddyfile` има `admin off` — Caddy Admin API не е достъпен, промените
  стават само чрез файл и `systemctl reload caddy`.
