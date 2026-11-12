# Качване на сайта на VPS-а (Caddy)

Сайтът е **изцяло статичен** — Caddy му обслужва файловете и нищо друго.
Няма Node, няма PHP, няма база данни, няма build на сървъра.

## 1. Подготвен пакет

```powershell
py -3.14 build_dist.py
```

Резултат: `dist/tabs90-site.zip` (~10 MB) — готов за качване.

## 2. На сървъра

```bash
ssh <user>@<vps>

sudo mkdir -p /var/www/tabs90
sudo chown -R $USER:$USER /var/www/tabs90
cd /var/www/tabs90

# качи архива (от твоята машина):
#   scp dist/tabs90-site.zip user@vps:/tmp/

unzip -o /tmp/tabs90-site.zip -d /var/www/tabs90
ls -la /var/www/tabs90      # index.html трябва да е в корена
```

Ако няма `unzip`: `apt install unzip`.

## 3. Caddy

Отвори `/etc/caddy/Caddyfile` и добави блока (замени домейна с твоя):

```caddy
tabs90.example.com {
    root * /var/www/tabs90
    file_server

    # кеш за статиката, но не за манифеста
    @manifest path /data/songs.json
    header @manifest Cache-Control "no-cache"
    header Cache-Control "public, max-age=3600"

    # YouTube вграждания -> всичко е от youtube-nocookie.com
    header {
        Content-Security-Policy "default-src 'self'; img-src 'self' data: https:; frame-src https://www.youtube-nocookie.com https://www.youtube.com; script-src 'self' 'unsafe-inline' https://www.youtube.com https://www.youtube-nocookie.com; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com; connect-src 'self' https://www.youtube-nocookie.com https://www.youtube.com"
        X-Content-Type-Options "nosniff"
        Referrer-Policy "strict-origin-when-cross-origin"
    }
}
```

После:

```bash
sudo caddy validate --config /etc/caddy/Caddyfile
sudo systemctl reload caddy
```

Caddy сам ще вземе TLS сертификата (Let's Encrypt), ако DNS сочи към VPS-а.

## 4. Обновяване, когато излязат нови карти

Локално:

```powershell
py -3.14 build_dist.py     # обновява каталога + assets + архива
```

На сървъра:

```bash
scp dist/tabs90-site.zip user@vps:/tmp/
ssh user@vps 'unzip -o /tmp/tabs90-site.zip -d /var/www/tabs90 && systemctl reload caddy'
```

Това е целият цикъл. `import_cards.py` добавя само нови записи и не пипа
ръчно редактираните, `site_build.py` генерира webp файловете и манифеста.

## 5. Напълно автоматично обновяване (когато имаш субдомейн)

Двата варианта се избират **веднъж**, после само се push-ва:

**Вариант А — GitHub Actions → rsync към VPS-а**
- repo в GitHub, push-ваш `songs.json` + `site/`
- workflow: `py import_cards.py && py site_build.py` → rsync `site/` на сървъра
- нужен е deploy key (без пароли)

**Вариант Б — сам VPS-ът дърпа от Git**
- `git clone` на сървъра + systemd timer, който на всеки час прави
  `git pull && py site_build.py` и релоадва Caddy

И двате работят с едно и също съдържание — разликата е къде тече build-ът.
Ако искаш, мога да го настроя, когато субдомейнът е готов.

---

## Важни бележки

- **Ембедването на YouTube** зависи от настройките на канала (embedding).
  Ако някое видео откаже да се пуска вътре в плеъра, картата все пак
  показва пълните табове, а бутонът **OPEN ON YOUTUBE** го отваря директно.
- **Шрифтовете** идват от Google Fonts — ако VPS-ът няма изход към Google,
  сайтът ще падне на системните шрифтове (всичко остава работещо).
- `data/songs.json` е с `no-cache`, за да се обнови веднага след нов deploy;
  картите и миниатюрите са с кеш.
