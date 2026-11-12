import os, sys, glob
from PIL import Image, ImageDraw

src_dir = sys.argv[1]
out = sys.argv[2]
cols = int(sys.argv[3]) if len(sys.argv) > 3 else 8
step = float(sys.argv[4]) if len(sys.argv) > 4 else 8.0

files = sorted(glob.glob(os.path.join(src_dir, '*.png')))
TW, TH = 320, 200
LAB = 22
rows = (len(files) + cols - 1) // cols
canvas = Image.new('RGB', (cols * TW, rows * (TH + LAB)), (20, 20, 20))
d = ImageDraw.Draw(canvas)
for i, f in enumerate(files):
    im = Image.open(f).convert('RGB').resize((TW, TH))
    x = (i % cols) * TW
    y = (i // cols) * (TH + LAB)
    canvas.paste(im, (x, y))
    d.rectangle([x, y + TH, x + TW, y + TH + LAB], fill=(0, 0, 0))
    d.text((x + 5, y + TH + 4), '%.0fs' % (i * step), fill=(255, 220, 0))
canvas.save(out)
print('saved', out, canvas.size, 'frames', len(files))
