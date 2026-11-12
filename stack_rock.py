"""Stack cropped strips vertically (helper for my own batch)."""
import sys
from PIL import Image

out = sys.argv[1]
ims = [Image.open(p).convert('RGB') for p in sys.argv[2:]]
w = max(i.size[0] for i in ims)
h = sum(i.size[1] for i in ims)
canvas = Image.new('RGB', (w, h), (0, 0, 0))
y = 0
for i in ims:
    canvas.paste(i, (0, y))
    y += i.size[1]
canvas.save(out)
print('saved', out, canvas.size)
