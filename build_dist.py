# -*- coding: utf-8 -*-
"""
One-command update: rebuild the site and produce the uploadable archive.

    py -3.14 build_dist.py

Steps:
  1. import_cards.py  -> merges new cards from out_gz/ + out/ into songs.json
  2. site_build.py    -> regenerates site/cards, site/thumbs and site/data/songs.json
  3. dist/tabs90-site.zip  -> ready to upload to the VPS

On the VPS (see DEPLOY.md):

    /home/ceo/production/tabs-deploy.sh
"""
import os
import subprocess
import sys
import zipfile

ROOT = os.path.dirname(os.path.abspath(__file__))
PY = sys.executable
SITE = os.path.join(ROOT, 'site')
DIST = os.path.join(ROOT, 'dist')
ZIP = os.path.join(DIST, 'tabs90-site.zip')


def run(script, *args):
    cmd = [PY, os.path.join(ROOT, script)] + list(args)
    print('\n$ %s %s' % (script, ' '.join(args)))
    r = subprocess.run(cmd, cwd=ROOT)
    if r.returncode != 0:
        raise SystemExit('FAILED: %s (exit %d)' % (script, r.returncode))


def main():
    run('import_cards.py')
    run('site_build.py')

    os.makedirs(DIST, exist_ok=True)
    if os.path.exists(ZIP):
        os.remove(ZIP)
    with zipfile.ZipFile(ZIP, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for base, _dirs, files in os.walk(SITE):
            for f in files:
                full = os.path.join(base, f)
                z.write(full, os.path.relpath(full, SITE).replace('\\', '/'))

    size = os.path.getsize(ZIP) / 1048576
    print('\n%s  (%.2f MB)' % (os.path.relpath(ZIP, ROOT), size))
    print('the VPS syncs itself from GitHub every 5 minutes:')
    print('  git push origin main   ->   /home/ceo/production/tabs-deploy.sh')


if __name__ == '__main__':
    main()
