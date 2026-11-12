import json, os, subprocess, sys, time

ids = [e['id'] for e in json.load(open('gz_batches/batch5.json'))]
for vid in ids:
    out = 'dl/v_%s.mp4' % vid
    if os.path.exists(out):
        print('SKIP', vid, flush=True)
        continue
    url = 'https://www.youtube.com/watch?v=' + vid
    for attempt, extra in enumerate([[], ['--extractor-args', 'youtube:player_client=android']]):
        cmd = ['py', '-3.14', '-m', 'yt_dlp', '--no-warnings']
        if not extra:
            cmd += ['--extractor-args', 'youtube:player_client=android_creator']
        else:
            cmd += extra
        cmd += ['-f', '137/best', '--no-part', '-o', out, url]
        r = subprocess.run(cmd, capture_output=True, text=True)
        if os.path.exists(out):
            print('OK', vid, flush=True)
            break
        print('FAIL', vid, 'attempt', attempt, r.stderr[-400:], flush=True)
        time.sleep(10)
    else:
        print('GIVEUP', vid, flush=True)
print('ALLDONE', flush=True)
