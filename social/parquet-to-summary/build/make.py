import csv, statistics as st, collections, math, subprocess

T = '/home/theo/cuplyr-material/benchmarks/parquet-pipeline/timings.csv'
OUT = '/home/theo/cuplyr-material/social/parquet-to-summary'
d = collections.defaultdict(list)
for r in csv.DictReader(open(T)):
    if int(r['rep']) >= 1 and r['ok'] == 'TRUE' and r['quiet'] == 'TRUE' and r['table'] == 'narrow' and r['cache'] == 'warm':
        d[(r['engine'], r['variant'], int(float(r['rows'])))].append(float(r['secs']))
med = {k: st.median(v) for k, v in d.items()}

BG, FG, MUT, GRID = '#0f1419', '#f2f4f7', '#8b95a3', '#232b36'
COL = {'cuplyr': '#2fd08f', 'duckdb': '#f0a830', 'dplyr': '#4aa3ff', 'data.table': '#d98ac0'}
NAME = {'cuplyr': 'cuplyr (GPU)', 'duckdb': 'DuckDB', 'dplyr': 'dplyr + arrow', 'data.table': 'data.table'}
F = 'font-family="Adwaita Sans, sans-serif"'
M = 'font-family="Adwaita Mono, monospace"'
ENG = ['cuplyr', 'duckdb', 'dplyr', 'data.table']
HW = 'RTX 5070 vs i9-12900K'
# compute time on data already fully loaded in R (build/split2.R, arrow.use_altrep = FALSE);
# "read" is the rest of each engine's measured total, i.e. getting the file into R
COMP = {}
for r in csv.DictReader(open(OUT + '/build/split2.csv')):
    if int(r['rep']) >= 1 and r['altrep'] == 'FALSE':
        COMP.setdefault(r['engine'], []).append(float(r['comp_el']))
COMP = {k: st.median(v) for k, v in COMP.items()}


def fmt(s):
    return f'{s*1000:.0f} ms' if s < 1 else f'{s:.1f} s'


def wrap(body, w=1600, h=900):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">'
            f'<rect width="{w}" height="{h}" fill="{BG}"/>{body}</svg>')


def foot(extra='', head='100M-row fact table in parquet. ', runs='5'):
    return (f'<text x="80" y="850" {F} font-size="22" fill="{MUT}">{head}'
            f'Median of {runs} runs, warm file cache. {HW}. {extra}</text>')


def hero():
    v, n = 'p1_nopush', 10**8
    vals = [(e, med[(e, v, n)]) for e in ENG]
    mx = max(x for _, x in vals)
    x0, wmax = 400, 760
    c = med[('cuplyr', v, n)]
    b = f'<text x="80" y="120" {F} font-size="64" font-weight="700" fill="{FG}">Parquet to summary,</text>'
    b += f'<text x="80" y="195" {F} font-size="64" font-weight="700" fill="{COL["cuplyr"]}">100M rows in {fmt(c)}</text>'
    b += (f'<text x="80" y="245" {F} font-size="26" fill="{MUT}">read, filter, mutate, group by 2 keys, summarise: one call, '
          f'result back in R. The filter cannot skip any of the file.</text>')
    for i, (e, s) in enumerate(vals):
        y = 330 + i * 115
        w = max(6, wmax * s / mx)
        b += f'<text x="{x0-24}" y="{y+42}" text-anchor="end" {F} font-size="30" fill="{FG}">{NAME[e]}</text>'
        if e in COMP:
            rd = s - COMP[e]
            rw = wmax * rd / mx
            b += f'<rect x="{x0}" y="{y}" width="{rw:.1f}" height="64" rx="8" fill="{COL[e]}" fill-opacity="0.45"/>'
            b += f'<rect x="{x0+rw:.1f}" y="{y}" width="{w-rw:.1f}" height="64" rx="8" fill="{COL[e]}"/>'
            b += f'<rect x="{x0+rw:.1f}" y="{y}" width="16" height="64" fill="{COL[e]}"/>'
            b += (f'<text x="{x0+rw/2:.1f}" y="{y+40}" text-anchor="middle" {F} font-size="24" font-weight="700" fill="{BG}">read into R {fmt(rd)}</text>')
            b += (f'<text x="{x0+rw+(w-rw)/2:.1f}" y="{y+40}" text-anchor="middle" {F} font-size="21" font-weight="700" fill="{BG}">compute {fmt(COMP[e])}</text>')
        else:
            b += f'<rect x="{x0}" y="{y}" width="{w:.1f}" height="64" rx="8" fill="{COL[e]}"/>'
        tx = x0 + w + 18
        b += f'<text x="{tx:.1f}" y="{y+45}" {F} font-size="34" font-weight="700" fill="{FG}">{fmt(s)}</text>'
        if e != 'cuplyr':
            r = s / c
            lab = f'{r:.0f}x slower' if r >= 10 else f'{r:.1f}x slower'
            b += f'<text x="{tx+(150 if s < 1 else 120):.1f}" y="{y+45}" {F} font-size="26" fill="{MUT}">{lab}</text>'
    b += (f'<text x="{x0}" y="{330+4*115-18}" {F} font-size="22" fill="{MUT}">cuplyr and DuckDB read and compute in one fused pass, so their bars are not split.</text>')
    b += (f'<text x="{x0}" y="{330+4*115+10}" {F} font-size="22" fill="{MUT}">For dplyr and data.table, compute is timed on data already loaded in R.</text>')
    b += foot('dplyr and data.table both read with arrow.')
    return wrap(b)


def scaling():
    v = 'p1_nopush'
    sizes = [10**6, 10**7, 10**8]
    L, R, Tp, B = 190, 1180, 300, 760
    lo, hi = math.log10(0.008), math.log10(10)
    X = lambda n: L + (math.log10(n) - 6) / 2 * (R - L)
    Y = lambda s: B - (math.log10(s) - lo) / (hi - lo) * (B - Tp)
    b = f'<text x="80" y="115" {F} font-size="58" font-weight="700" fill="{FG}">100x the data,</text>'
    b += f'<text x="80" y="185" {F} font-size="58" font-weight="700" fill="{COL["cuplyr"]}">{med[("cuplyr",v,10**8)]/med[("cuplyr",v,10**6)]:.0f}x the time</text>'
    b += (f'<text x="80" y="235" {F} font-size="26" fill="{MUT}">cuplyr: {fmt(med[("cuplyr",v,10**6)])} at 1M rows, '
          f'{fmt(med[("cuplyr",v,10**8)])} at 100M. dplyr: {fmt(med[("dplyr",v,10**6)])} to {fmt(med[("dplyr",v,10**8)])}.</text>')
    for s, lab in [(0.01, '10 ms'), (0.1, '100 ms'), (1, '1 s'), (10, '10 s')]:
        b += f'<line x1="{L}" y1="{Y(s):.1f}" x2="{R}" y2="{Y(s):.1f}" stroke="{GRID}" stroke-width="2"/>'
        b += f'<text x="{L-16}" y="{Y(s)+8:.1f}" text-anchor="end" {F} font-size="22" fill="{MUT}">{lab}</text>'
    for n, lab in zip(sizes, ['1M rows', '10M rows', '100M rows']):
        b += f'<text x="{X(n):.1f}" y="{B+42}" text-anchor="middle" {F} font-size="24" fill="{MUT}">{lab}</text>'
    for e in ENG:
        pts = [(X(n), Y(med[(e, v, n)])) for n in sizes]
        b += (f'<polyline fill="none" stroke="{COL[e]}" stroke-width="6" stroke-linejoin="round" '
              f'points="{" ".join(f"{x:.1f},{y:.1f}" for x, y in pts)}"/>')
        for x, y in pts:
            b += f'<circle cx="{x:.1f}" cy="{y:.1f}" r="9" fill="{COL[e]}"/>'
    last = -99
    for y, e in sorted((Y(med[(e, v, 10**8)]), e) for e in ENG):
        yy = max(y, last + 36)
        last = yy
        b += f'<text x="{R+28}" y="{yy+8:.1f}" {F} font-size="28" font-weight="700" fill="{COL[e]}">{NAME[e]}</text>'
    b += foot('Log scale.', head='Fact table in parquet, 1M to 100M rows. ', runs='5 to 15')
    return wrap(b)


def code():
    v, n = 'p1_nopush', 10**8
    lines = [
        ('read_parquet_gpu("sales.parquet") |>', 0),
        ('  filter(price >= 150, channel != "phone") |>', 0),
        ('  mutate(revenue = price * qty * (1 - discount)) |>', 0),
        ('  group_by(store, channel) |>', 0),
        ('  summarise(n = n(), revenue = sum(revenue),', 0),
        ('            avg_price = mean(price), max_qty = max(qty)) |>', 0),
        ('  collect()', 1),
    ]
    b = f'<text x="80" y="115" {F} font-size="58" font-weight="700" fill="{FG}">Same dplyr code.</text>'
    b += f'<text x="80" y="185" {F} font-size="58" font-weight="700" fill="{COL["cuplyr"]}">Different engine.</text>'
    b += f'<rect x="80" y="235" width="1440" height="400" rx="18" fill="#161d26" stroke="{GRID}" stroke-width="2"/>'
    for i, (t, hl) in enumerate(lines):
        t = t.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        b += (f'<text x="124" y="{300+i*52}" xml:space="preserve" {M} font-size="31" '
              f'fill="{COL["cuplyr"] if hl else FG}">{t}</text>')
    b += f'<text x="80" y="720" {F} font-size="34" fill="{FG}">100M rows, 773 MB of parquet, 2 keys, 4 aggregates:</text>'
    b += f'<text x="80" y="785" {F} font-size="48" font-weight="700" fill="{COL["cuplyr"]}">{fmt(med[("cuplyr",v,n)])}</text>'
    b += (f'<text x="250" y="783" {F} font-size="30" fill="{MUT}">on the GPU, vs {fmt(med[("dplyr",v,n)])} for dplyr '
          f'and {fmt(med[("duckdb",v,n)])} for DuckDB</text>')
    b += foot()
    return wrap(b)


def board():
    pipes = [('p1_nopush', 'filter, mutate,\ngroup by 2 keys'),
             ('p2_nopush', 'plus a join to\nthe store table'),
             ('p3_nopush', 'group by product,\ntop 10')]
    n = 10**8
    b = f'<text x="80" y="115" {F} font-size="58" font-weight="700" fill="{FG}">Where the GPU wins,</text>'
    b += f'<text x="80" y="185" {F} font-size="58" font-weight="700" fill="{COL["duckdb"]}">and where DuckDB does</text>'
    b += f'<text x="80" y="235" {F} font-size="26" fill="{MUT}">Time for 100M rows, parquet to summary. Shorter bar is faster (log scale).</text>'
    gx = [80, 580, 1080]
    gw = 440
    for (p, desc), x in zip(pipes, gx):
        for j, ln in enumerate(desc.split('\n')):
            b += f'<text x="{x}" y="{300+j*34}" {F} font-size="26" font-weight="700" fill="{FG}">{ln}</text>'
        for i, e in enumerate(ENG):
            s = med[(e, p, n)]
            y = 380 + i * 92
            w = max(14, (math.log10(s) - math.log10(0.02)) / (math.log10(15) - math.log10(0.02)) * (gw - 120))
            b += f'<rect x="{x}" y="{y}" width="{w:.1f}" height="52" rx="7" fill="{COL[e]}"/>'
            b += f'<text x="{x+w+12:.1f}" y="{y+37}" {F} font-size="28" font-weight="700" fill="{FG}">{fmt(s)}</text>'
    for i, e in enumerate(ENG):
        b += (f'<rect x="{80+i*340}" y="770" width="22" height="22" rx="5" fill="{COL[e]}"/>'
              f'<text x="{112+i*340}" y="789" {F} font-size="24" fill="{FG}">{NAME[e]}</text>')
    b += (f'<text x="80" y="850" {F} font-size="22" fill="{MUT}">Median of 5 runs, warm file cache. {HW}. '
          f'The join is cuplyr\'s weak spot at this size.</text>')
    return wrap(b)


for name, svg in [('1-hero', hero()), ('2-scaling', scaling()), ('3-code', code()), ('4-scoreboard', board())]:
    p = f'{OUT}/build/{name}.svg'
    open(p, 'w').write(svg)
    subprocess.run(['rsvg-convert', '-w', '1600', p, '-o', f'{OUT}/{name}.png'], check=True)
    print(name)
