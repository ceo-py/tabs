# -*- coding: utf-8 -*-
"""
Background downloader for the 4th wave videos (batches 13..16).

Downloads to dl/w4_<ID>.mp4 (final name appears only when the file is complete).

    py -3.14 download_w4.py
"""
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
    out = []
    for bi in range(13, 17):
        p = os.path.join(ROOT, 'gz_batches', 'batch%d.json' % bi)
        for r in json.load(open(p, encoding='utf-8')):
            out.append(r['id'])
    return out


def fetch(vid):
    target = os.path.join(DL, 'w4_%s.mp4' % vid)
    if os.path.exists(target) and os.path.getsize(target) > 100000:
        return vid, 'skip'
    for attempt in range(4):
        cmd = [
            sys.executable, '-m', 'yt_dlp', '--no-warnings',
            '--extractor-args', 'youtube:player_client=android_creator',
            '-f', '137/best', '-o', target,
            BASE + vid,
        ]
        p = subprocess.run(cmd, capture_output=True, text=True)
        if os.path.exists(target) and os.path.getsize(target) > 100000:
            return vid, 'ok'
        time.sleep(12 + attempt * 10)
    return vid, 'FAIL'


def main():
    vids = ids()
    print('%d videos to fetch' % len(vids))
    ok = fail = skip = 0
    with ThreadPoolExecutor(max_workers=4) as ex:
        for vid, st in ex.map(fetch, vids):
            if st == 'ok':
                ok += 1
                print('ok   %s  (%d done)' % (vid, ok))
            elif st == 'skip':
                skip += 1
            else:
                fail += 1
                print('FAIL %s' % vid)
    print('DONE ok=%d skip=%d fail=%d' % (ok, skip, fail))


if __name__ == '__main__':
    main()
