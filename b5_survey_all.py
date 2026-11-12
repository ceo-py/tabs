import json, subprocess, sys

entries = json.load(open('gz_batches/batch5.json'))
ids = sys.argv[1:]
for e in entries:
    if ids and e['id'] not in ids:
        continue
    vid = e['id']
    out = 'frames/sv_%s' % vid
    if __import__('os').path.exists(out + '_montage.png'):
        print('SKIP', vid); continue
    r = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                        '-of', 'csv=p=0', 'dl/v_%s.mp4' % vid], capture_output=True, text=True)
    dur = float(r.stdout.strip())
    iv = 12 if dur < 160 else (15 if dur < 300 else 18)
    subprocess.run(['py', '-3.14', 'b5_survey.py', 'dl/v_%s.mp4' % vid, out, str(iv)])
print('SURVEYDONE', flush=True)
