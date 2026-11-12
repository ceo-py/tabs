# PLAYBOOK — extracting guitar chords + strumming cards from BernadetteTeachesMusic

Workspace: `D:\MiniMax Code Repos\Guitar Lessons`

## Goal
For each assigned YouTube tutorial, produce ONE card image in `out/` that contains the
chord/tab diagrams and the strumming pattern EXTRACTED DIRECTLY FROM THE VIDEO
(screenshots of the on-screen graphics), plus the link to the video.

Two cards already exist as reference for style and quality:
- `out/Hotel-California.png`
- `out/Sweet-Child-O-Mine.png`

Open them with the `read` tool and match their visual quality.

## Available tooling (verified working — use exactly these)
- `py -3.14` (Python 3.14) with Pillow installed
- `py -3.14 -m yt_dlp` — yt-dlp 2026.10.26
- A bgutil PO-Token server is ALREADY RUNNING on http://127.0.0.1:4416.
- `ffmpeg` / `ffprobe` on PATH.

Download a video (1080p):
```
py -3.14 -m yt_dlp --no-warnings --extractor-args "youtube:player_client=android_creator" -f "137/best" --no-part -o "dl/v_<ID>.%(ext)s" "https://www.youtube.com/watch?v=<ID>"
```
If it fails, wait ~10s and retry (YouTube throttles bursts). Add `--extractor-args "youtube:player_client=android"` as a fallback.
The file lands at `dl/v_<ID>.mp4`.

## Workflow per video

### 1. Survey
```
py -3.14 survey.py dl/v_<ID>.mp4 frames/sv_<ID> <interval_seconds>
```
→ writes `frames/sv_<ID>_montage.png` (labeled with `t=<sec>` and frame index).

Use interval 15–30s for long videos (10–15s for shorts). Read the montage with the
`read` tool. Identify the frames that show:
  - the CHORD DIAGRAMS (fretboard grids with chord names)
  - the STRUMMING PATTERN (text like "Strum: D D U U D" or "D DU UDU")
  - optionally the CHORD PATTERN (letters like "D D C C / G G D D")

NOTE: montage labels are `t=<sec>` for that frame. BUT the frame index `f_NNNN` maps to
`N * interval` seconds. If you need a specific timestamp, extract it directly:
```
ffmpeg -y -v error -ss <sec> -i dl/v_<ID>.mp4 -frames:v 1 "frames/sv_<ID>/key_<sec>.png"
```

### 2. Zoom in
Once you know which region of the frame holds the chords/strum, crop a REGION of the
survey montage to see it clearly, or better: extract the full-res frame and crop it:
```
ffmpeg -y -v error -ss <sec> -i dl/v_<ID>.mp4 -frames:v 1 -vf "crop=W:H:X:Y" "frames/sv_<ID>/c_<name>.png"
```
then read the crop with the `read` tool to verify it is complete (nothing cut off,
nothing irrelevant). W/H/X/Y are in SOURCE pixels (1920x1080 for landscape videos,
1080x1920 for vertical Shorts).

Iterate on the crop until it is clean. Typical problems: a black column on the right
(the video is 1920 wide but only x<1916 has content), a guitar headstock intruding at
the bottom, or text cut in half. Trim those out.

### 3. Compose the card
Write a small script that imports the shared helpers:
```python
from card import make_card
make_card(
    '<VIDEO_ID>',
    '<TITLE IN CAPS>',
    '<SUBTITLE>',
    [('CHORDS', ['frames/sv_<ID>/c_chords1.png']),
     ('CHORD PATTERN', ['frames/sv_<ID>/c_pattern.png']),
     ('STRUMMING PATTERN', ['frames/sv_<ID>/c_strum.png'])],
    note='Chords: ...   Verse: ...   Chorus: ...',
)
```
- `card.py` uses `compose_lib.build(...)`. DO NOT EDIT `card.py`, `compose_lib.py` or
  `survey.py` — they are shared with other agents working in parallel. If you need a
  tweak, write your own copy with a different filename.
- Sections are rendered in order, each as a labeled row; multiple images in one
  section sit side by side.
- Include ONLY sections whose content you actually found in the video. Never invent
  chord charts, strumming patterns or chord progressions. If the video shows no
  strumming pattern, omit the STRUMMING PATTERN section rather than guessing.
- The `note` line is plain text summarising what is on screen (chords, patterns).

### 4. Verify
Read the produced PNG with the `read` tool. Check:
  - title fits (auto-shrink works, but verify nothing is clipped)
  - every crop is complete and legible — chord finger positions must be readable
  - no stray black bars, no cut-off text, no guitar headstock
  - the link at the bottom is correct
Fix and re-render until it is right.

## Titles
- Title: song name in CAPS, e.g. `YELLOW`, `HOTEL CALIFORNIA`,
  `"SWEET CHILD O' MINE"` (keep the quotes inside the string).
- Subtitle: `<ARTIST>  ·  <subtitle from the video title>  ·  Bernadette Teaches Music`
- Output file name: `<Artist-Song>.png` in `out/`, e.g. `Eagles-Hotel-California.png`,
  `Coldplay-Yellow.png`. Use the `make_card` `out_name` argument if you need a
  specific name — otherwise it is derived from the title.

## Deliverable report
Return, per video:
- output file path
- the exact chords / chord pattern / strumming pattern text you read from the video
- any timestamp used
- anything you could NOT find (e.g. "this tutorial shows no strumming pattern")
