# PLAYBOOK — GuitarZero2HeroExpress tab cards

Workspace: `D:\MiniMax Code Repos\Guitar Lessons`

## Goal
For each assigned song, produce ONE card image in `out_gz/` containing the TAB
sheet (and any chord pattern / strumming pattern) EXTRACTED DIRECTLY FROM THE VIDEO,
plus a link to the video.

**Reference card (already done — read it and match it):**
`out_gz/3-Doors-Down-Here-Without-You.png`

## The channel's on-screen layout (1920x1080 landscape, consistent across videos)

```
x=0..260      vertical fretboard chord diagram (wooden)  -- usually skip it
y=0..560      the guitarist / song title top-right
y=558..1078   THE TAB SHEET PANEL  <-- this is what we want
                y=558..620   dark-red header bar: VERSE / CHORUS / BRIDGE / INTRO
                y=620..1078  white sheet: 6-line TAB notation (TAB / A / B strings),
                            fret numbers, chord names above, strum symbols below
```

Some sections show chord names + a "STRUMMING PATTERN" line instead of tab staff
(that is the BRIDGE/INTRO style). Capture whichever the video shows.

**Default crop for the tab panel (verified):**
```
ffmpeg -y -v error -ss <sec> -i <video> -frames:v 1 -vf "crop=1658:520:262:558" out.png
```
Adjust if the layout differs (some videos may be a different resolution — check with
`ffprobe`). Verify every crop by reading it with the `read` tool.

## Tooling (verified working)
- `py -3.14` (Python 3.14, Pillow installed)
- `py -3.14 -m yt_dlp` — yt-dlp 2026.10.26
- bgutil PO-Token server ALREADY RUNNING on http://127.0.0.1:4416
- `ffmpeg` / `ffprobe` on PATH
- `survey.py` builds a labeled frame montage; `montage.py` tiles a folder of PNGs

Download a video (1080p):
```
py -3.14 -m yt_dlp --no-warnings --extractor-args "youtube:player_client=android_creator" -f "137/best" --no-part -o "dl/gz_%(id)s.%(ext)s" "https://www.youtube.com/watch?v=<ID>"
```
If it fails, wait ~10s and retry — YouTube throttles bursts. ALWAYS download to
`dl/gz_<ID>.mp4` (the `gz_` prefix is yours; do not touch `dl/v_*`).

## Workflow per song

1. **Download** the video to `dl/gz_<ID>.mp4`.
2. **Survey** to find the moments:
   ```
   py -3.14 survey.py dl/gz_<ID>.mp4 frames/gz_<ID> 10
   ```
   → `frames/gz_<ID>_montage.png` with `t=<sec>` labels. Read it with the `read` tool.
   The montage label `t=<sec>` equals frame index × interval. If you need an exact
   second, extract it directly:
   ```
   ffmpeg -y -v error -ss <sec> -i dl/gz_<ID>.mp4 -frames:v 1 "frames/gz_<ID>/k<sec>.png"
   ```
   You want at least: one VERSE tab sheet, one CHORUS tab sheet, and one section
   with the strumming pattern if it exists.
3. **Crop** each section from the full-res frame (see default crop above), then READ
   each crop to confirm: complete notation, nothing cut off, section header visible.
   Iterate until clean.
4. **Compose** using the shared helper:
   ```python
   from card import make_card
   make_card(
       '<VIDEO_ID>',
       '<SONG IN CAPS>',
       '<ARTIST>  ·  Guitar Cover  ·  <TAG>  ·  GuitarZero2HeroExpress',
       [('TAB  ·  VERSE',  ['frames/gz_<ID>/c_verse.png']),
        ('TAB  ·  CHORUS', ['frames/gz_<ID>/c_chorus.png']),
        ('CHORD PATTERN & STRUMMING  ·  BRIDGE', ['frames/gz_<ID>/c_bridge.png'])],
       note='Chords: ...   Strumming: ...',
       out_name='<Artist-Song>.png',
   )
   ```
   `card.py` / `compose_lib.py` write into `out/`. **These two files hard-code the
   output folder `out/` and the footer label `BernadetteTeachesMusic`.** For this
   channel you need `out_gz/` and the label `GuitarZero2HeroExpress`.
   Write your own private copy (e.g. `gz_card.py`, `gz_compose.py`) based on them and
   DO NOT edit the shared `card.py` / `compose_lib.py` / `survey.py` / `montage.py` —
   three other agents are using them concurrently.
   Note `compose_lib.build()` now accepts `source='GuitarZero2HeroExpress'` for the
   footer label, and `out_name=` controls the filename.
5. **Verify** by reading the produced PNG with the `read` tool: tab notation legible,
   no clipped edges, no stray black bars, title/subtitle fit, correct URL.

## Rules
- Every crop must come from a real frame of the real video. NEVER invent tablature,
  chord names, chord progressions or strumming patterns. If the video shows no
  strumming pattern, OMIT that section.
- Keep the exact output path from the batch manifest — the manifest `out` field is
  the required filename.
- If a video cannot be downloaded, or shows no tab sheet at all, still report it
  clearly instead of producing an empty card.
- Song titles in CAPS for the card title. Keep apostrophes and special characters.

## Report back
Per song: output path, the section names you captured, the chords / strumming pattern
text you read from the screen, the timestamps used, and anything you could not find.
