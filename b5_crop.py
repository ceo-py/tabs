"""Crop a region out of a saved full-res survey frame (lossless, no re-encode).

Usage: py -3.14 b5_crop.py <src_frame.png> <out.png> W:H:X:Y
"""
import sys, os
from PIL import Image

src, out = sys.argv[1], sys.argv[2]
os.makedirs(os.path.dirname(out) or '.', exist_ok=True)
w, h, x, y = [int(v) for v in sys.argv[3].split(':')]
scale = float(sys.argv[4]) if len(sys.argv) > 4 else 1.0
im = Image.open(src).convert('RGB')
sw, sh = im.size
x = max(0, min(x, sw - 1)); y = max(0, min(y, sh - 1))
w = min(w, sw - x); h = min(h, sh - y)
out_im = im.crop((x, y, x + w, y + h))
if scale != 1.0:
    out_im = out_im.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
out_im.save(out)
print('saved', out, out_im.size, 'from', src)
