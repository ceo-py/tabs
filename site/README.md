# TABS 90 — static site

Mobile-friendly gallery of guitar lesson cards (TAB notation, chord pattern,
strumming pattern) with an embedded YouTube player on top of every card.

Everything is static: plain HTML + CSS + JavaScript, no framework, no build
tool, no database, no server-side code. The folder `site/` is the deployable
artefact — copy it anywhere that serves static files.

```
site/
  index.html        markup
  style.css         90s MTV look (neon, chrome logo, CRT overlay, checkerboard)
  app.js            rendering, search, filters, lightbox, YouTube player
  data/songs.json   generated manifest (do not hand-edit)
  cards/*.webp      full lesson cards
  thumbs/*.webp     4:5 previews
```

---

## Adding a song

There is **one source of truth**: `songs.json` (repo root). Everything else is
generated from it.

### 1. A new batch of cards finished (agents working in `out_gz/`)

```powershell
py -3.14 import_cards.py      # merge new cards into songs.json
py -3.14 site_build.py         # regenerate webp assets + site/data/songs.json
```

`import_cards.py` only *adds* entries that are missing, so hand-edited titles
or flags in `songs.json` survive. Use `--force` to overwrite existing metadata.

### 2. One single song, by hand

```powershell
py -3.14 add_song.py --png out_gz/Adele-Someone-Like-You.png `
    --artist "Adele" --title "Someone Like You" `
    --url https://www.youtube.com/watch?v=mjwqrQkMLpQ
```

This copies the card, generates the preview, and appends the entry to
`songs.json`. Then run `site_build.py` to refresh the served manifest.

### 3. Editing metadata

Open `songs.json` and change `title`, `artist`, `tag`, `rock`, `url` — then run
`site_build.py`. The file is plain JSON, one object per song:

```json
{
  "id": "mjwqrQkMLpQ",
  "title": "Someone Like You",
  "artist": "Adele",
  "tag": "Tabs + Chords",
  "rock": false,
  "channel": "GuitarZero2HeroExpress",
  "url": "https://www.youtube.com/watch?v=mjwqrQkMLpQ",
  "card": "out_gz/Adele-Someone-Like-You.png"
}
```

`card` is the path of the source PNG relative to the repo root. `site_build.py`
converts it to `site/cards/<name>.webp` + `site/thumbs/<name>.webp`.

---

## Running it locally

```powershell
Set-Location site
py -3.14 -m http.server 8765 --bind 0.0.0.0
```

- this computer: <http://127.0.0.1:8765/>
- phone / other device on the same Wi-Fi: `http://<LAN-IP>:8765/`

---

## Publishing later

The `site/` folder is standalone. Any static host works:

- **Vercel / Netlify** — connect the repo, build command `py -3.14 site_build.py`
  (or a no-build deploy of `site/`), output directory `site`. Every `git push`
  then republishes automatically.
- **GitHub Pages** — push `site/` to a `gh-pages` branch.
- **Netlify Drop / any static bucket** — drag the `site/` folder in.

If you want the site to rebuild itself on every push, add a CI step that runs:

```bash
python import_cards.py
python site_build.py
```

before the deploy step.

> Note: the YouTube embeds respect the uploader's embedding settings. If a
> video refuses to play inside the player, the card still shows the full tab
> sheet and the **OPEN ON YOUTUBE** button opens it directly.

---

## Editing the design

- `site/style.css` — all colours/spacing live here. The palette is at the top
  of the file (`--pink`, `--cyan`, `--yellow`, `--green`, `--violet`).
- `site/app.js` — search, filters and the lightbox.
- `site/index.html` — text and structure.
