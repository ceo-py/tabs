"""Report, for each crop, the lowest row/column containing bright (graphic) pixels,
so we can tell whether the on-screen graphic is clipped by the crop boundary.
"""
import glob, os, sys
from PIL import Image

rows = []
for path in sorted(glob.glob(sys.argv[1])):
    im = Image.open(path).convert('L')
    w, h = im.size
    px = im.load()
    last_row = -1
    for y in range(h - 1, -1, -1):
        if any(px[x, y] > 150 for x in range(0, w, 2)):
            last_row = y
            break
    last_col = -1
    for x in range(w - 1, -1, -1):
        if any(px[x, y] > 150 for y in range(0, h, 2)):
            last_col = x
            break
    rows.append((os.path.basename(path), w, h, last_row, h - 1 - last_row, last_col,
                 w - 1 - last_col))
print('%-28s %5s %5s %8s %8s %8s %8s' % ('file', 'w', 'h', 'lastRow', 'botGap', 'lastCol', 'rightGap'))
for r in rows:
    flag = '  <-- CLIPPED' if (r[4] <= 1 or r[6] <= 1) else ''
    print('%-28s %5d %5d %8d %8d %8d %8d%s' % (r[0], r[1], r[2], r[3], r[4], r[5], r[6], flag))
