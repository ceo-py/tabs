"""Private make_card for my batch: same contract as card.make_card but uses
compose_rock.build (subtitle auto-shrink). Shared card.py is NOT modified.
"""
import os
from PIL import Image
from compose_rock import build

OUT_DIR = 'out'


def make_card(video_id, title, subtitle, sections, note, out_name=None):
    """sections: list of (label, [crop_png_path, ...])"""
    url = 'https://www.youtube.com/watch?v=' + video_id
    secs = []
    for label, paths in sections:
        imgs = [Image.open(p).convert('RGB') for p in paths]
        secs.append((label, imgs))
    out = os.path.join(OUT_DIR, out_name)
    build(out, title, subtitle, secs, url, note=note, min_width=1400)
    return out
