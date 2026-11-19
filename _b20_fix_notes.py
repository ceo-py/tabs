# -*- coding: utf-8 -*-
"""Apply the audit findings to the b20a / b20d note texts.

Second independent audit (9 cards) found 4 note texts that do not match what
the videos actually show. Geometry, times, bboxes and `out` are untouched - only
the note strings change, then the affected cards are re-rendered.

    py -3.14 _b20_fix_notes.py
"""
import json
import os
import subprocess
import sys

R = os.path.dirname(os.path.abspath(__file__))

FIXES = {
    # Half The World Away: the video shows "Em/C", never "Fm/C"
    # (the same row also contains "Fmaj7/C", so E and F are distinguishable here)
    ("b20a_spec", "wtjoRQfmHQI"): [
        ("Fm/C", "Em/C"),
        ("over the chord shapes in the lower panel", "over the TAB in the lower panel"),
    ],
    # Whatever: "F#" is never a chord on its own in this video - it is the bass
    # note of G/F#. The remaining 9 chords are all confirmed.
    ("b20a_spec", "6CVKC5LVAAs"): [
        ("B7add11 F# E A", "B7add11 E A"),
        ("over the chord shapes in the upper panel", "over the TAB in the upper panel"),
    ],
    # Some Might Say: the trailing glyph is cut off in the video itself and
    # cannot be read (most likely "Em") - it must not be listed as "E".
    ("b20a_spec", "qPTV5wkocv0"): [
        ("D5 Bsus2/F# G D A Em C E (", "D5 Bsus2/F# G D A Em C ("),
    ],
    # Columbia / Shakermaker: these videos show NO tab notation at all, so
    # "TAB notation only" is factually wrong.
    ("b20d_spec", "Lbs---ONA3I"): [
        ("Strumming: not shown in the video - TAB notation only",
         "Strumming: not shown in the video - no strumming pattern appears on screen"),
    ],
    ("b20d_spec", "B-BkCZrGp2M"): [
        ("Strumming: not shown in the video - TAB notation only",
         "Strumming: not shown in the video - no strumming pattern appears on screen"),
    ],
}


def main():
    changed = []
    for (specdir, vid), subs in FIXES.items():
        p = os.path.join(R, specdir, "%s.json" % vid)
        if not os.path.exists(p):
            print("  MISSING %s/%s.json" % (specdir, vid))
            continue
        raw = open(p, encoding="utf-8").read()
        j = json.loads(raw)
        note = j.get("note", "")
        orig = note
        for a, b in subs:
            if a not in note:
                print("  !! %s/%s: pattern not found: %r" % (specdir, vid, a))
                continue
            note = note.replace(a, b)
        if note != orig:
            j["note"] = note
            with open(p, "w", encoding="utf-8") as f:
                json.dump(j, f, ensure_ascii=False, indent=1)
            changed.append((specdir.replace("_spec", ""), vid))
            print("  fixed %s/%s" % (specdir, vid))
            print("      %s" % note)
        else:
            print("  unchanged %s/%s" % (specdir, vid))

    if not changed:
        print("\nnothing to do")
        return 0

    # re-render the affected cards
    for ns in ("b20a", "b20d"):
        ids = [v for n, v in changed if n == ns]
        if not ids:
            continue
        script = os.path.join(R, "%s_build.py" % ns)
        r = subprocess.run([sys.executable, script] + ids, cwd=R, capture_output=True,
                           text=True, encoding="utf-8", errors="replace", timeout=1800)
        print("build %s rc=%s" % (ns, r.returncode))
        if r.returncode != 0:
            print(r.stdout[-1200:])
            print(r.stderr[-1200:])
            return 1
    print("\n%d cards re-rendered" % len(changed))
    return 0


if __name__ == "__main__":
    sys.exit(main())
