import json, os, subprocess, sys, time

ids = [e['id'] for e in json.load(open('gz_batches/batch6.json', encoding='utf-8'))]
out = open('b6_dl.log', 'a', encoding='utf-8')

def log(*a):
    print(*a, file=out, flush=True)

for vid in ids:
    tgt = 'dl/v_%s.mp4' % vid
    if os.path.exists(tgt) and os.path.getsize(tgt) > 100000:
        log('SKIP', vid)
        continue
    ok = False
    for attempt, extra in enumerate(['', 'youtube:player_client=android']):
        cmd = ['py', '-3.14', '-m', 'yt_dlp', '--no-warnings']
        if extra:
            cmd += ['--extractor-args', extra]
        else:
            cmd += ['--extractor-args', 'youtube:player_client=android_creator']
        cmd += ['-f', '137/best', '--no-part', '-o', 'dl/v_%s.%%(ext)s' % vid,
                'https://www.youtube.com/watch?v=%s' % vid]
        r = subprocess.run(cmd, capture_output=True, text=True)
        if os.path.exists(tgt) and os.path.getsize(tgt) > 100000:
            log('OK', vid, os.path.getsize(tgt))
            ok = True
            break
        log('FAIL', vid, 'attempt', attempt, (r.stderr or '')[-300:])
        time.sleep(10)
    if not ok:
        log('FAILED_FINAL', vid)
out.close()
print('done')
