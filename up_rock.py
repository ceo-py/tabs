"""Upscale cropped chord-diagram regions for legibility (LANCZOS)."""
import sys
from PIL import Image

for spec in sys.argv[1:]:
    path, factor = spec.rsplit('@', 1)
    im = Image.open(path).convert('RGB')
    w, h = im.size
    im = im.resize((int(w * float(factor)), int(h * float(factor))), Image.LANCZOS)
    im.save(path)
    print('up', path, im.size)
