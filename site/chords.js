/* TABS 90 — chord shapes
   Renders a guitar chord diagram in the style the lessons use:
   the chord letter on top, the fretboard underneath.

   Classic vertical box: six strings (6th / low E on the left, 1st / high e
   on the right), frets running down, a dot on every string you press,
   a small circle for an open string and a cross for a muted one. */
(function (global) {
  'use strict';

  const STRINGS = ['E', 'A', 'D', 'G', 'B', 'e'];
  const X0 = 24;            // x of the 6th string
  const STEP = 16;          // distance between strings
  const NUT = 40;           // y of the nut
  const FR = 21;            // height of one fret
  const ROWS = 5;           // frets drawn
  const W = X0 + STEP * 5 + 18;

  let SHAPES = {};

  /* if the chord sits above the 1st fret the window moves up so the lowest
     pressed fret becomes the first row */
  function window(frets) {
    const used = frets.filter(f => f > 0);
    if (!used.length) return 1;
    const lo = Math.min.apply(null, used);
    return lo > 1 ? lo : 1;
  }

  function parse(name) {
    const direct = SHAPES[name];
    if (direct && direct.frets) {
      return { frets: direct.frets, base: direct.base || name, bass: direct.bass || null };
    }
    const m = /^(.+?)\(([^)]+)\)$/.exec(name);
    if (m && SHAPES[m[1]] && SHAPES[m[1]].frets) {
      return { frets: SHAPES[m[1]].frets, base: m[1], bass: m[2] };
    }
    const slash = name.split('/');
    if (slash.length > 1 && SHAPES[slash[0]] && SHAPES[slash[0]].frets) {
      return { frets: SHAPES[slash[0]].frets, base: slash[0], bass: slash.slice(1).join('/') };
    }
    return null;
  }

  function esc(s) {
    return String(s == null ? '' : s).replace(/[&<>"]/g, c => (
      { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  }

  /* -> SVG markup for one chord */
  function chordSVG(name, opts) {
    opts = opts || {};
    const found = parse(name);
    if (!found) return '';
    const frets = found.frets;
    const start = window(frets);
    const H = NUT + FR * ROWS + 10;

    let g = '';
    /* string names + open/muted markers above the nut */
    for (let i = 0; i < 6; i++) {
      const x = X0 + STEP * i;
      g += '<text x="' + x + '" y="14" class="cd-sn">' + STRINGS[i] + '</text>';
      if (frets[i] === -1) {
        g += '<text x="' + x + '" y="34" class="cd-x">×</text>';
      } else if (frets[i] === 0) {
        g += '<circle cx="' + x + '" cy="30" r="4.5" class="cd-o"/>';
      }
    }
    /* strings (vertical) */
    for (let i = 0; i < 6; i++) {
      const x = X0 + STEP * i;
      g += '<line x1="' + x + '" y1="' + NUT + '" x2="' + x + '" y2="' + (NUT + FR * ROWS) +
           '" class="cd-s"/>';
    }
    /* frets (horizontal) */
    for (let c = 0; c <= ROWS; c++) {
      const y = NUT + FR * c;
      g += '<line x1="' + (X0 - 8) + '" y1="' + y + '" x2="' + (X0 + STEP * 5 + 8) +
           '" y2="' + y + '" class="' + (c === 0 ? 'cd-nut' : 'cd-f') + '"/>';
    }
    /* the starting fret number */
    if (start > 1) {
      g += '<text x="' + (X0 - 12) + '" y="' + (NUT + FR * 0.5 + 6) +
           '" class="cd-fr">' + start + '</text>';
    }
    /* the dots */
    for (let i = 0; i < 6; i++) {
      const f = frets[i];
      if (f <= 0) continue;
      const row = f - start;
      if (row < 0 || row >= ROWS) continue;
      const x = X0 + STEP * i;
      const y = NUT + FR * row + FR / 2;
      g += '<circle cx="' + x + '" cy="' + y + '" r="7.2" class="cd-dot"/>';
    }

    const label = opts.noLabel ? '' : '<b class="cd-name">' + esc(name) + '</b>';
    const bass = found.bass && found.bass !== found.base
      ? '<span class="cd-bass">' + esc(found.bass) + ' bass</span>' : '';

    return '<figure class="cd">' + label +
      '<svg viewBox="0 0 ' + W + ' ' + H + '" width="' + W + '" height="' + H +
        '" role="img" aria-label="' + esc(name) + ' chord shape">' + g + '</svg>' + bass + '</figure>';
  }

  /* -> a whole legend for one song */
  function legend(names) {
    if (!names || !names.length) return '';
    const seen = [];
    names.forEach(n => { if (seen.indexOf(n) < 0) seen.push(n); });
    return seen.map(n => chordSVG(n)).join('');
  }

  function setShapes(shapes) { SHAPES = shapes || {}; }

  global.Chords = { setShapes: setShapes, chordSVG: chordSVG, legend: legend, STRINGS: STRINGS };
})(window);
