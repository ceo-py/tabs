"""Build a guitar lesson card from cropped frames of a YouTube tutorial.

Usage (from compose_lib import build):
    build(out_path, title, subtitle, [(label, [Image,...]), ...], url, note=...)

Crops must be taken from the ORIGINAL 1080p frames with ffmpeg, e.g.
    ffmpeg -y -v error -ss <sec> -i <video> -frames:v 1 -vf "crop=W:H:X:Y" out.png
"""
import os
from PIL import Image
from compose_lib import build

OUT_DIR = 'out'
os.makedirs(OUT_DIR, exist_ok=True)


def make_card(video_id, title, subtitle, sections, note, out_name=None):
    """sections: list of (label, [crop_png_path, ...])"""
    url = 'https://www.youtube.com/watch?v=' + video_id
    secs = []
    for label, paths in sections:
        imgs = [Image.open(p).convert('RGB') for p in paths]
        secs.append((label, imgs))
    out = os.path.join(OUT_DIR, out_name or (out_name_from(title) + '.png'))
    build(out, title, subtitle, secs, url, note=note, min_width=1400)
    return out


def out_name_from(title):
    s = ''.join(c if c.isalnum() or c in ' -' else '' for c in title)
    return '-'.join(s.split()).strip('-')
