# -*- coding: utf-8 -*-
"""Final synthesis: two axes per channel —
   (1) rock/grunge catalogue size
   (2) usability for TABS 90 (title says tab AND is a rock cover)
"""
import collections
import json
import os

R = os.path.dirname(os.path.abspath(__file__))
import _channels_all_dump as D

PRIMARY = [
    "DadRock TABS", "Schmuck's Punk Tabs", "CWZ Guitar", "CoverSolutions",
    "Dotti Brothers", "Nikola Gugoski", "Steven Perrone", "GuitarForce.Com",
    "Godderdy Tabs", "guitar cover with tabs & chords",
]


def metrics(vids):
    pool = [v for v in vids if D.TAB_RE.search(v.get("t", ""))]
    if not pool:
        pool = vids
    g = collections.Counter()
    usable = collections.Counter()
    for v in pool:
        t = v.get("t", "")
        tags = [k for k, rx in D.GEN_RE.items() if rx.search(t)]
        for k in tags:
            g[k] += 1
        if tags and D.COVER_RE.search(t):
            for k in tags:
                usable[k] += 1
    return {
        "total": len(vids), "tab": sum(1 for v in vids if D.TAB_RE.search(v.get("t", ""))),
        "bass": sum(1 for v in pool if D.BASS_RE.search(v.get("t", ""))),
        "g": g, "usable": usable, "pool": len(pool),
    }


def main():
    data = D.load()
    res = {k: metrics(v) for k, v in data.items()}

    lines = ["# Финална матрица: обем vs. използваемост за TABS 90\n"]

    lines.append("## A. Топ-10 — какво има и колко от него е използваемо\n")
    lines.append("| Канал | Видеа | С TAB | Рок(всички) | Рок+cover+tab (използваемо) | Дял | Водеща група |")
    lines.append("|---|---|---|---|---|---|---|")
    for lbl in PRIMARY:
        m = res[lbl]
        tot_rock = sum(m["g"].values())
        use = sum(m["usable"].values())
        gs = sorted(m["g"].items(), key=lambda kv: -kv[1])[:3]
        top = ", ".join("%s %d" % (k.upper(), c) for k, c in gs)
        lines.append("| %s | %d | %d | %d | **%d** | %.0f%% | %s |" % (
            lbl, m["total"], m["tab"], tot_rock, use,
            100.0 * use / max(1, m["pool"]), top))
    lines.append("")

    lines.append("## B. Всички канали, подредени по ИЗПОЛЗВАЕМИ rock+cover+tab видеа\n")
    lines.append("| Канал | Използваемо | С TAB | Рок | Видеа | Водеща група |")
    lines.append("|---|---|---|---|---|---|")
    rows = sorted(res.items(), key=lambda kv: -sum(kv[1]["usable"].values()))
    for lbl, m in rows[:30]:
        use = sum(m["usable"].values())
        if use == 0:
            break
        gs = sorted(m["g"].items(), key=lambda kv: -kv[1])[:2]
        top = ", ".join("%s %d" % (k.upper(), c) for k, c in gs)
        lines.append("| %s | **%d** | %d | %d | %d | %s |" % (
            lbl, use, m["tab"], sum(m["g"].values()), m["total"], top))
    lines.append("")

    lines.append("## C. По група — най-големият източник (rock + cover + tab)\n")
    lines.append("| Група | #1 | #2 | #3 | Използваемо общо |")
    lines.append("|---|---|---|---|---|")
    for grp in ("grunge", "punk", "metal", "classic", "alt"):
        ranked = sorted(res.items(), key=lambda kv: -kv[1]["usable"].get(grp, 0))[:3]
        cells = ["%s (%d)" % (l, m["usable"].get(grp, 0)) for l, m in ranked]
        lines.append("| %s | %s | **%d** |" % (grp.upper(), " | ".join(cells),
                                              sum(m["usable"].get(grp, 0) for m in res.values())))
    lines.append("")

    lines.append("## D. Канали с голям rock каталог, но БЕЗ tab в заглавията (имат нужда от проверка на кадри)\n")
    lines.append("| Канал | Видеа | Rock | TAB в заглавията | Забележка |")
    lines.append("|---|---|---|---|---|")
    for lbl, m in sorted(res.items(), key=lambda kv: -sum(kv[1]["g"].values())):
        if m["tab"] > 0:
            continue
        rock = sum(m["g"].values())
        if rock < 60:
            continue
        gs = sorted(m["g"].items(), key=lambda kv: -kv[1])[:2]
        top = ", ".join("%s %d" % (k.upper(), c) for k, c in gs)
        lines.append("| %s | %d | %d | 0 | %s |" % (lbl, m["total"], rock, top))
    lines.append("")

    txt = "\n".join(lines)
    with open(os.path.join(R, "_final_matrix.md"), "w", encoding="utf-8") as f:
        f.write(txt)
    print(txt)


if __name__ == "__main__":
    main()
