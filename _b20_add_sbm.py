# -*- coding: utf-8 -*-
"""Add the Stand By Me lesson (Oasis, Lex Guitar Tabs) to gz_batches/batch20.json."""
import json
import os

R = os.path.dirname(os.path.abspath(__file__))
P = os.path.join(R, "gz_batches", "batch20.json")

entry = {
    "id": "BAoPHsvI1v0",
    "artist": "Oasis",
    "song": "Stand By Me",
    "tag": "Tabs + Chords",
    "rock": True,
    "out": "out_gz/Oasis-Stand-By-Me.png",
    "url": "https://www.youtube.com/watch?v=BAoPHsvI1v0",
    "source_channel": "Lex Guitar Tabs",
    "score": 130,
}

data = json.load(open(P, encoding="utf-8"))
if isinstance(data, dict):
    data = data.get("lessons") or data.get("items") or list(data.values())
    raise SystemExit("unexpected dict shape, not touching")

ids = {r.get("id") for r in data}
if entry["id"] in ids:
    print("already in manifest")
else:
    data.append(entry)
    with open(P, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    print("added Stand By Me -> %d lessons" % len(data))

# keep the id list in sync
ip = os.path.join(R, "gz_batches", "batch20_ids.txt")
if os.path.exists(ip):
    lines = [l.strip() for l in open(ip, encoding="utf-8") if l.strip()]
    if entry["id"] not in lines:
        lines.append(entry["id"])
        with open(ip, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")
        print("batch20_ids.txt -> %d ids" % len(lines))
