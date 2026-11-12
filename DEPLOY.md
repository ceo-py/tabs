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
│   ├── chords.js
│   ├── data/songs.json
│   ├── data/chord_shapes.json
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
  && sudo systemctl restart caddy
```

> ⚠️ Използвай **`restart`**, не `reload`. Глобалният Caddyfile съдържа
> `admin off` → Admin API-то на :2019 не работи и `caddy reload` винаги
> пада с „connection refused“. Пълният restart отнема секунда-две и
> прекъсва за кратко останалите сайтове.

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

## Легенда на акордите (грифни диаграми)

Под вся карта, която показва **само букви** (без грифна диаграма), светът рисува
лента с грифните диаграми на всички акорди от урока. Картите, които вече
имат грифни диаграми в самото видео, не получават лента.

Данните идват от няколко файла в репото:

| файл | какво е |
|---|---|
| `chord_shapes.json` | речникът с формите на 87 акорда (6 струни, лад по струна) |
| `chords.json` | акордите на всяка карта, извадени от `note` полетата на спецификациите |
| `chords_manual.json` | ръчно прочетени акорди за картите, чиито note-и не са в скриптовете |
| `chords_diagram_p1..p4.json` | класификация на всяка карта: `DIAGRAM` / `LETTERS` / `NONE` |
| `chords_has_diagram.json` | сборният файл (създава се от `merge_chord_diagrams.py`) |

```powershell
py -3.14 chord_shapes.py          # -> chord_shapes.json
py -3.14 chord_extract.py         # -> chords.json
py -3.14 merge_chord_diagrams.py  # -> chords_has_diagram.json
py -3.14 build_dist.py            # -> site/ + dist/tabs90-site.zip
```

`site/chords.js` рисува SVG диаграмите (вертикална кутия, 6-а струна отляво),
`site_build.py` слага списъка с акорди в манифеста (`chords` на карта), а
`site/app.js` рисува лентата при отваряне на картата.

## Локално пускане

```powershell
Set-Location site
py -3.14 -m http.server 8765 --bind 0.0.0.0
```

- този компютър: <http://127.0.0.1:8765/>
- телефон в същата мрежа: `http://<LAN-IP>:8765/`

---

## Важни бележки

- **Cloudflare кеш и версии на файловете.** Домейнът минава през Cloudflare, а
  браузърът получава `Cache-Control: max-age=14400` (4 часа) за статиката.
  Затова всеки ребилд добавя `?v=<hash>` към URL-а на променените файлове:
  - `style.css` и `app.js` — версията се записва в `site/index.html`
  - `data/songs.json` — build stamp в `<meta name="site-build">`
  - `cards/*.webp` и `thumbs/*.webp` — собствен hash във всяка карта от манифеста

  `site_build.py` го прави автоматично. **Ръчно редактиране на `app.js` или
  `style.css` без ребилд няма да се види** — първо `py -3.14 build_dist.py`.
- **Ембедването на YouTube** работи на живия домейн (проверено). В локалния
  Electron браузер обаче често показва „This video is unavailable“, защото там
  няма YouTube сесия — това е проблем на браузъра, не на сайта.
- **Шрифтовете** идват от Google Fonts — без изход към Google сайтът пада на
  системните шрифтове (всичко остава работещо).
- `data/songs.json` се вика с `no-cache` и версия, за да се обнови веднага след
  нов deploy; картите и миниатюрите имат собствен URL с версия.
- `Caddyfile` има `admin off` — Caddy Admin API не е достъпен, промените
  стават само чрез файл и `systemctl restart caddy`.
