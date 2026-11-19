# -*- coding: utf-8 -*-
"""Extract every Oasis-related video with tabs, across all measured channels."""
import collections
import json
import os
import re

R = os.path.dirname(os.path.abspath(__file__))
import _channels_all_dump as D

OASIS = re.compile(r"\boasis\b", re.I)


def main():
    data = D.load()
    out = []
    rows = []
    for label, vids in data.items():
        hits = [v for v in vids if OASIS.search(v.get("t", ""))]
        if not hits:
            continue
        tab = [v for v in hits if D.TAB_RE.search(v.get("t", ""))]
        cover = [v for v in hits if D.COVER_RE.search(v.get("t", ""))]
        out.append((label, hits, tab, cover))

    out.sort(key=lambda x: -len(x[2]))
    total_tab = sum(len(x[2]) for x in out)
    total_all = sum(len(x[1]) for x in out)

    md = ["# Oasis — всички видеа в измерените канали\n",
          "**%d видеа общо, от които %d с tab (%d с cover)**\n" % (total_all, total_tab,
                                                                 sum(len(x[3]) for x in out)),
          "| Канал | Видеа | С tab | С cover |",
          "|---|---|---|---|"]
    for label, hits, tab, cover in out:
        md.append("| %s | %d | %d | %d |" % (label, len(hits), len(tab), len(cover)))
    md.append("")

    for label, hits, tab, cover in out:
        md.append("## %s — %d видеа (%d с tab)\n" % (label, len(hits), len(tab)))
        md.append("| # | Видео | TAB |")
        md.append("|---|---|---|")
        for i, v in enumerate(sorted(hits, key=lambda x: x.get("t", "")), 1):
            t = re.sub(r"\s+", " ", v.get("t", "")).strip().replace("|", "\\|")
            istab = "да" if D.TAB_RE.search(v.get("t", "")) else ""
            md.append("| %d | [%s](%s) | %s |" % (i, t, v.get("url", ""), istab))
            rows.append([label, t, v.get("url", ""), istab])
        md.append("")

    with open(os.path.join(R, "_oasis_videos.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(md))
    with open(os.path.join(R, "_oasis_videos.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["channel", "title", "url", "has_tab"])
        w.writerows(rows)

    print("Oasis: %d видеа общо, %d с tab, в %d канала" % (total_all, total_tab, len(out)))
    print()
    for label, hits, tab, cover in out:
        print("%-34s %4d видеа  %4d tab  %4d cover" % (label[:34], len(hits), len(tab), len(cover)))
    print()
    for label, hits, tab, cover in out:
        for v in sorted(tab, key=lambda x: x.get("t", "")):
            print("  %-22s %s" % (label[:22], re.sub(r"\s+", " ", v.get("t", ""))[:96]))


if __name__ == "__main__":
    import csv
    main()
