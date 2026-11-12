import json
import os
import subprocess
import sys

entries = json.load(open('gz_batches/batch6.json', encoding='utf-8'))
for e in entries:
    vid = e['id']
    src = 'dl/v_%s.mp4' % vid
    if not os.path.exists(src) or os.path.getsize(src) < 100000:
        continue
    outdir = 'frames/sv_%s' % vid
    if os.path.exists(outdir + '_montage.png'):
        print('have', vid)
        continue
    r = subprocess.run(['ffprobe', '-v', 'error', '-show_entries',
                        'format=duration', '-of', 'csv=p=0', src],
                       capture_output=True, text=True)
    try:
        dur = float(r.stdout.strip())
    except Exception:
        dur = 240
    interval = 10 if dur < 180 else (15 if dur < 420 else 20)
    cols = 6 if interval <= 15 else 7
    print('survey', vid, 'dur=%.0f' % dur, 'interval', interval, flush=True)
    subprocess.run(['py', '-3.14', 'survey.py', src, outdir, str(interval), str(cols)],
                   capture_output=True, text=True)
print('done')
