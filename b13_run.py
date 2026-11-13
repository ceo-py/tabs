"""b13_run.py - run the survey for every song of my manifests.

Picks the right video file for each song and calls b13_survey.py.

Usage: py -3.14 b13_run.py <manifest.json> [...]
"""
import json
import os
import subprocess
import sys


def pick(vid):
    for c in ('dl/w4_%s.mp4' % vid, 'dl/gz_%s.mp4' % vid, 'dl/v_%s.mp4' % vid):
        if os.path.exists(c) and os.path.getsize(c) > 1000000:
            return c
    return None


def main():
    for man in sys.argv[1:]:
        for it in json.load(open(man, encoding='utf-8')):
            vid = it['id']
            v = pick(vid)
            if not v:
                print('NO VIDEO', vid, flush=True)
                continue
            r = subprocess.run(['py', '-3.14', 'b13_survey.py', v, vid, '4'],
                               capture_output=True, text=True)
            out = r.stdout.strip().splitlines()
            print(out[0] if out else ('ERR %s %s' % (vid, r.stderr[-200:])), flush=True)
            r2 = subprocess.run(['py', '-3.14', 'b13_labels.py', v, vid, '16'],
                                capture_output=True, text=True)
            o2 = r2.stdout.strip().splitlines()
            print('   ', o2[0] if o2 else ('ERR %s %s' % (vid, r2.stderr[-200:])), flush=True)


if __name__ == '__main__':
    main()
