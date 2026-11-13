"""Private prep tool (b16 / b12r) for GuitarZero2HeroExpress cards.

Samples 1 frame per second and works out, per video, where the TAB / chord
sheet panel and its section label are.  Two layouts are supported:

  A) a dark-red horizontal header bar above a white sheet  (most videos)
  B) a white sheet with a vertical dark-red section label on its right
     (some videos, e.g. Shallow)

The section title glyphs inside the red label are used to split the video into
sections; for every section a full-resolution crop of the panel (label
included) is written out.

Usage:
  py -3.14 b16_prep.py <video.mp4> <outdir>
Outputs: <outdir>/scan.json, <outdir>/stack.png, <outdir>/c_*.png
"""
import json, os, subprocess, sys, glob
import numpy as np
from PIL import Image, ImageDraw, ImageFont

RED_T = (125, 80, 80)
WHITE_T = (200, 200, 200)
DW = 480


def run(cmd):
    return subprocess.run(cmd, capture_output=True)


def probe(video):
    o = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0',
                        '-show_entries', 'stream=width,height',
                        '-show_entries', 'format=duration',
                        '-of', 'csv=p=0', video], capture_output=True, text=True).stdout
    parts = [p for p in o.replace('\n', ',').split(',') if p]
    return int(parts[0]), int(parts[1]), float(parts[-1])


def components(mask, min_area):
    """Run-length connected components (4-connectivity)."""
    h, w = mask.shape
    parent = {}

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[rb] = ra

    prev_runs = []
    comp = {}
    label = 0
    for y in range(h):
        row = mask[y]
        if not row.any():
            prev_runs = []
            continue
        d = np.diff(np.concatenate(([0], row.view(np.int8), [0])))
        starts = np.flatnonzero(d == 1)
        ends = np.flatnonzero(d == -1) - 1
        cur_runs = []
        for s, e in zip(starts, ends):
            label += 1
            parent[label] = label
            comp[label] = [int(s), y, int(e), y, int(e - s + 1)]
            for ps, pe, plab in prev_runs:
                if ps <= e and s <= pe:
                    union(plab, label)
            cur_runs.append((int(s), int(e), label))
        prev_runs = cur_runs
    groups = {}
    for lab, (x0, y0, x1, y1, a) in comp.items():
        r = find(lab)
        if r not in groups:
            groups[r] = [x0, y0, x1, y1, a]
        else:
            g = groups[r]
            g[0] = min(g[0], x0); g[1] = min(g[1], y0)
            g[2] = max(g[2], x1); g[3] = max(g[3], y1)
            g[4] += a
    res = [(g[0], g[1], g[2] - g[0] + 1, g[3] - g[1] + 1, g[4]) for g in groups.values()]
    res = [r for r in res if r[4] >= min_area]
    res.sort(key=lambda b: -b[4])
    return res


def analyse(arr):
    a = arr.astype(np.int16)
    r, g, b = a[:, :, 0], a[:, :, 1], a[:, :, 2]
    rm = (r > RED_T[0]) & (g < RED_T[1]) & (b < RED_T[2])
    wm = (r > WHITE_T[0]) & (g > WHITE_T[0]) & (b > WHITE_T[0])
    red = components(rm, 200)
    wht = components(wm, 200)
    h, w = wm.shape
    roww = wm.sum(axis=1)
    runx = np.zeros((h, 2), np.int32)
    for y in range(h):
        row = wm[y]
        if not row.any():
            continue
        d = np.diff(np.concatenate(([0], row.view(np.int8), [0])))
        starts = np.flatnonzero(d == 1)
        ends = np.flatnonzero(d == -1) - 1
        lens = ends - starts + 1
        k = int(np.argmax(lens))
        runx[y] = (starts[k], ends[k])
    return red, wht, roww, runx


def median(v):
    s = sorted(v)
    return s[len(s) // 2]


def longest_row_band(roww, thresh):
    """Longest contiguous run of rows with many white pixels."""
    ys = [y for y in range(len(roww)) if roww[y] > thresh]
    if not ys:
        return None
    groups = []
    start = ys[0]
    prev = ys[0]
    for y in ys[1:]:
        if y != prev + 1:
            groups.append((start, prev))
            start = y
        prev = y
    groups.append((start, prev))
    g = max(groups, key=lambda gg: gg[1] - gg[0])
    return g


def main():
    video = sys.argv[1]
    outdir = sys.argv[2]
    os.makedirs(outdir, exist_ok=True)
    sc = os.path.join(outdir, '_sc')
    os.makedirs(sc, exist_ok=True)
    run(['ffmpeg', '-y', '-v', 'error', '-i', video, '-vf', 'fps=1,scale=%d:-1' % DW,
         os.path.join(sc, 'sc_%04d.png')])
    files = sorted(glob.glob(sc + '/*.png'))
    if not files:
        print('NO FRAMES')
        return
    src_w, src_h, dur = probe(video)
    fx = src_w / Image.open(files[0]).size[0]

    frames = []
    for i, f in enumerate(files):
        arr = np.asarray(Image.open(f).convert('RGB'))
        red, wht, roww, runx = analyse(arr)
        frames.append({'t': i, 'red': red, 'white': wht, 'roww': roww,
                       'runx': runx, 'file': f})

    # ---- layout mode ----------------------------------------------------
    key = {}
    for fr in frames:
        for c in fr['red']:
            # a section header bar: wide but thin
            if c[2] > 0.5 * DW and c[3] <= 0.2 * (len(fr['roww'])) and c[4] > 1500:
                k = (c[0], c[1], c[2], c[3])
                key[k] = key.get(k, 0) + 1
    mode = 'A'
    bar_box = None
    if key and max(key.values()) > 0.2 * len(frames):
        best = max(key.items(), key=lambda kv: kv[1])[0]
        bar_box = [best[0], best[1], best[0] + best[2], best[1] + best[3]]
    else:
        mode = 'B'

    def sheet_band(fr):
        """(y0,y1,x0,x1) of the white sheet band."""
        band = longest_row_band(fr['roww'], 0.08 * DW)
        if not band:
            return None
        y0, y1 = band
        xs0 = [int(fr['runx'][y][0]) for y in range(y0, y1 + 1)
               if fr['runx'][y][1] > fr['runx'][y][0]]
        xs1 = [int(fr['runx'][y][1]) for y in range(y0, y1 + 1)
               if fr['runx'][y][1] > fr['runx'][y][0]]
        if not xs0:
            return None
        x0 = median(xs0)
        x1 = median(xs1)
        if (x1 - x0) < 0.15 * DW:      # too narrow to be the sheet
            return None
        return (y0, y1, x0, x1)

    def label_for(fr, sheet):
        """Red label adjacent to the sheet (right of it or above it)."""
        best = None
        for c in fr['red']:
            x0, y0, w, h, a = c
            if a < 200:
                continue
            if mode == 'A':
                continue
            # right of the sheet
            if y0 < sheet[1] and y0 + h > sheet[0] and x0 >= sheet[2] - 2 \
                    and x0 - sheet[3] < 40:
                cand = (a, c)
                if best is None or cand[0] > best[0]:
                    best = cand
        if best:
            c = best[1]
            return [c[0], c[1], c[0] + c[2], c[1] + c[3]]
        return None

    def tall_red_label(fr):
        """A narrow, tall red strip = the vertical section label (layout B)."""
        H = len(fr['roww'])
        best = None
        for c in fr['red']:
            x0, y0, w, h, a = c
            if h >= 0.12 * H and w <= 0.12 * DW and a >= 150:
                if best is None or a > best[4]:
                    best = c
        if not best:
            return None
        x0, y0, w, h, a = best
        return [x0, y0, x0 + w, y0 + h]

    # per-frame geometry
    for fr in frames:
        sh = sheet_band(fr)
        fr['sheet'] = sh
        if mode == 'A':
            fr['panel'] = None
            fr['label'] = bar_box
        else:
            lab = tall_red_label(fr)
            fr['label'] = lab
            if not lab:
                fr['panel'] = None
                continue
            # the sheet sits left of the label, on the same rows
            starts = []
            for y in range(lab[1], min(lab[3], len(fr['roww']))):
                s, e = fr['runx'][y]
                if s < lab[0] and e >= s:
                    starts.append(int(s))
            x0 = median(starts) if starts else lab[0]
            fr['panel'] = (x0, lab[1], lab[2], lab[3])

    # ---- signature box --------------------------------------------------
    if mode == 'A':
        sx0, sy0, sx1, sy1 = bar_box
    else:
        labs = [fr['label'] for fr in frames if fr.get('label')]
        if not labs:
            print('NO LABEL')
            return
        sx0 = median([l[0] for l in labs]); sy0 = median([l[1] for l in labs])
        sx1 = median([l[2] for l in labs]); sy1 = median([l[3] for l in labs])

    def sig(arr):
        sub = arr[sy0:sy1 + 1, sx0:sx1 + 1]
        m = (sub[:, :, 0] > 195) & (sub[:, :, 1] > 195) & (sub[:, :, 2] > 195)
        return m.tobytes()

    secs = []
    prev = None
    if mode == 'B':
        # the vertical label is too small at 480 px wide - re-read it at full
        # resolution so the rotated section title is legible
        lx = max(0, int(sx0 * fx) - 6)
        ly = max(0, int(sy0 * fx) - 6)
        lw = min(src_w - lx, int((sx1 - sx0) * fx) + 12)
        lh = min(src_h - ly, int((sy1 - sy0) * fx) + 12)
        ld = outdir + '/_lab'
        os.makedirs(ld, exist_ok=True)
        for f in glob.glob(ld + '/*.png'):
            os.remove(f)
        run(['ffmpeg', '-y', '-v', 'error', '-i', video, '-vf',
             'fps=1,crop=%d:%d:%d:%d' % (lw, lh, lx, ly),
             os.path.join(ld, 'l_%04d.png')])
        lf = sorted(glob.glob(ld + '/l_*.png'))
        for i, f in enumerate(lf):
            arr = np.asarray(Image.open(f).convert('RGB'))
            m = (arr[:, :, 0] > 195) & (arr[:, :, 1] > 195) & (arr[:, :, 2] > 195)
            s = m.tobytes()
            if prev is None:
                diff = 10 ** 9
            else:
                diff = sum(1 for x, y in zip(s, prev) if x != y)
                thr = max(6, 0.35 * max(int(sum(prev)), int(m.sum())))
                if diff <= thr:
                    diff = 0
            if diff > 0:
                secs.append([i, i])
            else:
                secs[-1][1] = i
            prev = s
    else:
        for fr in frames:
            arr = np.asarray(Image.open(fr['file']).convert('RGB'))
            s = sig(arr)
            if prev is None:
                diff = 10 ** 9
            else:
                diff = sum(1 for x, y in zip(s, prev) if x != y)
                wp = sum(prev)
                wc = sum(s)
                thr = max(6, 0.35 * max(wp, wc))
                if diff <= thr:
                    diff = 0
            if diff > 0:
                secs.append([fr['t'], fr['t']])
            else:
                secs[-1][1] = fr['t']
            prev = s
    merged = []
    for s in secs:
        if merged and s[1] - s[0] < 2 and s[0] - merged[-1][1] <= 1:
            merged[-1][1] = s[1]
        else:
            merged.append(list(s))
    secs = merged

    out = {'video': video, 'src': [src_w, src_h], 'duration': dur, 'mode': mode,
           'bar': [int(sx0 * fx), int(sy0 * fx), int(sx1 * fx), int(sy1 * fx)],
           'sections': []}
    crops = []
    for n, (a, b) in enumerate(secs):
        sf = [fr for fr in frames if a <= fr['t'] <= b]
        t = a + 0.5
        if mode == 'A':
            shs = [fr['sheet'] for fr in sf if fr['sheet']]
            if shs:
                sy0s = median([s[0] for s in shs]); sy1s = median([s[1] for s in shs])
                sx0s = median([s[2] for s in shs]); sx1s = median([s[3] for s in shs])
            else:
                sy0s, sy1s, sx0s, sx1s = bar_box[3], src_h, bar_box[0], bar_box[2]
            X0 = int(min(bar_box[0], sx0s) * fx)
            Y0 = int(bar_box[1] * fx)
            X1 = int(max(bar_box[2], sx1s) * fx)
            Y1 = int(sy1s * fx)
        else:
            ps = [fr['panel'] for fr in sf if fr.get('panel')]
            if not ps:
                continue
            px0 = median([p[0] for p in ps]); py0 = median([p[1] for p in ps])
            px1 = median([p[2] for p in ps]); py1 = median([p[3] for p in ps])
            X0 = int(px0 * fx); Y0 = int(py0 * fx)
            X1 = int(px1 * fx); Y1 = int(py1 * fx)
        X0 = max(0, X0); Y0 = max(0, Y0); X1 = min(src_w, X1); Y1 = min(src_h, Y1)
        if mode == 'A':
            # refine the exact red-bar top from the full-res frame
            probe_png = outdir + '/_probe.png'
            run(['ffmpeg', '-y', '-v', 'error', '-ss', '%.2f' % t, '-i', video,
                 '-frames:v', '1', '-vf',
                 'crop=%d:%d:%d:%d' % (X1 - X0, 120, X0, max(0, Y0 - 30)), probe_png])
            if os.path.exists(probe_png):
                pa = np.asarray(Image.open(probe_png).convert('RGB')).astype(np.int16)
                pr, pg, pb = pa[:, :, 0], pa[:, :, 1], pa[:, :, 2]
                redrow = ((pr > 125) & (pg < 80) & (pb < 80)).sum(axis=1)
                full = np.flatnonzero(redrow > 0.55 * (X1 - X0))
                if len(full):
                    groups = []
                    st = full[0]
                    pv = full[0]
                    for v in full[1:]:
                        if v != pv + 1:
                            groups.append((st, pv))
                            st = v
                        pv = v
                    groups.append((st, pv))
                    g = min(groups, key=lambda gg: abs(gg[0] - 30))
                    Y0 = max(0, Y0 - 30) + int(g[0])
        bbox = [X0, Y0, X1 - X0, Y1 - Y0]
        png = outdir + '/c_%02d.png' % n
        run(['ffmpeg', '-y', '-v', 'error', '-ss', '%.2f' % t, '-i', video,
             '-frames:v', '1', '-vf', 'crop=%d:%d:%d:%d' % (bbox[2], bbox[3], bbox[0], bbox[1]),
             png])
        sec = {'i': n, 't0': a, 't1': b, 't': t, 'bbox': bbox, 'png': png}
        out['sections'].append(sec)
        crops.append(('SEC %d  t=%d-%ds' % (n, a, b), png))

        # extra white panels (chord / strumming boxes) above the main panel
        for c in sf[0]['white']:
            X = int(c[0] * fx); Y = int(c[1] * fx); W = int(c[2] * fx); H = int(c[3] * fx)
            if Y + H < Y0 - 20 and W * H >= 4000:
                p = outdir + '/x_%02d_%d.png' % (n, c[0])
                run(['ffmpeg', '-y', '-v', 'error', '-ss', '%.2f' % t, '-i', video,
                     '-frames:v', '1', '-vf', 'crop=%d:%d:%d:%d' % (W, H, X, Y), p])
                sec.setdefault('extra', []).append({'bbox': [X, Y, W, H], 'png': p})
                crops.append(('SEC %d EXTRA panel (t=%ds)' % (n, a), p))

    lab = 30
    fnt = ImageFont.truetype(r'C:\Windows\Fonts\arialbd.ttf', 22)
    ims = []
    for name, p in crops:
        if os.path.exists(p):
            ims.append((name, Image.open(p).convert('RGB')))
    if ims:
        W = max(im.size[0] for _, im in ims)
        H = sum(im.size[1] + lab for _, im in ims)
        canvas = Image.new('RGB', (W, H), (18, 18, 30))
        d = ImageDraw.Draw(canvas)
        y = 0
        for name, im in ims:
            d.rectangle([0, y, W, y + lab], fill=(0, 0, 0))
            d.text((6, y + 3), name, font=fnt, fill=(255, 210, 0))
            y += lab
            canvas.paste(im, (0, y))
            y += im.size[1]
        canvas.save(outdir + '/stack.png')
        print('saved', outdir + '/stack.png', canvas.size)
    json.dump(out, open(outdir + '/scan.json', 'w'), indent=1)
    print('mode', mode, 'sections', len(out['sections']),
          [(s['t0'], s['t1']) for s in out['sections']])


if __name__ == '__main__':
    main()
