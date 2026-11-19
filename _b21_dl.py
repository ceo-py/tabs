# -*- coding: utf-8 -*-
"""Download the batch-21 videos (metadata + media) into dl/w4_<ID>.mp4."""
import json
import os
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor

R = os.path.dirname(os.path.abspath(__file__))
DL = os.path.join(R, "dl")
BASE = "https://www.youtube.com/watch?v="


def fetch(vid):
    target = os.path.join(DL, "w4_%s.mp4" % vid)
    if os.path.exists(target) and os.path.getsize(target) > 100000:
        return vid, "skip"
    for attempt in range(4):
        cmd = [sys.executable, "-m", "yt_dlp", "--no-warnings",
               "--extractor-args", "youtube:player_client=android_creator",
               "-f", "299/137/136/303/399/18/best", "-o", target, BASE + vid]
        subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8",
                       errors="replace")
        if os.path.exists(target) and os.path.getsize(target) > 100000:
            return vid, "ok"
        time.sleep(12 + attempt * 10)
    return vid, "FAIL"


def main():
    rows = json.load(open(os.path.join(R, "gz_batches", "batch21.json"), encoding="utf-8"))
    print("%d videos to fetch" % len(rows), flush=True)
    ok = fail = skip = 0
    with ThreadPoolExecutor(max_workers=3) as ex:
        for vid, st in ex.map(fetch, [r["id"] for r in rows]):
            print("%-6s %s" % (st, vid), flush=True)
            if st == "ok":
                ok += 1
            elif st == "skip":
                skip += 1
            else:
                fail += 1
    print("DONE ok=%d skip=%d fail=%d" % (ok, skip, fail), flush=True)


if __name__ == "__main__":
    main()
