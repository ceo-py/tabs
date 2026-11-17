# TABS 90 — състояние на проекта

**Вълна 5 в ход — 18 ноември 2026.** Партида 17 (21 песни) е публикувана — жив сайт с
**348 карти**, commit `f73f71a`. **Партида 18 (25 песни) е готова и комитната, но НЕ е
публикувана** — VPS-ът е изключен, деплой не е възможен. Виж „Партида 18“ в раздел 2.
Документът се обновява след всеки деплой — виж раздел 1 за текущите числа.

---

## 1. Какво е готово и публикувано

| Слой | Състояние |
|---|---|
| Жив сайт | <https://tabs.ceo-py.eu/> — **348 карти**, 2 канала, 191 rock, легенда на акордите |
| Локален preview | http://127.0.0.1:8765/ — изключен (стартира се с `Start-Process`, виж т. 6) |
| Репо | `github.com/ceo-py/tabs`, branch `main`, авто-деплой на VPS-а на всеки 5 мин |
| Карти в архива | `out/` (22 карти на Bernadette) + `out_gz/` (344 PNG-та; 326 публикувани + 18 готови от партида 18) |
| Легенда на акордите | 205 форми в речника; 0 неразрешени |

### Функционалност на сайта
- Рендер на каталог от JSON манифест, търсене, чипове по канал/рок
- Lightbox: YouTube embed, карта на цялата ширина, само ✕ горе вдясно, затварянето връща при картата
- Лента **CHORD SHAPES** под картата — SVG грифни диаграми, само за картите с букви (без вече налични грифни диаграми)
- Cache busting с `?v=<hash>` на всеки URL (Cloudflare кешира по URL)
- Пейзаж режим, оптимизиран скрол (без `mix-blend-mode` / `backdrop-filter` / `drop-shadow`)

---

## 2. Каталиогът и партидите

Източник: `gz_tabs_all.json` — **606 песни** с табове от GuitarZero2HeroExpress.
Партидите са по 25 песни и са в `gz_batches/batch<N>.json` (+ `batch<N>_ids.txt`).

| Партида | Песни | Обхват | Карти |
|---|---|---|---|
| 1–5 | 125 | първите 125 от каталога | ✅ 125/125 |
| 6 | 25 | 125–149 | ✅ 25/25 (завършена във вълна 3+4) |
| 7 | 25 | | ✅ 25/25 |
| 8 | 25 | | ✅ 25/25 |
| 9 | 25 | 150–174 | ✅ 25/25 |
| 10 | 25 | 175–199 | ✅ 25/25 |
| 11 | 25 | 200–224 | ✅ 25/25 (остатъкът — 14 — е вълна 4) |
| 12 | 25 | 225–249 | ✅ 25/25 (остатъкът — 20 — е вълна 4) |
| **13** | **25** | **250–274** | **✅ 25/25 (вълна 4)** |
| **14** | **25** | **275–299** | **✅ 25/25 (текущата вълна — 4 агента × 5–6 песни)** |
| 15 | 25 | 300–324 | ⏸ отложена (5 карти са готови и публикувани) |
| 16 | 25 | 325–349 | ⏸ отложена (0 карти) |
| **17** | **21** | RHCP 8 · Nirvana 7 · Linkin Park 6 | **✅ 21/21 — публикувана (вълна 5)** |
| **18** | **25** | Metallica 3 · Queen 3 · Rolling Stones 3 · Smashing Pumpkins 3 · U2 3 · Oasis 2 · Pearl Jam 2 · Stone Sour 2 · The Police 2 · Radiohead 2 | **✅ 25/25 готови — комитната, непубликувана (VPS изключен)** |

### Партида 18 — готова, чака деплой (18 ноември)

Манифест: `gz_batches/batch18.json` (25 песни) + `batch18_ids.txt`.
Видеата са свалени **25/25** в `dl/w4_<ID>.mp4`. Бриф: `B18-BRIEF.md`.

| Агент | Изпълнители | Карти | Класификация |
|---|---|---|---|
| b18a | Metallica 3 + Queen 3 | 6/6 | 4 LETTERS + 2 DIAGRAM (Enter Sandman, Bohemian Rhapsody Solo) |
| b18b | Rolling Stones 3 + Smashing Pumpkins 3 | 6/6 | 6 LETTERS |
| b18c | U2 3 + Oasis 2 + The Police 2 | 7/7 | 5 LETTERS + 1 DIAGRAM (EBYT studio) + 1 LETTERS (EBYT acoustic) |
| b18d | Pearl Jam 2 + Stone Sour 2 + Radiohead 2 | 6/6 | 6 LETTERS |

Общо: **22 LETTERS + 3 DIAGRAM** → `chords_diagram_p20.json`.
Каталогът след импорта: **373 песни** (325 LETTERS · 27 DIAGRAM · 21 NONE),
350/373 с акорди, 219 форми в речника.

⚠️ **Не е публикувано** — VPS-ът (`Oriahovo`) е изключен, `tabs-deploy.sh` не може да се
изпълни. Когато сървърът се върне, деплойът е:
```powershell
$SSH = (Get-ChildItem 'C:\Windows\WinSxS' -Filter 'ssh.exe' -Recurse | Where-Object { $_.FullName -like '*openssh-client-components-onecore*' -and $_.DirectoryName -notlike '*\r' } | Select-Object -First 1).FullName
$script = '/home/ceo/production/tabs-deploy.sh && tail -3 /home/ceo/production/deploy.log'
$b64 = [Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes($script))
& $SSH -F "$HOME\.ssh\config" -o BatchMode=yes -o ConnectTimeout=20 Oriahovo "echo $b64 | base64 -d | bash"
```
(`remote.ps1` още сочи към build `10.0.26100.9444` на `ssh.exe`, който го няма след Windows
ъпдейта → `10.0.26100.9711`; да се ползва горният начин.)

Остават в каталога на канала **606 − 351 = 255** песни за бъдещи вълни
(39 в готови партидни файлове batch15/16, 216 без такъв; 143 изпълнителя).
(351 = 373 публикувани − 22 карти на BernadetteTeachesMusic, които не са от този канал.)

**Решение на потребителя (13 ноември):** 100 нови песни е твърде много → вълната е стеснена
до остатъците + **следващите 25** (партида 13), а след това — партида 14 по същия принцип.
Партиди 15–16 са отложени, не отменени — манифестите им са генерирани, а 5-те вече готови
карти от 15 са публикувани.

Остават в каталога **606 − 327 = 279** песни за бъдещи вълни (партиди 15+).

### Как се генерират нови партиди
```powershell
py -3.14 gz_make_batches4.py     # остатъците + партиди 13..16 (индекс 250..349)
# за следваща вълна: WAVE3_START = 350 в gz_make_batches4.py -> партиди 17..20
```
Видеата се свалят наведнъж на фон:
```powershell
py -3.14 download_w4.py          # -> dl/w4_<ID>.mp4  (PO-Token сървър на 127.0.0.1:4416)
```

---

## 3. Как се прави карта (pipeline)

1. **Видео** → `dl/v_<ID>.mp4` (стари партиди) или `dl/w4_<ID>.mp4` (нови)
2. **Survey** → `b13_survey.py` намира червената лента с името на секцията, групира кадрите
   по секции и пише в `frames/b13_<ID>/`: `survey.png` (монтаж: `#n t=<a>-<b>s crop=[x,y,w,h]`
   + заглавие на секцията + панел), `sections.json`, `panels.json`.
   `b13_labels.py` прави лист с всички заглавия на секции изправени.
3. **Спецификация** → `b<N>_spec/<ID>.json`:
   `{"title", "subtitle", "out", "panels":[{"label","t","bbox","png"}], "note"}`
   — `bbox` е в **изходни пиксели** на видеото, `t` е секунда в секцията.
4. **Компоновка** → `b13_build.py` реже crop-овете с ffmpeg и вика `b13_compose.make_card(...)`
   → PNG в `out_gz/` (footer `GuitarZero2HeroExpress`, линк към видеото в долния ляв ъгъл).
5. **Проверка** → всяка карта се чете с `read` инструмента; нередна geometry се поправя и се
   рендерира наново. Агентът трябва да преотчете crop-а, ако панелът е отрязан.

Схемата на канала (1920x1080), ориентир за crop:
```
x=0..260      вертикална грифна диаграма (дървена) — обикновено се пропуска
y=558..1078   TAB панелът:  y=558..620 червена лента (VERSE/CHORUS/BRIDGE/INTRO)
                           y=620..1078 белият лист с 6-редови TAB
```

> **Съдържанието идва само от кадрите на видеото** — никога да не се реконструират акорди,
> прогресии или удари по струните. Ако видеото не показва strumming pattern, разделът се
> пропуска и се отбелязва в note-а на картата.

---

## 4. Легенда на акордите

Всяка карта трябва да е класифицирана, за да знае сайтът дали да показва легендата:

- `DIAGRAM` — картата вече съдържа грифна диаграма → легенда **не** се показва
- `LETTERS` — картата показва само букви (имена на акорди) → легенда се показва
- `NONE` — няма имена на акорди → нищо не се добавя

```powershell
py -3.14 make_crops3.py                 # crop-ове (долна 60%) + контактни листове
# агент чете dbg_crops3_sheets/sheet_*.png и пише chords_diagram_p<N>.json
py -3.14 merge_chord_diagrams.py        # p1..pN (+p99 поправки) -> chords_has_diagram.json
```

Класификацията на партида 14 е в `chords_diagram_p16/p17/p18.json` (12 + 6 + 5 карти).
`_c14_crops.py` е scratch помощник: реже crop-ове за списък от карти, когато още не са
в `songs.json` (за класификация преди импорта).

Речникът с формите се генерира автоматично:
```powershell
py -3.14 chord_extract.py               # акорди от note-ите (b*_spec/ + b*_build.py)
py -3.14 chord_shapes.py                # -> chord_shapes.json (203 форми)
```
`chord_extract.py` разбира ръчно написаните ноутри: `A(D/F#)` = два акорда,
`Bm7(1)` = позиция, `Fmaj7(b5)` = качество. `chord_shapes.py` добавя автоматично
изчислима позиция (`chord_voicings.py`) за всеки акорд, който липсва в речника.

---

## 5. Публикуване

```powershell
py -3.14 import_cards.py        # нови карти -> songs.json (обхваща партиди 1..16)
py -3.14 merge_chord_diagrams.py # p1..p18 (+p99 поправки) -> chords_has_diagram.json
py -3.14 chord_extract.py       # акорди за новите карти ( AFTER merge: картите,
                                 # класифицирани като NONE, се пропускат)
py -3.14 chord_shapes.py        # -> chord_shapes.json (203 форми)
py -3.14 site_build.py          # -> site/cards, site/thumbs, site/data/songs.json
git -C <repo> add -A ; git -C <repo> commit -m "..." ; git -C <repo> push origin main
```
`merge_chord_diagrams.py` сортира файловете по число (`p2` преди `p13`), а `p99` е
файлът с ръчни поправки — той се прилага последен и презаписва останалите.

**Съгласуваност (трябва да е 0 и 0):** карта, класифицирана като NONE, няма да има
акордови данни; карта, класифицирана като LETTERS, трябва да има.
VPS-ът се обновява сам (user crontab `*/5 * * * *`). Ръчен деплой:
```powershell
. 'D:\MiniMax Code Repos\Guitar Lessons\remote.ps1'
Invoke-Remote '/home/ceo/production/tabs-deploy.sh && tail -3 /home/ceo/production/deploy.log'
```

**Проверка на живото:**
```powershell
(Invoke-WebRequest 'https://tabs.ceo-py.eu/data/songs.json' -UseBasicParsing).Content | ConvertFrom-Json
```

---

## 6. Локален preview и deployment

```powershell
# локален preview (отделен процес, не умира с тайм-аута на задачата)
Start-Process -FilePath 'py' -ArgumentList '-3.14','-m','http.server','8765','--bind','0.0.0.0' `
  -WorkingDirectory 'D:\MiniMax Code Repos\Guitar Lessons\site' -WindowStyle Hidden
```
VPS: `/home/ceo/production/tabs/` = web root, `/home/ceo/production/tabs-repo/` = clone,
`tabs-deploy.sh` = pull + sync. DNS `tabs.ceo-py.eu` → Cloudflare (proxy ON).

---

## 7. Важни правила на проекта

- **Съдържанието идва само от кадрите на видеото** — никога да не се реконструират акорди,
  прогресии или удари по струните. Ако видеото не показва strumming pattern, разделът се пропуска.
- Споделените помощни файлове (`card.py`, `compose_lib.py`, `survey.py`, `montage.py`,
  `PLAYBOOK.md`, `PLAYBOOK-GZ.md`) **не се редактират**. За нова партида се прави копия:
  `bN_compose.py` + `bN_build.py` + `bN_spec/`.
- Архивът (`out/`, `out_gz/`) е непокътнат; линкът към видеото се маха **само в сайт асетите**
  (`strip_link.py` вътре в `site_build.py`).
- `songs.json` е единственият източник на истина; `import_cards.py` пази ръчните редакции.
- Агентските скриптове работят сами — **агентите не правят git операции**, комитва се от parent сесията.
- Caddy: `restart`, не `reload` (`admin off`); конфиг в `/etc/caddy/caddy.d/tabs.conf`,
  source-of-truth в репото `deploy/tabs.conf`. Sudo изисква парола → потребителят.
- Изтриване само през recoverable delete: `rm -- "<path>"` (самоцелна команда).
- Git: `git -C <path>`; не се прави `git add` след `Set-Location`.
- Лимит: **4 конкурентни child task-а**.

---

## 8. Помощни скриптове

| файл | роля |
|---|---|
| `gz_make_batches4.py` | генерира остатъците + партиди 13–16 от каталога |
| `download_w4.py` | фоново сваляне на видеата за нова партида |
| `b13_survey.py` / `b13_labels.py` | survey на видеото: секции, времена, crop кутии |
| `b13_build.py` / `b13_compose.py` | реже crop-овете и композира картата |
| `b16_prep.py` / `b16_titles.py` / `b16_stack.py` | алтернативен layout-aware survey (вертикални ленти, черен фон) |
| `make_crops3.py` | crop-ове (долна 60%) + контактни листове за класификация |
| `merge_chord_diagrams.py` | обединява `chords_diagram_p*.json` → `chords_has_diagram.json` |
| `chord_extract.py` | вади акордите от `note` полетата (автоматично от всички `b*_spec/`) |
| `chord_shapes.py` | речникът с формите + автоматично генериране на липсващи |
| `chord_voicings.py` | намира изиграема позиция за произволен акорд |
| `strip_link.py` | маха линка към видеото от футъра (само в сайт асетите) |
