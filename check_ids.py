# -*- coding: utf-8 -*-
"""Cross-check every $('#id') used in app.js against site/index.html."""
import os
import re

ROOT = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(ROOT, 'site', 'app.js'), encoding='utf-8').read()
html = open(os.path.join(ROOT, 'site', 'index.html'), encoding='utf-8').read()

ids = sorted(set(re.findall(r"\$\('#([A-Za-z0-9_-]+)'\)", src)))
bad = []
for i in ids:
    ok = ('id="%s"' % i) in html
    print('%-12s %s' % (i, 'ok' if ok else '*** MISSING IN HTML ***'))
    if not ok:
        bad.append(i)
print('\nmissing:', bad if bad else 'none')
