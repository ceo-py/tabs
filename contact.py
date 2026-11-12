import glob, os
from PIL import Image, ImageDraw, ImageFont

files = sorted(glob.glob('out/*.png'))
TW = 380
COLS = 4
fnt = ImageFont.truetype(r'C:\Windows\Fonts\arialbd.ttf', 16)

# first pass: compute row heights
thumbs = []
for f in files:
    im = Image.open(f).convert('RGB')
    h = int(im.height * TW / im.width)
    thumbs.append((f, im.resize((TW, h)), h))

rows = [thumbs[i:i + COLS] for i in range(0, len(thumbs), COLS)]
row_h = [max(t[2] for t in r) + 26 for r in rows]

W = COLS * (TW + 12) + 12
H = sum(row_h) + 12
canvas = Image.new('RGB', (W, H), (12, 12, 20))
d = ImageDraw.Draw(canvas)

y = 12
for r, rh in zip(rows, row_h):
    x = 12
    for f, im, h in r:
        canvas.paste(im, (x, y))
        d.text((x + 3, y + h + 4), os.path.basename(f)[:-4][:46], font=fnt, fill=(255, 210, 80))
        x += TW + 12
    y += rh

canvas.save('out/_contact_sheet.png')
print('saved out/_contact_sheet.png', canvas.size, len(files), 'cards')
