# TABS 90 — състояние на проекта

Последна актуализация: **12 ноември 2026, 19:00** (commit `8825d10` е последният в GitHub; картите по-долу още не са комитнати)

---

## 1. Какво е готово и публикувано

| Слой | Състояние |
|---|---|
| Жив сайт | <https://tabs.ceo-py.eu/> — 72 карти, 2 канала, легенда на акордите |
| Локален preview | http://127.0.0.1:8765/ (от телефон: http://192.168.0.206:8765/) — отделян процес, не умира с тайм-аута |
| Репо | `github.com/ceo-py/tabs`, branch `main`, авто-деплой на VPS-а на всеки 5 мин |
| Карти в архива | `out/` (22 карти на Bernadette) + `out_gz/` (114 карти на GuitarZero) |

### Функционалност на сайта
- Рендер на каталог от JSON манифест, търсене, чипове по канал/рок
- Lightbox: YouTube embed, карта на цялата ширина, само ✕ горе вдясно, затварянето връща при картата
- Лента **CHORD SHAPES** под картата — SVG грифни диаграми, само за картите с букви (без вече налични грифни диаграми)
- Cache busting с `?v=<hash>` на всеки URL (Cloudflare кешира по URL)
- Пейзаж режим, оптимизиран скрол (без `mix-blend-mode` / `backdrop-filter` / `drop-shadow`)

---

## 2. Втора вълна: следващите 100 песни (в момента тече)

Източник: `gz_tabs_all.json` (606 песни с табове от GuitarZero2HeroExpress).
Партидите 1–4 = първите 50 (готови). **Партидите 5–8 = следващите 100** (тече).

| Партида | Песни | Съдържание | Карти готови |
|---|---|---|---|
| 5 | 25 | Billy Joel, Bing Crosby, Blink-182, Bob Dylan, Bob Marley, Bon Iver, Bon Jovi, Boston, Boyce Avenue, Bradley Cooper, Brenda Lee, Bring Me The Horizon, Bruno Mars | **25/25 ✅** |
| 6 | 25 | Bruno Mars, BTS, Bush, Cage The Elephant, Calum Scott, Cat Stevens, Charlie Puth, Chris Cornell, Chris Isaak, Chris Stapleton, Christmas, Chuck Berry, Clean Bandit, Clinton Kane, Coldplay ×5 | 8/25 ⏳ |
| 7 | 25 | Coldplay, Collective Soul, Conan Gray, Creed, CCR, Crowded House, Damien Rice, Dan, Daniel Caesar, Danny Vera, Darius Rucker, Dashboard Confessional, Dave Matthews, David Bowie, Dean Lewis, Death Cab, Dolly Parton | 6/25 ⏳ |
| 8 | 25 | Ed Sheeran ×25 | **25/25 ✅** |

**Общо готови: 64 от 100.**

### Активни агенти (4 слота, лимитът е 4)
| Агент | Задача | Статус |
|---|---|---|
| `bg_f5cff672` | карти, партида 6 | тече |
| `bg_4f6c16e9` | карти, партида 7 | тече |
| `bg_dddf9bb7` | класификация DIAGRAM/LETTERS, партида 8 | тече |
| — | карти, партида 5 | приключи (25/25) |
| — | класификация, партида 5 | приключи (23 LETTERS, 1 DIAGRAM, 1 NONE) |

> Агентът за партида 5 докладва: 25/25 карти, 0 неуспешни видеа, всеки crop проверен визуално,
> programmatичен audit за празни панели и за бележки над 2 реда (композиторът реже 3-тия).
> Класификация: `Bon-Iver-Skinny-Love.png` = DIAGRAM (има C диаграма в горната 40%),
> `Blink182-Adams-Song.png` = NONE (само TAB), останалите 23 = LETTERS.

---

## 3. Какво да се направи, когато приключат

```powershell
# 1. нови карти -> songs.json
py -3.14 import_cards.py

# 2. акордите за новите карти (note полетата от b5..b8 build скриптовете и spec папките)
py -3.14 chord_extract.py

# 3. класификация DIAGRAM/LETTERS -> chords_has_diagram.json
py -3.14 merge_chord_diagrams.py

# 4. речникът с формите (87) — добави новите акорди, ако има непокрити
py -3.14 chord_shapes.py

# 5. пълен билд + zip
py -3.14 build_dist.py

# 6. commit + push (VPS-ът се обновява сам за 5 мин)
git add -A ; git commit -m "..." ; git push origin main
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
