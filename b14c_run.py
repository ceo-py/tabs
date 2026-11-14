"""b14c_run.py - survey + labels for the 6 John Mayer songs of b14_assign_3.json.

Same as b13_run.py but filtered to my own video ids and with my own
b14c_manifest.json so I never touch another agent's work.

Usage: py -3.14 b14c_run.py [video_id ...]
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
    man = json.load(open('b14c_manifest.json', encoding='utf-8'))
    ids = sys.argv[1:] or [it['id'] for it in man]
    for it in man:
        vid = it['id']
        if vid not in ids:
            continue
        v = pick(vid)
        if not v:
            print('NO VIDEO', vid, flush=True)
            continue
        r = subprocess.run(['py', '-3.14', 'b13_survey.py', v, vid, '4'],
                           capture_output=True, text=True)
        out = r.stdout.strip().splitlines()
        print(out[0] if out else ('ERR %s %s' % (vid, r.stderr[-300:])), flush=True)
        for ln in out[1:]:
            print('   ', ln, flush=True)
        r2 = subprocess.run(['py', '-3.14', 'b13_labels.py', v, vid, '16'],
                            capture_output=True, text=True)
        o2 = r2.stdout.strip().splitlines()
        print('   ', o2[0] if o2 else ('ERR %s %s' % (vid, r2.stderr[-300:])), flush=True)


if __name__ == '__main__':
    main()
