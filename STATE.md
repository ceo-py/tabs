# TABS 90 — състояние на проекта

**19 ноември 2026.** Жив сайт: **348 карти** (build `f73f71a`), комитнат е `70d1fd1` (партида 19,
389 карти), но **партида 19 не е публикувана** — VPS-ът е изключен и деплой не е възможен.
**Партида 20 (Oasis, 20 урока от 4 нови канала) е в ход** — 12/20 карти са готови и комитнати
(`ff43fd0`), 8 остават (b20a + b20d). Виж **раздел 9** за пълното състояние и точните команди.
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
| **18** | **25** | Metallica 3 · Queen 3 · Rolling Stones 3 · Smashing Pumpkins 3 · U2 3 · Oasis 2 · Pearl Jam 2 · Stone Sour 2 · The Police 2 · Radiohead 2 | **✅ 25/25 готови — комитната (`c9d99d5`), непубликувана (VPS изключен)** |
| **19** | **16** | Lady Gaga 2 · Lady Gaga & Bradley Cooper 1 · Phil Collins · Pink Floyd · R.E.M. · REM · Rage Against The Machine · Santana · Shania Twain · Slipknot · The Cranberries · The Offspring · The Verve · Tracy Chapman · Wheatus | **✅ 16/16 готови — комитната, непубликувана (VPS изключен)** |

### Партида 19 — готова, комитната, чака деплой (18 ноември, ~11:50)

Манифест: `gz_batches/batch19.json` + `batch19_ids.txt` (**16 песни**).
Видеата са свалени **16/16** в `dl/w4_<ID>.mp4` (PO-Token сървър на `127.0.0.1:4416` — ако
не работи, пусни го от `potsrc/server/` с `denobin/deno.exe run --allow-all
--node-modules-dir=manual src/main.ts -p 4416`).
Бриф: `B19-BRIEF.md`. Класификация: `chords_diagram_p21.json`.

| Агент | Изпълнители | Карти | Класификация |
|---|---|---|---|
| b19a | Lady Gaga ×2 + Lady Gaga & Bradley Cooper + Phil Collins | 4/4 | 4 LETTERS |
| b19b | Pink Floyd · R.E.M. · REM · Rage Against The Machine | 4/4 | 3 LETTERS + 1 NONE (Killing In The Name) |
| b19c | Santana · Shania Twain · Slipknot · The Cranberries | 4/4 | 4 LETTERS |
| b19d | The Offspring · The Verve · Tracy Chapman · Wheatus | 4/4 | 4 LETTERS |

⚠️ **3-те Lady Gaga песни са преместени** от batch15/batch16 в batch19, за да не са в два
партидни файла едновременно: `YGGjna1GkK0` (Always Remember Us This Way),
`gz0mC6yiMFQ` (I'll Never Love Again) → от batch15; `11plqWEM8cc` (Shallow) → от batch16.
Сега: batch15 = 23, batch16 = 24, batch19 = 16. Няма дубликати в batch1..batch19 (403).

⚠️ **Ръчна корекция на класификацията:** `Rage Against The Machine - Killing In The Name`
беше дадена от агента като `DIAGRAM`, но видеото показва **само TAB** (H/P/P.M. темпо марки,
без имена на акорди и без грифна диаграма) → поправена на `NONE`. Проверено визуално по
4-те панела (`frames/b19b__9K3nBCkwbs/p0..p3.png`).

Резултат от pipeline-а: `import_cards` → **389 песни** (+16) · merge → 340 LETTERS /
27 DIAGRAM / 22 NONE · `chord_extract` → 364/389 · `chord_shapes` → **221 форми** ·
съгласуваност: **0 LETTERS без акорди, 0 NONE с акорди**.
`REMAINING-LESSONS.md`: **239 остатъка / 129 изпълнителя** (36 в готови batch15/16/18+19,
203 без партиден файл).

**Следващи стъпки:**
```powershell
git add <явни пътища> ; git commit ; git push origin main
# деплой (само ако VPS-ът е назад)
```

> `import_cards.py` вече чете `range(1, 20)` (batch19 е включен).

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

---

## 9. ПАРТИДА 20 — Oasis (4 нови канала)

> **АКТУАЛНО СЪСТОЯНИЕ: 19 ноември 2026, 22:40.**
> **Партида 20 е ЗАВЪРШЕНА, комитната и push-ната: `669e6c8`.**
> Каталогът: **389 → 410 песни**. Класификация: **17 LETTERS + 2 DIAGRAM + 2 NONE**.
> Сайт: 410 карти + 410 thumbs (820 webp, всички валидни), 69 MB.
> Активни агенти: **партида 21** (6 урока / 5 нови канала) + одит на b20a/b20d.
> Историята на прекъсването (18 ноември 13:20) е под този блок.

### 9.0 Актуално състояние (19 ноември 2026)

| # | задача | статус |
|---|---|---|
| 1 | **b20a** — Lex Guitar Tabs, 6 урока (вкл. Stand By Me) | ✅ 6/6 · 3 LETTERS + 1 DIAGRAM + 2 LETTERS |
| 2 | **b20b** — guitar cover with tabs & chords, 8 урока | ✅ 8/8 · 8 LETTERS |
| 3 | **b20c** — ike, 4 урока | ✅ 4/4 · 4 LETTERS |
| 4 | **b20d** — Sparky Guitar, 3 урока | ✅ 3/3 · 1 LETTERS + 2 NONE |
| 5 | класификация `chords_diagram_p22.json` | ✅ 21 карти (17/2/2) |
| 6 | pipeline | ✅ 410 песни · 357 LETTERS / 29 DIAGRAM / 24 NONE · 382 с акорди · 229 форми · **0 несъгласуваности** |
| 7 | site_build | ✅ 410 карти + 410 thumbs, 820 webp валидни, 69 MB |
| 8 | commit + push | ✅ `669e6c8` → **push-нат** |
| 9 | маркирани списъци + `REMAINING-LESSONS.md` | ✅ 2792 видео маркирани · REMAINING: 239 (GZ2H, непроменен — песните са от други канали) |
| 10 | **партида 21** — 6 урока / 5 нови канала | 🔄 в ход (манифест, видеата и брифът са готови) |
| 11 | деплой на VPS-а | 🔒 блокиран — SSH връзката се затваря, сайтът не отговаря и на 20 s; чака физически рестарт |

Комити по партида 20:
* `ff43fd0` — **part 1**: 12 карти (b20b + b20c), research списъците с маркерите, `B20-BRIEF.md`,
  `gz_batches/batch20.json`, `import_cards.py`, `site_build.py` → **push-нат**
* `b7f5e7b` — **part 2**: 5 карти от Lex Guitar Tabs (b20a)
* `3be5021` — **part 3**: 3 карти от Sparky Guitar (b20d) + 21-ви урок Stand By Me
* `669e6c8` — **финал**: пълният pipeline (410 карти), всичките 21 рендерирани карти,
  поправените spec-и, списъците, `B21-BRIEF.md`, манифестът на партида 21 → **push-нат**

#### Находки от независимия одит (важни!)

Одит на 12-те карти от b20b/b20c потвърди, че **геометрията, crop-ите (pixel-exact 40/40),
label-ите, класификацията и темпото са перфектни**, но откри:

* **8 карти с неточен note** — note-ът изброява акорди, които **не се виждат** на картата
  (`G#m`/`A`/`A7` при Rock 'n' Roll Star, `D/F#` при Slide Away, `C#7` при Supersonic,
  `FM7(9)` при Live Forever, `G6/A` при Lyla, `G`/`FM7` при Champagne Supernova).
* **1 карта отрича strumming, който се вижда** — D'You Know What I Mean? (`BYLzgA94yxU`) има
  реална strumming схема в bars 6–7.
* **2 карти остарели спрямо spec-а** — Slide Away (`d1RxW2VIVcI`, липсва `C` в note-а) и
  Stay Young (`kBs2nBraZBM`, label `TAB · SOLO` вместо `CHORDS & TAB · SOLO`).
  И двете са били рендирани преди последната промяна на spec-а.
* 2 фактически грешни твърдения в note-а — Songbird („no section title printed", но видеото
  печата „Verse 1"), Roll With It („chorus progression", но на екрана е „Verse 2").

⇒ Всичко това е поправено от агентите b20b/b20c (spec + прекомпозиране) и **трябва да се
рекомпозира наново след общата поправка на compose копията** (виж т. 9.4).

#### Два дефекта в композера, открити и поправени

1. `note_extra = 32*(n-2)` резервираше 32 px по-малко от нужното → последният ред на note-а
   сядаше на 1 px от долния ръб и изглеждаше отрязан. Копията на b20a е вече `32*(n-1)`.
2. `wrap_note()` дели по `' '` и събира с `' '` → трите интервала между полетата на note-а
   („Chords: …   Strumming: …“) се свиват до един и полетата се слепват.
   Поправено с `re.sub(r'\s{2,}', ' · ', note)` в копията на b20a.

`_b20_finalize.py` applyingва и двете поправки към b20b/b20c/b20d, прекомпозира **всичките 21
карти** и проверява всяка (размер на панел = bbox, четни y/височини, `out` = манифест).

#### Проверка на връзката id ↔ песен

`_b20_verify_titles.py` изтегля реалните заглавия на всичките 21 видео →
**21/21 съвпадат** с манифеста (`_b20_real_titles.json`).

#### Покритие на Oasis — какво още липсва

`_oasis_gap.py` сканира **целия корпус** (50 490 видеа) за всяка канонична Oasis песен
(предишният отчет гледаше само видеата с „Oasis“ в заглавието). Резултат:

* Остават без карта **27 от 56** песни.
* От тях **само 1** има използваемо tab видео в корпуса → **Stand By Me** (добавен в партида 20).
* Останалите ~26 са **лъжливи съвпадения** или нямат източник:
  „The Turning“ → Pink Floyd, „My Big Mouth“ → Minor Threat, „All Around The World“ →
  Judas Priest, „Party On“ → Bloc Party / Deftones и т.н.
* `_oasis_search.py` (търсене в YouTube) намира кандидати за **Acquiesce**, **Digsy's Dinner**,
  **Who Feels Love**, **The Hindu Times**, **Love Like A Bomb**, **Boy With The Blues** —
  в канали, които **не са** в измерените 112: **G.S.N. Tabs**, **Fretboard Fundamentals**,
  **Behnam Guitar Tabs**, **Danny Trenton Guitar**, **At sushi**, **Kevin Carrion**.
  → това е кандидат за **партида 21**.

---

### Какво беше готово при спирането (18 ноември 13:20)

**Работата беше спряна по нареждане на потребителя. Тогава нищо не беше комитнато за партида 20.**

### Какво е готово
* `gz_batches/batch20.json` — 20 урока (score >= 30), всеки с `source_channel`
* **20/20 видеа свалени** в `dl/w4_<ID>.mp4` (1080p60, 43–230 MB)
* **12 от 20 карти ПОСТРОЕНИ и проверени визуално** (всички `LETTERS`):
  * `b20b` — guitar cover with tabs & chords: **8/8**
    (D'You Know What I Mean?, I Hope I Think I Know, Live Forever, Morning Glory,
     Rock 'n' Roll Star, Slide Away, Supersonic, Champagne Supernova)
  * `b20c` — ike: **4/4** (Lyla, Roll With It, Songbird, Stay Young)
  * спецификациите са в `b20b_spec/` (8) и `b20c_spec/` (4), всички с `diagram: LETTERS`
  * картите са в `out_gz/Oasis-*.png` (12 файла)
* `_b20_classify.py` — готов, пише `chords_diagram_p22.json` (ще обере 12-те готови)
* `import_cards.py` — `range(1, 21)` + `channel` от `source_channel` (тествано: каталогът
  остава стабилен на 389, 0 промени)
* `site_build.py` — списъкът с канали се генерира динамично през `CHANNEL_URLS`

### Какво НЕ е направено
| # | задача | статус |
|---|---|---|
| 1 | **b20a** — Lex Guitar Tabs, 5 урока (Half The World Away, Whatever, Cigarettes & Alcohol, She's Electric, Some Might Say) | 0 спецификации. Агентът беше в измерване на геометрията и откри, че **layout-ът се различава между видеа от един и същ канал** → трябва отделни bbox-и за всяко видео |
| 2 | **b20d** — Sparky Guitar, 3 урока (Columbia, Masterplan, Shakermaker) | 0 спецификации. Агентът беше в измерване на геометрията |
| 3 | класификация `chords_diagram_p22.json` | не е пусната (готов е `_b20_classify.py`) |
| 4 | pipeline (import_cards -> merge -> chord_extract -> chord_shapes -> site_build) | не е пуснат |
| 5 | commit + push на партида 20 | ✅ **направен за part 1** (`ff43fd0`, push-нат); остатъка след pipeline-а |
| 6 | деплой на VPS-а | блокиран — машината е жива, но задушена (`Exceeded MaxStartups`), чака физически рестарт |
| 7 | `REMAINING-LESSONS.md` + `STATE.md` след партида 20 | не е обновен (STATE.md е обновен с раздел 9) |
| 8 | маркираните списъци след новите карти | не е прегенерирано (виж т. 9.1) |

### Как се продължава
```powershell
# 1. b20a и b20d агентите се рестартират (вече са активни от 19.11) — готови сканери:
#    b20a_grab.py / b20a_probe.py / b20a_grid.py / b20a_sheet.py / b20a_arrows.py
#    b20d_grab.py / b20d_scan.py / b20d_sheet.py / b20d_tiles.py
py -3.14 b20a_build.py wtjoRQfmHQI 6CVKC5LVAAs 1F7ZncckR1o 42GX06WDX5w qPTV5wkocv0
py -3.14 b20d_build.py Lbs---ONA3I p0Fpu1mZKOk B-BkCZrGp2M

# 2. класификация (ще вземе всички 20)
py -3.14 _b20_classify.py          # -> chords_diagram_p22.json

# 3. pipeline
py -3.14 import_cards.py           # 389 -> 409
py -3.14 merge_chord_diagrams.py
py -3.14 chord_extract.py
py -3.14 chord_shapes.py
py -3.14 site_build.py             # бавен ~13 мин
py -3.14 list_remaining.py         # -> REMAINING-LESSONS.md
```

### 9.1 Маркиране „вече го имаме“ в research списъците — ГОВОРЕНО

Направено е на 18 ноември 2026. `_mark_have.py` сверява целия корпус
(112 канала / 50 490 видеа) с `songs.json` и прегенерира:

| файл | какво е променено |
|---|---|
| `_channel_lists/*.md` (112) | нова колона `Карта`: `✅ Артист — Песен` за всяко видео с готова карта |
| `_artist_lists/*.md` (95) | нова колона `Имаме`: колко видеа с tab от този артист вече покриваме |
| `_artists_per_channel.md` / `.csv` (11 651 реда) | същата колка по канал |
| `_oasis_by_song.md` | маркира покритите Oasis песни |
| `_have_map.json` | машинен mapping URL -> нашата карта |

Резултат при създаването: **2 731 от 50 490 видеа** маркирани (389 карти).
Проверена извадка от 20 случайни съвпадения — няма лъжливи.

⚠️ **Правило за съвпадение (важно):** изисква се името на артиста да е в
заглавието на видеото. По-меко правило („песен съвпада, артистът не е написан“)
беше изпробвано и **отрязано** — даваше ~40% лъжливи маркери, защото някои канали
публикуват cover-и под **грешно име на артист** (напр. GZ2H публикува
„Come Out And Play“ с „Billie Eilish“, а song-ът е на The Offspring).

⚠️ Списъците трябва да се прегенерират **след** импорта на партида 20, за да се
появят и 20-те нови Oasis карти:
```powershell
py -3.14 _mark_have.py
py -3.14 _oasis_coverage.py
```

### 9.2 Покритие на Oasis — 56 канонични песни

`_oasis_coverage.md` (генериран от `_oasis_coverage.py`) — **състояние след партида 20**:
* канонични Oasis песни: **56**
* с готова карта: **23** (беше 2 преди партида 20)
* остават: **33**

`_oasis_gap.py` сканира **целия корпус** (50 490 видео), а не само видеата с „Oasis“ в
заглавието — това е причината да се разкрие Stand By Me. Резултат:
* **само 1** от останалите песни има използваемо tab видео в корпуса → Stand By Me (добавен)
* останалите ~26 са **лъжливи съвпадения** („The Turning" → Pink Floyd, „My Big Mouth" →
  Minor Threat, „All Around The World" → Judas Priest, „Party On" → Bloc Party/Deftones)
  или нямат източник → за тях трябва нов източник (виж т. 10)

### 9.3 Източникови канали на партида 20

| канал | handle | channel id | уроци |
|---|---|---|---|
| Lex Guitar Tabs | @LexGuitarTabs | `UCN4wqAJ7UYPnVRGKshckZJQ` | 6 |
| guitar cover with tabs & chords | @guitarcoverwithtab | `UCeWHmkuMBM760nryL8wLfLg` | 8 |
| ike | @Guitar-Jam. | `UCOXYqrNa6diSXKD8wl5EpIA` | 4 |
| Sparky Guitar | @SparkyGuitar | `UCR8OM6seRnlh6bvZinGyyjA` | 3 |

---

## 10. ПАРТИДА 21 — още 6 урока от 5 НОВИ канала (в ход от 19.11 22:30)

Партида 20 доказа, че **измерените 112 канала не са всичко** — за много Oasis песни няма
подходящо видео в тях. `_oasis_search.py` търси в YouTube (`Oasis <песен> guitar tab`) и
намира кандидати в канали, които **не са** в измерения корпус.

### Уроци

| песня | артист | канал | id | out |
|---|---|---|---|---|
| Acquiesce | Oasis | G.S.N. Tabs | `oE6uuH-eKHI` | `out_gz/Oasis-Acquiesce.png` |
| Digsy's Dinner | Oasis | G.S.N. Tabs | `ILwkE8olT7I` | `out_gz/Oasis-Digsy-s-Dinner.png` |
| The Hindu Times | Oasis | Behnam Guitar Tabs | `GwSh_jC4xqY` | `out_gz/Oasis-The-Hindu-Times.png` |
| Who Feels Love? | Oasis | ~~Wayne R Guitar~~ → **Fretboard Fundamentals** | `WPupZKbRTvo` | `out_gz/Oasis-Who-Feels-Love.png` |
| Love Like A Bomb | Oasis | Fretboard Fundamentals | `7Fc5KPnarJo` | `out_gz/Oasis-Love-Like-A-Bomb.png` |
| Instant Karma | John Lennon | Top Guitar Players | `2lc9NwgCwmA` | `out_gz/Oasis-Instant-Karma.png` |

⚠️ „The Hindu Times" и „Who Feels Love?" са **точните имена** на песните (в каноничния списък
`_oasis_songs.py` са записани неточно като „The Hindu" и „Who Feels It") — коригирай при
следваща итерация.

⚠️ **Who Feels Love? смени източника.** Първият избор (`zYP0Npys8s4`, Wayne R Guitar) се оказа
видео **без никаква нотация** — пълно сканиране на 662-те кадра (1 fps) не намери нито TAB,
нито имена на акорди, нито грифни диаграми, нито текстов overlay. Вместо празна карта е
използвана версията от **Fretboard Fundamentals** (`WPupZKbRTvo`) — същия канал и layout като
Love Like A Bomb. Старите spec и PNG са изтрити (recoverable delete).

### Нови канали (добавени в `site_build.py` → `CHANNEL_URLS`)

| канал | channel id | уроци |
|---|---|---|
| G.S.N. Tabs | `UCJ4ZRv0jfD8MmBD1s2CRUPg` | 2 |
| Behnam Guitar Tabs | `UC2JWSXBqH8Ihwy9f5kmHAWw` | 1 |
| Fretboard Fundamentals | `UCFcJJp4uBTXN3_j5kBjNzIw` | 2 |
| Top Guitar Players | `UCpMKt1zAnRPjwpk3RLr439g` | 1 |
| Wayne R Guitar | `UCwTczAeQtEqoSqOc5ouSqwQ` | 0 (източникът е заменен) |

### Състояние

* ✅ манифест `gz_batches/batch21.json` + `batch21_ids.txt` (6 урока)
* ✅ 6/6 видеа свалени в `dl/w4_<ID>.mp4`
* ✅ `B21-BRIEF.md` — бриф за агентите (namespace-и b21a…b21c)
* ✅ 5/6 карти построени и машинно проверени (`_b21_check.py` → 0 проблема):
  Acquiesce=DIAGRAM, Digsy's Dinner=LETTERS, The Hindu Times=LETTERS,
  Love Like A Bomb=LETTERS, Instant Karma=DIAGRAM
* 🔄 Who Feels Love? (новата версия) се строи · 🔄 независим одит на 5-те готови карти
* ⏳ след тях: `chords_diagram_p23.json` → pipeline → 410 + 6 = **416** карти → commit + push

### Важно: видеата не са еднакви по размер

* **G.S.N. Tabs** — 1280×720 (rolling tab strip на `y 360..627`)
* **Wayne R Guitar** — 1280×720
* **Behnam Guitar Tabs**, **Fretboard Fundamentals**, **Top Guitar Players** — 1920×1080

Всички bbox-и са преизмерени в пространството на съответното видео — брифът предполага
1920×1080, но това не важи за всички.

### Важно за `import_cards.py`

`import_cards.py` чете `range(1, 21)` — за партида 21 трябва да стане `range(1, 22)`,
иначе уроците от batch21 няма да се импортират.

### Важно за каналите

`source_channel` в манифеста е точното име на канала, както го връща YouTube
(с водещи/завършващи интервали в някои случаи). То трябва да съвпада с ключа в
`CHANNEL_URLS` на `site_build.py`, иначе каналът няма линк в сайта.
