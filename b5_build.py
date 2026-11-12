import json, os, sys, glob
from b5_compose import make_card

SPEC_DIR = 'b5_spec'

def main():
    only = sys.argv[1:]
    files = sorted(glob.glob(os.path.join(SPEC_DIR, '*.json')))
    for f in files:
        e = json.load(open(f, encoding='utf-8'))
        if only and e['id'] not in only:
            continue
        for _lbl, _paths in e['sections']:
            for _p in _paths:
                if not os.path.exists(_p):
                    print('MISSING CROP', _p); raise SystemExit(1)
        make_card(
            e['id'], e['title'], e['subtitle'],
            [(lbl, list(paths)) for lbl, paths in e['sections']],
            note=e['note'], out_path=e['out'],
        )

if __name__ == '__main__':
    main()
