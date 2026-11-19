# -*- coding: utf-8 -*-
"""Synthesise the research: per-channel genre-group distribution + group leaders."""
import collections
import json
import os
import re

R = os.path.dirname(os.path.abspath(__file__))
import _channels_all_dump as D  # reuse GENRES / regexes / loader

PRIMARY = [
    "DadRock TABS", "Schmuck's Punk Tabs", "CWZ Guitar", "CoverSolutions",
    "Dotti Brothers", "Nikola Gugoski", "Steven Perrone", "GuitarForce.Com",
    "Godderdy Tabs", "guitar cover with tabs & chords",
]
GROUP_ORDER = ["grunge", "punk", "metal", "classic", "alt", "posthc", "pop"]


def analyse(vids):
    """Non-exclusive genre counts over the channel's tab-style videos."""
    tab = [v for v in vids if D.TAB_RE.search(v.get("t", ""))]
    cov = [v for v in tab if D.COVER_RE.search(v.get("t", ""))]
    used = tab if tab else vids
    cnt = collections.Counter()
    unclassified = []
    for v in used:
        t = v.get("t", "")
        hit = False
        for g, rx in D.GEN_RE.items():
            if rx.search(t):
                cnt[g] += 1
                hit = True
        if not hit:
            unclassified.append(t)
    return {
        "total": len(vids), "tab": len(tab), "cover": len(cov),
        "bass": sum(1 for v in used if D.BASS_RE.search(v.get("t", ""))),
        "groups": cnt, "other": unclassified, "pool": len(used),
    }


def top_artists(titles, n=6):
    c = collections.Counter()
    for t in titles:
        t = re.sub(r"\(.*?\)|\[[^\]]*\]", "", t)
        parts = [p.strip() for p in t.split(" - ") if p.strip()]
        cand = None
        if len(parts) >= 2:
            cand = parts[1] if len(parts[1]) < 26 else parts[0]
        elif parts:
            cand = parts[0].split()[0] if parts[0].split() else None
        if cand:
            cand = re.sub(r"\b(guitar|bass|tab|tabs|tutorial|lesson|cover|song|chords|"
                          r"strumming|how|to|play|the)\b", " ", cand, flags=re.I).strip(" -")
            cand = re.sub(r"\s{2,}", " ", cand)
            if len(cand) > 2:
                c[cand] += 1
    return c.most_common(n)


def main():
    data = D.load()
    res = {}
    for label, vids in data.items():
        res[label] = analyse(vids)

    out = []
    out.append("# Синтез: канал x жанрова група\n")

    # ---------- 1. per channel ----------
    out.append("## 1. Всеки канал — от коя група има най-много\n")
    for label in PRIMARY:
        a = res.get(label)
        if not a:
            continue
        tot = a["pool"] or 1
        gs = sorted(a["groups"].items(), key=lambda kv: -kv[1])
        top = " · ".join("%s %d (%.0f%%)" % (g.upper(), c, 100.0 * c / tot) for g, c in gs[:3])
        other = a["other"]
        out.append("### %s — %d видеа (%d с tab, %d cover, %d bass)" % (
            label, a["total"], a["tab"], a["cover"], a["bass"]))
        out.append("")
        out.append("**Водещи групи:** " + (top or "—"))
        out.append("")
        out.append("| Група | Видеа | Дял |")
        out.append("|---|---|---|")
        for g in GROUP_ORDER:
            if a["groups"].get(g):
                out.append("| %s | %d | %.0f%% |" % (g.upper(), a["groups"][g],
                                                    100.0 * a["groups"][g] / tot))
        if other:
            arts = top_artists(other)
            out.append("| (некласифицирани) | %d | %.0f%% |" % (
                len(other), 100.0 * len(other) / tot))
            out.append("")
            out.append("Най-честите артисти в некласифицираните: " +
                       ", ".join("%s (%d)" % (x[:24], n) for x, n in arts))
        out.append("")

    # ---------- 2. group leaders ----------
    out.append("## 2. Кой канал води в коя група\n")
    out.append("| Група | #1 | #2 | #3 | #4 | #5 |")
    out.append("|---|---|---|---|---|---|")
    for g in GROUP_ORDER:
        ranked = sorted(res.items(), key=lambda kv: -kv[1]["groups"].get(g, 0))[:5]
        cells = []
        for label, a in ranked:
            c = a["groups"].get(g, 0)
            cells.append("%s (%d)" % (label, c) if c else "—")
        out.append("| %s | %s |" % (g.upper(), " | ".join(cells)))
    out.append("")

    # ---------- 3. best source per group ----------
    out.append("## 3. Най-добър източник за карти по група\n")
    out.append("| Група | Канал | Видеа | Защо |")
    out.append("|---|---|---|---|")
    notes = {
        "grunge": "най-близкият формат до нашия (TAB + chord панел върху изпълнение)",
        "punk": "пълен punk репертоар, табът е в описанието/екрана",
        "metal": "най-много обем, но двойни ленти гитар+бас",
        "classic": "класически rock репертоар за 70-80-те",
        "alt": "най-широк алтернативен/инди каталог",
        "posthc": "пост-хардкор/емо уроци с TAB",
        "pop": "поп/аниме cover-и, слаб fit за сайта",
    }
    for g in GROUP_ORDER:
        ranked = sorted(res.items(), key=lambda kv: -kv[1]["groups"].get(g, 0))
        for label, a in ranked[:2]:
            c = a["groups"].get(g, 0)
            if c < 20:
                continue
            out.append("| %s | %s | %d | %s |" % (g.upper(), label, c, notes[g]))
    out.append("")

    # ---------- 4. compact table for all channels ----------
    out.append("## 4. Всички 112 канала — водеща група\n")
    out.append("| Канал | Видеа | TAB | Водеща група | #1 | #2 | #3 |")
    out.append("|---|---|---|---|---|---|---|")
    rows = sorted(res.items(), key=lambda kv: -kv[1]["pool"])
    for label, a in rows:
        gs = sorted(a["groups"].items(), key=lambda kv: -kv[1])[:3]
        top = ", ".join("%s %d" % (g.upper(), c) for g, c in gs)
        out.append("| %s | %d | %d | %s |" % (label, a["total"], a["tab"], top or "—"))
    out.append("")

    txt = "\n".join(out)
    with open(os.path.join(R, "_genre_synthesis.md"), "w", encoding="utf-8") as f:
        f.write(txt)
    print(txt[:12000])


if __name__ == "__main__":
    main()
