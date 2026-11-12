import glob, subprocess, os, json

rows = []
for f in sorted(glob.glob('dl/v_*.mp4')) + ['dl/hc.mp4', 'dl/ac137.mp4']:
    if not os.path.exists(f):
        continue
    try:
        out = subprocess.run(['ffprobe', '-v', 'error', '-show_entries',
                              'format=duration:stream=width,height',
                              '-of', 'json', f],
                             capture_output=True, text=True, timeout=60).stdout
        d = json.loads(out)
        dur = float(d['format']['duration'])
        v = [s for s in d['streams'] if 'width' in s]
        wh = '%dx%d' % (v[0]['width'], v[0]['height']) if v else '?'
        ok = 'OK' if dur > 5 else 'TRUNC'
    except Exception as e:
        dur, wh, ok = 0, '?', 'BAD'
    rows.append((os.path.basename(f), wh, round(dur), ok))

for n, wh, d, ok in rows:
    print('%-28s %-10s %5ds  %s' % (n, wh, d, ok))
print('total', len(rows), 'bad:', sum(1 for r in rows if r[3] != 'OK'))
