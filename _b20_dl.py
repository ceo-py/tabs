# -*- coding: utf-8 -*-
"""Background downloader for batch 20 (Oasis)."""
import json
import os
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor

ROOT = os.path.dirname(os.path.abspath(__file__))
DL = os.path.join(ROOT, 'dl')
BASE = 'https://www.youtube.com/watch?v='


def ids():
    rows = json.load(open(os.path.join(ROOT, 'gz_batches', 'batch20.json'), encoding='utf-8'))
    return [r['id'] for r in rows]


def fetch(vid):
    target = os.path.join(DL, 'w4_%s.mp4' % vid)
    if os.path.exists(target) and os.path.getsize(target) > 100000:
        return vid, 'skip'
    for attempt in range(4):
        cmd = [
            sys.executable, '-m', 'yt_dlp', '--no-warnings',
            '--extractor-args', 'youtube:player_client=android_creator',
            '-f', '299/137/136/303/399/18/best', '-o', target,
            BASE + vid,
        ]
        subprocess.run(cmd, capture_output=True, text=True)
        if os.path.exists(target) and os.path.getsize(target) > 100000:
            return vid, 'ok'
        time.sleep(12 + attempt * 10)
    return vid, 'FAIL'


def main():
    vids = ids()
    print('%d videos to fetch' % len(vids), flush=True)
    ok = fail = skip = 0
    with ThreadPoolExecutor(max_workers=4) as ex:
        for vid, st in ex.map(fetch, vids):
            if st == 'ok':
                ok += 1
                print('ok   %s  (%d done)' % (vid, ok), flush=True)
            elif st == 'skip':
                skip += 1
            else:
                fail += 1
                print('FAIL %s' % vid, flush=True)
    print('DONE ok=%d skip=%d fail=%d' % (ok, skip, fail), flush=True)


if __name__ == '__main__':
    main()
