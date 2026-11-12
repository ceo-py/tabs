"""Check how many lines a note will occupy in a card of a given width."""
import sys

from PIL import ImageFont

f = ImageFont.truetype(r'C:\Windows\Fonts\arial.ttf', 24)
maxw = int(sys.argv[1])
text = sys.argv[2]
n, cur = 0, ''
for x in text.split(' '):
    tr = (cur + ' ' + x).strip()
    if f.getlength(tr) <= maxw or not cur:
        cur = tr
    else:
        n += 1
        cur = x
print(n + 1, len(text))
