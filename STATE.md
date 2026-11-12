# TABS 90 — състояние на проекта

**ПАУЗА — 12 ноември 2026, 19:20.** Агентите са спрени, всичко е комитнато и на живия сайт.
Продължаваме от тук, когато е удобно.

---

## 1. Какво е готово и публикувано

| Слой | Състояние |
|---|---|
| Жив сайт | <https://tabs.ceo-py.eu/> — **143 карти**, 2 канала, 67 rock, легенда на акордите |
| Локален preview | http://127.0.0.1:8765/ — изключен при паузата (стартира се с `Start-Process`, виж т. 6) |
| Репо | `github.com/ceo-py/tabs`, branch `main`, авто-деплой на VPS-а на всеки 5 мин |
| Карти в архива | `out/` (22 карти на Bernadette) + `out_gz/` (121 карти на GuitarZero) |
| Легенда на акордите | 112 форми в речника; 0 неразрешени акорда |

### Функционалност на сайта
- Рендер на каталог от JSON манифест, търсене, чипове по канал/рок
- Lightbox: YouTube embed, карта на цялата ширина, само ✕ горе вдясно, затварянето връща при картата
- Лента **CHORD SHAPES** под картата — SVG грифни диаграми, само за картите с букви (без вече налични грифни диаграми)
- Cache busting с `?v=<hash>` на всеки URL (Cloudflare кешира по URL)
- Пейзаж режим, оптимизиран скрол (без `mix-blend-mode` / `backdrop-filter` / `drop-shadow`)

---

## 2. Втора вълна: следващите 100 песни

Източник: `gz_tabs_all.json` (606 песни с табове от GuitarZero2HeroExpress).
Партидите 1–4 = първите 50 (готови). **Партидите 5–8 = следващите 100.**

| Партида | Песни | Карти готови | Класификация |
|---|---|---|---|
| 5 | 25 | **25/25 ✅** | 23 LETTERS, 1 DIAGRAM, 1 NONE ✅ |
| 6 | 25 | **11/25 ⏸** | ❌ не е правена |
| 7 | 25 | **10/25 ⏸** | ❌ не е правена |
| 8 | 25 | **25/25 ✅** | 23 LETTERS, 2 NONE ✅ |

**Публикувани са 71 от 100. Остават 29 карти (партида 6: 14, партида 7: 15).**

### Какво остава за партида 6 (14 песни)
`How Long` · `Nothing Compares 2 U` · `Wicked Game` · `Tennessee Whiskey` · `O Holy Night` ·
`The First Noel` · `Johnny B. Goode` · `Symphony` · `Chicken Tendies` · `Don't Panic` ·
`Green Eyes` · `In My Place` · `Sky Full Of Stars` · `Sparks`

### Какво остава за партида 7 (15 песни)
`Better Be Home Soon` · `Fall At Your Feet Acoustic` · `Cannonball` · `10000 Hours` ·
`Tequila` · `Best Part` · `Roller Coaster` · `Wagon Wheel` · `Hands Down` ·
`Crash Into Me` · `Starman` · `Be Alright` · `Stay Awake` ·
`I Will Follow You Into The Dark` · `Jolene`

> Видеата за всички 100 песни вече са свалени в `dl/` — при нова пуск не е нужно да се тегли отново.
> Агентът за партида 5 докладва 25/25 карти, 0 неуспешни видеа, programmatичен audit за празни панели
> и за бележки над 2 реда (композиторът реже 3-тия ред).
> Класификацията обхваща 122 карти: 97 LETTERS, 21 DIAGRAM, 4 NONE.
> `Bon-Iver-Skinny-Love` е DIAGRAM (има C диаграма в горната 40% — crop-ът я пропуска).
> `Blink182-Adams-Song`, `Ed-Sheeran-Bloodstream`, `Ed-Sheeran-Lego-House` са NONE (само TAB).

---

## 3. Как да продължим (следващата сесия)

### 3.1 Да довършим картите (2 агента, по ~15 песни)
Стартирай 2 worker агента:
- агент А → партида 6, само останалите 14 песни
- агент Б → партида 7, само останалите 15 песни

Рецептата е същата като преди (виж `PLAYBOOK-GZ.md` / prompt-а в историята на сесията):
`dl/v_<ID>.mp4` → `py -3.14 survey.py` → ffmpeg crop → `bN_compose.make_card(...)` → PNG в `out_gz/`.
**За всеки агент е нужна собствена копия на композитора** — напр. `b6_compose.py` вече съществува,
за `b7` също; ако се прави нова партида, копирай `b2_compose.py` → `bN_compose.py`.

### 3.2 Класификация DIAGRAM/LETTERS за партиди 6 и 7
Два агента по 25 карти:
- генерирай crop-ове: `py -3.14 make_crops2.py 6 7` → `dbg_crops2/<slug>.png`
- всеки агент чете crop-а И пълната карта (диаграмата може да е в горните 40%!) и пише
  `chords_diagram_p6.json` / `chords_diagram_p7.json`
- семантика: `DIAGRAM` = има грифна мрежа с точки; `LETTERS` = само букви; `NONE` = няма имена на акорди

### 3.3 Публикуване
```powershell
py -3.14 import_cards.py        # нови карти -> songs.json
py -3.14 chord_extract.py       # акорди (note полетата от b5..b8 скриптовете и spec папките)
py -3.14 merge_chord_diagrams.py # p1..p7 -> chords_has_diagram.json
py -3.14 chord_shapes.py        # -> chord_shapes.json (112 форми в момента)
py -3.14 build_dist.py          # пълен билд + dist/tabs90-site.zip
git add -A ; git commit -m "..." ; git push origin main   # VPS-ът се обновява сам за 5 мин
```

**Проверка на покритието на формите** (трябва да е 0 неразрешени):
```powershell
py -3.14 -c "
import json,os,re
R='.'
shapes=json.load(open('chord_shapes.json',encoding='utf-8'))
chords=json.load(open('chords.json',encoding='utf-8'))
cls=json.load(open('chords_has_diagram.json',encoding='utf-8'))
names=set(shapes)
def base(n):
    if n in names and shapes[n].get('frets'): return n
    m=re.match(r'^(.+?)\(([^)]+)\)$',n)
    if m and m.group(1) in names: return m.group(1)
    if '/' in n and n.split('/')[0] in names: return n.split('/')[0]
    return None
miss={c for card,ch in chords.items() if cls.get(card)!='DIAGRAM' for c in ch if base(c) is None}
print('unresolved:',miss)"
```

### 3.4 Ако се появи нов акорд без форма
```powershell
py -3.14 chord_voicings.py <акорд>     # намира изиграема позиция по грифа
```
После добави формата в `chord_shapes.py` (SHAPES или SLASH) и повтори `chord_shapes.py`.

---

## 4. Важни правила на проекта

- **Съдържанието идва само от кадрите на видеото** — никога да не се реконструират акорди, прогресии или
  удари по струните. Ако видеото не показва strumming pattern, разделът се пропуска.
- Споделените помощни файлове (`card.py`, `compose_lib.py`, `survey.py`, `montage.py`, `PLAYBOOK.md`,
  `PLAYBOOK-GZ.md`) **не се редактират**. За нова партида се прави копия: `bN_compose.py` + `bN_build.py`.
- Архивът (`out/`, `out_gz/`) е непокътнат; линкът към видеото се маха **само в сайт асетите**
  (`strip_link.py` вътре в `site_build.py`).
- `songs.json` е единственият източник на истина; `import_cards.py` пази ръчните редакции.
- Caddy: `restart`, не `reload` (`admin off`); конфиг в `/etc/caddy/caddy.d/tabs.conf`,
  source-of-truth в репото `deploy/tabs.conf`. Sudo изисква парола → потребителят.
- Изтриване само през recoverable delete: `rm -- "<path>"` (самоцелна команда).
- Git: `git -C <path>`; не се прави `git add` след `Set-Location`.

---

## 5. Помощни скриптове

| файл | роля |
|---|---|
| `gz_make_batches2.py` | генерира партиди 5–8 от каталога |
| `make_crops2.py` | crop-ове (долна 60%) на картите за класификация |
| `merge_chord_diagrams.py` | обединява `chords_diagram_p*.json` → `chords_has_diagram.json` |
| `chord_extract.py` | вади акордите от `note` полетата (включително `b5_spec/`…`b8_spec/`) |
| `chord_shapes.py` | речникът с формите на акордите (112) |
| `chord_voicings.py` | намира изиграема позиция за произволен акорд |
| `strip_link.py` | маха линка към видеото от футъра (само в сайт асетите) |

## 6. Deployment и локален сървър

```powershell
# локален preview (отделен процес, не умира с тайм-аута на задачата)
Start-Process -FilePath 'py' -ArgumentList '-3.14','-m','http.server','8765','--bind','0.0.0.0' `
  -WorkingDirectory 'D:\MiniMax Code Repos\Guitar Lessons\site' -WindowStyle Hidden

# ръчен деплой на VPS-а
. 'D:\MiniMax Code Repos\Guitar Lessons\remote.ps1'
Invoke-Remote '/home/ceo/production/tabs-deploy.sh && tail -3 /home/ceo/production/deploy.log'
```
VPS: `/home/ceo/production/tabs/` = web root, `/home/ceo/production/tabs-repo/` = clone,
`tabs-deploy.sh` = pull + sync, user crontab `*/5 * * * *`.

---

## 4. Важни правила на проекта

- **Съдържанието идва само от кадрите на видеото** — никога да не се реконструират акорди, прогресии или
  удари по струните. Ако видеото не показва strumming pattern, разделът се пропуска.
- Споделените помощни файлове (`card.py`, `compose_lib.py`, `survey.py`, `montage.py`, `PLAYBOOK.md`,
  `PLAYBOOK-GZ.md`) **не се редактират**. За нова партида се прави копия: `bN_compose.py` + `bN_build.py`.
- Архивът (`out/`, `out_gz/`) е непокътнат; линкът към видеото се маха **само в сайт асетите**
  (`strip_link.py` вътре в `site_build.py`).
- `songs.json` е единственият източник на истина; `import_cards.py` пази ръчните редакции.
- Caddy: `restart`, не `reload` (`admin off`); конфиг в `/etc/caddy/caddy.d/tabs.conf`,
  source-of-truth в репото `deploy/tabs.conf`. Sudo изисква парола → потребителят.
- Изтриване само през recoverable delete: `rm -- "<path>"` (самоцелна команда).
- Git: `git -C <path>`; не се прави `git add` след `Set-Location`.

---

## 5. Помощни скриптове (нови)

| файл | роля |
|---|---|
| `gz_make_batches2.py` | генерира партиди 5–8 от каталога |
| `make_crops2.py` | crop-ове (долна 60%) на новите карти за класификация |
| `merge_chord_diagrams.py` | обединява `chords_diagram_p*.json` → `chords_has_diagram.json` |
| `chord_extract.py` | вади акордите от `note` полетата (включително `b5_spec/`…`b8_spec/`) |
| `chord_shapes.py` | речникът с формите на акордите |
| `strip_link.py` | маха линка към видеото от футъра (само в сайт асетите) |

## 6. Deployment

```powershell
. 'D:\MiniMax Code Repos\Guitar Lessons\remote.ps1'
Invoke-Remote '/home/ceo/production/tabs-deploy.sh && tail -3 /home/ceo/production/deploy.log'
```
VPS: `/home/ceo/production/tabs/` = web root, `/home/ceo/production/tabs-repo/` = clone,
`tabs-deploy.sh` = pull + sync, user crontab `*/5 * * * *`.
