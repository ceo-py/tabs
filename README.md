# TABS 90 — guitar lesson cards with TAB notation

A mobile-friendly website that collects **guitar lesson cards**: TAB notation,
chord shapes, chord progressions and strumming patterns, all extracted
straight from YouTube video frames — nothing reconstructed.

Live site: **https://tabs.ceo-py.eu**

```
https://tabs.ceo-py.eu/
├── index.html        markup
├── style.css         90s MTV look — neon, chrome logo, CRT overlay
├── app.js            search, filters, lightbox, embedded YouTube player
├── data/songs.json   generated manifest
├── cards/*.webp      full lesson cards
└── thumbs/*.webp     4:5 previews
```

Opening a card shows the **YouTube video embedded on top** and the full TAB
sheet below it; the player scrolls away with the content so the notation gets
the whole screen.

Currently **72 songs** (50 from GuitarZero2HeroExpress, 22 from
BernadetteTeachesMusic), 41 of them rock.

---

## Repo layout

| Path | What it is |
|---|---|
| `site/` | the deployable website (served by Caddy) |
| `songs.json` | **source of truth** — one object per song |
| `out_gz/`, `out/` | source lesson cards (PNG) produced by the card agents |
| `import_cards.py` | merges new cards into `songs.json` |
| `add_song.py` | adds a single song by hand |
| `site_build.py` | `songs.json` → webp assets + served manifest |
| `build_dist.py` | all of the above + `dist/tabs90-site.zip` |
| `gz_batches/` | the song batches (artist, song, technique tag, video id) |
| `PLAYBOOK*.md` | how the cards are produced from video frames |

## Updating the site

New cards landed in `out_gz/` (or `out/`):

```powershell
py -3.14 build_dist.py
```

That merges the new songs into `songs.json`, regenerates every asset and
writes `dist/tabs90-site.zip`.

A single song by hand:

```powershell
py -3.14 add_song.py --png out_gz/Some-Song.png --artist "Artist" --title "Song" --url https://youtu.be/XXXX
```

Editing metadata: open `songs.json`, change `title` / `artist` / `tag` /
`rock` / `url`, then run `py -3.14 site_build.py`.

## Deployment

The VPS pulls this repo and syncs `site/` into the web root. See
[DEPLOY.md](DEPLOY.md) for the Caddy setup and the details.

## How the cards are made

Every symbol on a card is a real frame from the video. The agents locate the
TAB panel, read the section headers off the footage, crop each section and
composite it. Videos that show no TAB staff get a chord-only card — the
absence is shown honestly instead of being invented.

## License

MIT — see [LICENSE](LICENSE). The cards reproduce excerpts from third-party
YouTube videos for private study use; the original recordings belong to their
respective owners and channels.
