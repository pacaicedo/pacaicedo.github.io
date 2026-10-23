#!/usr/bin/env python3
"""construir_marca.py — genera los archivos de la marca P. E. Caicedo-Rodríguez
a partir de una sola fuente de verdad (tokens + geometría).

    python3 recursos/marca/fuente/construir_marca.py

Escribe en recursos/marca/: logos SVG/PNG, temas de resaltado y los .scss/.sty
a partir de las plantillas de fuente/plantillas/. Requiere fontTools; los PNG se
hacen con Playwright/Chromium si está.
"""
import base64, json, math, os, re, subprocess, sys, urllib.parse
from pathlib import Path

AQUI = Path(__file__).resolve().parent
MARCA = AQUI.parent
FUENTES = MARCA / 'fuentes'
LOGO = MARCA / 'logo'
sys.path.insert(0, str(AQUI))
from texto_a_trazo import trazar, ancho

# ======================================================================== Tokens
T = {
 # neutros para fondo claro
 'tinta': '#14173A',   # títulos, texto de diapositivas, isotipo (17.3:1 sobre blanco)
 'texto': '#1D2142',   # texto corrido de documentos y sitio (15.6:1)
 'tenue': '#4D5375',   # metadatos, pies, leyendas (7.5:1)
 'filete': '#C9CEDF',  # filetes decorativos (nunca para información)
 'papel': '#F3F5FA',   # fondo de código, callouts y citas
 'blanco': '#FFFFFF',
 # acentos: -d = texto sobre claro (>= 7:1) · pleno = rellenos y trazos · -luz = sobre oscuro (>= 7:1)
 'dato-d': '#0B626D',  'dato': '#13A3BA',  'dato-luz': '#1EC6AE',
 'grafo-d': '#7435BD', 'grafo': '#9257E0', 'grafo-luz': '#C29FFE',
 'causa-d': '#8B4606', 'causa': '#D4820E', 'causa-luz': '#F89B24',
 'aviso-d': '#B5041D', 'aviso': '#DB383B', 'aviso-luz': '#FE928A',
 # oscuros
 'sala': '#111419',    # fondo del modo sala oscura (neutro: no tiñe las imágenes en gris)
 'sala-2': '#1B1F27',  # código y callouts sobre sala
 'noche': '#1B1D4A',   # campo de marca: separadores, portada del sitio, barra de navegación
 'noche-2': '#262A63',
 'luz': '#EEF1F6',     # texto sobre oscuro (16.3:1 sobre sala)
 'tenue-luz': '#A9B0C8',
 'filete-luz': '#3B4256',
}
N = lambda f: str(FUENTES / f)
F_EXTRA = N('AtkinsonHyperlegibleNext-ExtraBold.ttf')
F_MEDIO = N('AtkinsonHyperlegibleNext-Medium.ttf')

def fmt(x):
    s = ('%.2f' % x).rstrip('0').rstrip('.')
    return '0' if s == '-0' else s

# ======================================================================== Geometría
# Primitivas: ('l', x1,y1,x2,y2, ancho, color, remate) · ('t', [(x,y)...], color) ·
# ('c', cx,cy,r, relleno, trazo, ancho) · ('p', d_svg, d_tikz, color)
def flecha(p1, p2, r1, r2, w, hl, hw, gap, col, punta=True):
    (x1, y1), (x2, y2) = p1, p2
    dx, dy = x2 - x1, y2 - y1; d = math.hypot(dx, dy); ux, uy = dx / d, dy / d
    sx, sy = x1 + ux * (r1 + gap), y1 + uy * (r1 + gap)
    ex, ey = x2 - ux * (r2 + gap), y2 - uy * (r2 + gap)
    if not punta:
        return [('l', sx, sy, ex, ey, w, col, 'round')]
    bx, by = ex - ux * hl, ey - uy * hl; px, py = -uy, ux
    lx, ly = ex - ux * hl * 0.92, ey - uy * hl * 0.92
    return [('l', sx, sy, lx, ly, w, col, 'round'),
            ('t', [(ex, ey), (bx + px * hw / 2, by + py * hw / 2), (bx - px * hw / 2, by - py * hw / 2)], col)]

def g_isotipo(puntas=True):
    """Triángulo causal en una rejilla de 64: Z confusor (anillo), X dato (disco), Y efecto (disco), X -> Y."""
    Z, X, Y = (32, 12.5), (11.5, 50.5), (52.5, 50.5)
    r, rz, sw = 7.2, 6.4, 4.4
    if not puntas:          # versión mini (favicon): trazos más gruesos y sin puntas en las aristas del confusor
        r, rz, sw = 7.8, 6.6, 5.6
    g = []
    g += flecha(Z, X, rz + sw / 2 - .4, r, sw, 8.5, 9.5, 2.6, 'tinta', puntas)
    g += flecha(Z, Y, rz + sw / 2 - .4, r, sw, 8.5, 9.5, 2.6, 'tinta', puntas)
    g += flecha(X, Y, r, r, 5.6 if puntas else 6.4, 10.5, 12.5, 2.6, 'causa')
    g.append(('c', Z[0], Z[1], rz, None, 'tinta', sw))
    g.append(('c', X[0], X[1], r, 'dato', None, 0))
    g.append(('c', Y[0], Y[1], r, 'causa', None, 0))
    return g

MOT_W, MOT_H = 1500, 340
def g_motivo():
    """De x[n] a la causa: muestras de un latido -> grafo -> triángulo causal (lienzo 1500 x 340)."""
    amps = [0.0, 0.06, 0.15, 0.07, 0.0, -0.11, 1.0, -0.30, -0.03, 0.05, 0.17, 0.28, 0.19, 0.06]
    base, A, x0, dx, r, sw = 252, 200, 40, 42, 8, 5
    g = [('l', 14, base, x0 + dx * (len(amps) - 1) + 18, base, 3, 'tenue', 'round')]
    heads = []
    for i, a in enumerate(amps):
        x = x0 + i * dx; y = base - a * A; heads.append((x, y))
        if abs(a) > .015:
            g.append(('l', x, base, x, y + (r if a > 0 else -r), sw, 'dato', 'butt'))
    G = [(660, 196), (712, 104), (800, 246), (842, 150), (944, 76), (972, 232), (1060, 150)]
    E = [(0, 1), (0, 2), (1, 3), (2, 3), (3, 4), (2, 5), (5, 6), (4, 6), (3, 6)]
    rg, gw = 10, 4.5
    s = 6.6; X = (1178, 300); Y = (X[0] + 41 * s, 300); Z = (X[0] + 20.5 * s, 300 - 38 * s)
    rz, rn = 17, 24
    for a, b, ra in [(heads[-1], G[0], r), (heads[-3], G[1], r)]:
        g += flecha(a, b, ra, rg, gw, 0, 0, 3.5, 'grafo', False)
    for a, b in E:
        g += flecha(G[a], G[b], rg, rg, gw, 0, 0, 3.5, 'grafo', False)
    g += flecha(G[4], Z, rg, rz + 4, gw, 0, 0, 3.5, 'grafo', False)
    g += flecha(G[6], X, rg, rn, gw, 0, 0, 3.5, 'grafo', False)
    g += flecha(G[5], X, rg, rn, gw, 0, 0, 3.5, 'grafo', False)
    g += flecha(Z, X, rz + 4.5, rn, 9, 24, 24, 7, 'tinta')
    g += flecha(Z, Y, rz + 4.5, rn, 9, 24, 24, 7, 'tinta')
    g += flecha(X, Y, rn, rn, 12, 32, 34, 7, 'causa')
    for i, (x, y) in enumerate(heads):
        g.append(('c', x, y, r, 'dato', None, 0))
    for (x, y) in G:
        g.append(('c', x, y, rg, 'hueco', 'grafo', gw + .5))
    g.append(('c', Z[0], Z[1], rz, 'hueco', 'tinta', 9))
    g.append(('c', X[0], X[1], rn, 'dato', None, 0))
    g.append(('c', Y[0], Y[1], rn, 'causa', None, 0))
    return g

def g_bioforge():
    g = [('p', 'M3 33.5H57V40.5H47.5L43 45.5V49.5L50.5 58H13.5L21 49.5V45.5L16.5 40.5H14C9.5 40.5 5.8 38 3 33.5Z', None, 'yunque')]
    base, r = 33.5, 3.1
    for x, a in [(11, .14), (20.5, .24), (31, 1.0), (41.5, .2), (51, .38)]:
        y = base - 3.5 - a * 20.5; col = 'causa' if a == 1.0 else 'dato'
        g.append(('l', x, base, x, y + r, 2.7, col, 'butt'))
        g.append(('c', x, y, r, col, None, 0))
    cx, cy = 31, base - 3.5 - 20.5
    for ang in (-150, -90, -30):
        a = math.radians(ang)
        g.append(('l', cx + math.cos(a) * 6.4, cy + math.sin(a) * 6.4, cx + math.cos(a) * 10.4, cy + math.sin(a) * 10.4, 2.6, 'causa', 'round'))
    return g

# Colores de cada rol según el fondo
MODOS = {
    'claro':  {'tinta': T['tinta'], 'tenue': T['tenue'], 'dato': T['dato'], 'causa': T['causa'], 'grafo': T['grafo'], 'hueco': T['blanco'], 'yunque': T['noche']},
    'oscuro': {'tinta': T['luz'], 'tenue': T['tenue-luz'], 'dato': T['dato'], 'causa': T['causa'], 'grafo': T['grafo-luz'], 'hueco': T['sala'], 'yunque': T['luz']},
    'noche':  {'tinta': T['luz'], 'tenue': T['tenue-luz'], 'dato': T['dato'], 'causa': T['causa'], 'grafo': T['grafo-luz'], 'hueco': T['noche'], 'yunque': T['luz']},
}

def svg_de(g, modo, q='"'):
    C = MODOS[modo]; o = []
    for e in g:
        if e[0] == 'l':
            _, x1, y1, x2, y2, w, c, cap = e
            o.append(f'<line x1={q}{fmt(x1)}{q} y1={q}{fmt(y1)}{q} x2={q}{fmt(x2)}{q} y2={q}{fmt(y2)}{q} stroke={q}{C[c]}{q} stroke-width={q}{fmt(w)}{q} stroke-linecap={q}{cap}{q}/>')
        elif e[0] == 't':
            pts = e[1]; d = 'M' + 'L'.join(f'{fmt(x)} {fmt(y)}' for x, y in pts) + 'Z'
            o.append(f'<path d={q}{d}{q} fill={q}{C[e[2]]}{q}/>')
        elif e[0] == 'c':
            _, cx, cy, r, fill, stroke, w = e
            a = f'fill={q}{C[fill]}{q}' if fill else f'fill={q}none{q}'
            if stroke: a += f' stroke={q}{C[stroke]}{q} stroke-width={q}{fmt(w)}{q}'
            o.append(f'<circle cx={q}{fmt(cx)}{q} cy={q}{fmt(cy)}{q} r={q}{fmt(r)}{q} {a}/>')
        elif e[0] == 'p':
            o.append(f'<path d={q}{e[1]}{q} fill={q}{C[e[3]]}{q}/>')
    return ''.join(o)

def svg_doc(cuerpo, w, h, titulo=None, q='"'):
    t = f'<title>{titulo}</title>' if titulo else ''
    return f'<svg xmlns={q}http://www.w3.org/2000/svg{q} viewBox={q}0 0 {fmt(w)} {fmt(h)}{q} width={q}{fmt(w)}{q} height={q}{fmt(h)}{q}>{t}{cuerpo}</svg>'

def tikz_de(g, u=r'\caicedo@u', colores=None):
    """Primitivas -> órdenes TikZ con coordenadas del SVG (usar con [x=\\u, y=-\\u])."""
    colores = colores or {}
    nom = lambda c: colores.get(c, 'caicedo@' + c)
    o = []
    for e in g:
        if e[0] == 'l':
            _, x1, y1, x2, y2, w, c, cap = e
            o.append(rf'\draw[{nom(c)},line width={fmt(w)}{u},line cap={cap}] ({fmt(x1)},{fmt(y1)}) -- ({fmt(x2)},{fmt(y2)});')
        elif e[0] == 't':
            o.append(rf'\fill[{nom(e[2])}] ' + ' -- '.join(f'({fmt(x)},{fmt(y)})' for x, y in e[1]) + ' -- cycle;')
        elif e[0] == 'c':
            _, cx, cy, r, fill, stroke, w = e
            if fill and stroke:
                o.append(rf'\filldraw[fill={nom(fill)},draw={nom(stroke)},line width={fmt(w)}{u}] ({fmt(cx)},{fmt(cy)}) circle ({fmt(r)});')
            elif fill:
                o.append(rf'\fill[{nom(fill)}] ({fmt(cx)},{fmt(cy)}) circle ({fmt(r)});')
            else:
                o.append(rf'\draw[{nom(stroke)},line width={fmt(w)}{u}] ({fmt(cx)},{fmt(cy)}) circle ({fmt(r)});')
    return '\n'.join(o)

# ======================================================================== Logotipos (texto en trazos)
def firma(modo, vertical=False):
    """Isotipo + nombre + lema. Devuelve (svg, ancho, alto)."""
    C = MODOS[modo]
    nom, lema = 'P. E. Caicedo-Rodríguez', 'Del dato a la causa'
    iso = svg_de(g_isotipo(), modo)
    if not vertical:
        sn, sl = 31, 16.2
        x = 64 + 15
        pn, wn = trazar(nom, F_EXTRA, sn, x, 30.2, tracking=-0.012, word=-0.06, color=C['tinta'])
        pl, wl = trazar(lema, F_MEDIO, sl, x + .6, 53.2, color=C['tenue'])
        w = x + max(wn, wl) + 2
        return svg_doc(f'<g>{iso}</g>{pn}{pl}', w, 64, nom), w, 64
    sn, sl = 30, 15.6
    wn = ancho(nom, F_EXTRA, sn, tracking=-0.012, word=-0.06); wl = ancho(lema, F_MEDIO, sl)
    w = max(wn, wl) + 4; ix = (w - 64 * 1.25) / 2
    pn, _ = trazar(nom, F_EXTRA, sn, (w - wn) / 2, 80 + 30, tracking=-0.012, word=-0.06, color=C['tinta'])
    pl, _ = trazar(lema, F_MEDIO, sl, (w - wl) / 2, 80 + 54, color=C['tenue'])
    return svg_doc(f'<g transform="translate({fmt(ix)} 0) scale(1.25)">{iso}</g>{pn}{pl}', w, 140, nom), w, 140

def firma_pie(modo):
    """Isotipo + nombre, sin lema: para pies de diapositiva (el lema no se lee a ese tamaño)."""
    C = MODOS[modo]
    iso = svg_de(g_isotipo(), modo)
    pn, wn = trazar('P. E. Caicedo-Rodríguez', F_EXTRA, 36, 64 + 14, 44.2, tracking=-0.01, word=-0.06, color=C['tinta'])
    w = 64 + 14 + wn + 2
    return svg_doc(f'<g>{iso}</g>{pn}', w, 64, 'P. E. Caicedo-Rodríguez')

def insignia(mini=True):
    g = g_isotipo(puntas=not mini)
    cuerpo = f'<rect width="64" height="64" rx="14" fill="{T["noche"]}"/><g transform="translate(9.6 9.6) scale(0.7)">{svg_de(g, "noche")}</g>'
    return svg_doc(cuerpo, 64, 64, 'P. E. Caicedo-Rodríguez')

def bioforge_firma(modo):
    C = MODOS[modo]
    sym = svg_de(g_bioforge(), modo)
    x = 64 + 12
    pn, wn = trazar('BioForge', F_EXTRA, 33, x, 34, tracking=-0.01, color=C['tinta'])
    pl, wl = trazar('Experiment OS', F_MEDIO, 15.5, x + .8, 55, color=C['tenue'])
    w = x + max(wn, wl) + 2
    return svg_doc(f'<g>{sym}</g>{pn}{pl}', w, 64, 'BioForge')

NOMBRES_TEX = {'tinta': 'ctinta', 'texto': 'ctexto', 'tenue': 'ctenue', 'filete': 'cfilete', 'papel': 'cpapel', 'blanco': 'cblanco',
    'dato-d': 'cdatod', 'dato': 'cdato', 'dato-luz': 'cdatoluz', 'grafo-d': 'cgrafod', 'grafo': 'cgrafo', 'grafo-luz': 'cgrafoluz',
    'causa-d': 'ccausad', 'causa': 'ccausa', 'causa-luz': 'ccausaluz', 'aviso-d': 'cavisod', 'aviso': 'caviso', 'aviso-luz': 'cavisoluz',
    'sala': 'csala', 'sala-2': 'csalados', 'noche': 'cnoche', 'noche-2': 'cnochedos', 'luz': 'cluz', 'tenue-luz': 'ctenueluz', 'filete-luz': 'cfileteluz'}
def colores_tex():
    w = max(len(v) for v in NOMBRES_TEX.values()) + 2
    o = [('\\definecolor{' + NOMBRES_TEX[k] + '}').ljust(w + 14) + '{HTML}{' + v.lstrip('#') + '}' + (f'  % {COMENTARIOS[k]}' if COMENTARIOS.get(k) else '') for k, v in T.items()]
    o.append('% Nombres de la versión 1 (para \\textcolor{...} escritos a mano en qmd antiguos)')
    for a, b in [('cink', 'ctinta'), ('csurface', 'cnoche'), ('cnavy', 'ctenue'), ('cpaper', 'cpapel'), ('ctext', 'ctexto'), ('cmuted', 'ctenue'),
                 ('crule', 'cfilete'), ('clight', 'cluz'), ('cmuteddk', 'ctenueluz'), ('cruledk', 'cfileteluz'), ('cgrafod', 'cgrafod')]:
        if a != b: o.append(f'\\colorlet{{{a}}}{{{b}}}')
    return '\n'.join(o)

def data_uri(svg):
    svg = svg.replace('"', "'")
    return 'data:image/svg+xml;charset=utf-8,' + urllib.parse.quote(svg, safe=" '=:/;,.-_()")

def escribir(p, s):
    """Escribe solo si el contenido cambió: así la fecha del archivo no cambia sin motivo y el
    pre-render del sitio no vuelve a calcular figuras que no lo necesitan."""
    p = Path(p); p.parent.mkdir(parents=True, exist_ok=True)
    if not (p.exists() and p.read_text(encoding='utf-8') == s):
        p.write_text(s, encoding='utf-8')
    return p

def logos():
    LOGO.mkdir(exist_ok=True)
    out = {}
    for modo in ('claro', 'oscuro'):
        out[f'isotipo-{modo}.svg'] = svg_doc(svg_de(g_isotipo(), modo), 64, 64, 'P. E. Caicedo-Rodríguez')
        out[f'isotipo-mini-{modo}.svg'] = svg_doc(svg_de(g_isotipo(False), modo), 64, 64, 'P. E. Caicedo-Rodríguez')
        out[f'firma-{modo}.svg'] = firma(modo)[0]
        out[f'firma-vertical-{modo}.svg'] = firma(modo, True)[0]
        out[f'firma-pie-{modo}.svg'] = firma_pie(modo)
        out[f'bioforge-{modo}.svg'] = svg_doc(svg_de(g_bioforge(), modo), 64, 64, 'BioForge')
        out[f'bioforge-firma-{modo}.svg'] = bioforge_firma(modo)
    for modo in ('claro', 'oscuro', 'noche'):
        out[f'motivo-{modo}.svg'] = svg_doc(svg_de(g_motivo(), modo), MOT_W, MOT_H, 'De x[n] a la causa')
    out['insignia.svg'] = insignia(mini=False)
    out['favicon.svg'] = insignia(mini=True)
    # nombres de la versión anterior, para no romper los qmd existentes
    out['red-causal.svg'] = out['motivo-noche.svg']
    out['logo-horizontal-claro.svg'] = out['firma-claro.svg']
    out['logo-horizontal-oscuro.svg'] = out['firma-oscuro.svg']
    for n, s in out.items():
        escribir(LOGO / n, s)
    return out

# ======================================================================== Web: fuentes, tokens SCSS
WEB = FUENTES / 'web'
def b64(p): return base64.b64encode(Path(p).read_bytes()).decode()
RESPALDO_RANGO = 'U+00B5, U+0370-03FF, U+2070-209F, U+2100-214F, U+2190-21FF, U+2200-22FF, U+2300-230F, U+25A0-25FF, U+2605-2606, U+2713-2717, U+27E8-27E9'
RESPALDO_MONO_RANGO = 'U+00B5, U+0370-03FF, U+2190-21FF, U+2200-22FF, U+2500-25FF, U+2713-2717'
def fuentes_css():
    f = []
    def ff(fam, estilo, peso, archivo, extra=''):
        f.append(f'@font-face {{ font-family: "{fam}"; font-style: {estilo}; font-weight: {peso}; font-display: swap;{extra} '
                 f'src: url("data:font/woff2;base64,{b64(WEB / archivo)}") format("woff2"); }}')
    ff('Atkinson Hyperlegible Next', 'normal', '200 800', 'AtkinsonHyperlegibleNext-Variable.woff2')
    ff('Atkinson Hyperlegible Next', 'italic', '200 800', 'AtkinsonHyperlegibleNext-Italic-Variable.woff2')
    ff('Atkinson Hyperlegible Mono', 'normal', '200 800', 'AtkinsonHyperlegibleMono-Variable.woff2')
    ff('Atkinson Hyperlegible Mono', 'italic', '200 800', 'AtkinsonHyperlegibleMono-Italic-Variable.woff2')
    # Respaldo para griego, flechas y símbolos que Atkinson no trae (DejaVu, a la altura x de Atkinson)
    ff('Caicedo Respaldo', 'normal', '400', 'CaicedoRespaldo.woff2', f' size-adjust: 91%; unicode-range: {RESPALDO_RANGO};')
    ff('Caicedo Respaldo Mono', 'normal', '400', 'CaicedoRespaldoMono.woff2', f' size-adjust: 91%; unicode-range: {RESPALDO_MONO_RANGO};')
    return '\n'.join(f)

COMENTARIOS = {
 'tinta': 'títulos, texto de diapositivas, isotipo (17.3:1 sobre blanco)', 'texto': 'texto corrido de documentos y sitio (15.6:1)',
 'tenue': 'metadatos, pies, leyendas (7.5:1)', 'filete': 'filetes decorativos, nunca para información',
 'papel': 'fondo de código, callouts y citas', 'blanco': '',
 'dato-d': 'dato, texto sobre claro (7.0:1)', 'dato': 'dato, rellenos y trazos', 'dato-luz': 'dato, sobre oscuro (8.6:1)',
 'grafo-d': 'grafo, texto sobre claro (7.0:1)', 'grafo': 'grafo, rellenos y trazos', 'grafo-luz': 'grafo, sobre oscuro (8.5:1)',
 'causa-d': 'causa, texto sobre claro (7.1:1)', 'causa': 'causa, rellenos y trazos', 'causa-luz': 'causa, sobre oscuro (8.5:1)',
 'aviso-d': 'aviso, texto sobre claro (7.0:1)', 'aviso': 'aviso, rellenos y trazos', 'aviso-luz': 'aviso, sobre oscuro (8.5:1)',
 'sala': 'fondo del modo sala oscura (neutro: no tiñe las imágenes en gris)', 'sala-2': 'código y callouts sobre sala',
 'noche': 'campo de marca: separadores, portada del sitio, barra de navegación', 'noche-2': 'superficie sobre noche',
 'luz': 'texto sobre oscuro (16.3:1 sobre sala)', 'tenue-luz': 'metadatos sobre oscuro (8.6:1)', 'filete-luz': 'filetes sobre oscuro',
}
def tokens_scss(default=True):
    d = ' !default' if default else ''
    w = max(len(k) for k in T) + 4
    out = [f'${("c-" + k + ":").ljust(w)} {v}{d};' + (f'  // {COMENTARIOS[k]}' if COMENTARIOS.get(k) else '') for k, v in T.items()]
    return '\n'.join(out)
ALIAS_SCSS = '''// Nombres de la versión 1, para no romper capas propias que los usen.
$c-ink: $c-tinta !default;
$c-surface: $c-noche !default;
$c-navy: $c-tenue !default;
$c-paper: $c-papel !default;
$c-text: $c-texto !default;
$c-muted: $c-tenue !default;
$c-rule: $c-filete !default;
$c-light: $c-luz !default;
$c-muted-dk: $c-tenue-luz !default;'''

def tokens_py():
    w = max(len(k) for k in T) + 3
    return '\n'.join(f"    {repr(k) + ':':<{w}} {repr(v)},  # {COMENTARIOS.get(k) or ''}".rstrip(' #') for k, v in T.items())

def barra_svg(alto=6, escala=1.0):
    """Barra causal: tramo de dato, hueco y tramo de causa con punta (de izquierda a derecha)."""
    a = alto; s = escala
    w = 108 * s; h = a * 2.4
    y = (h - a) / 2
    cuerpo = (f'<rect x="0" y="{fmt(y)}" width="{fmt(64*s)}" height="{fmt(a)}" fill="{T["dato"]}"/>'
              f'<rect x="{fmt(71*s)}" y="{fmt(y)}" width="{fmt(22*s)}" height="{fmt(a)}" fill="{T["causa"]}"/>'
              f'<path d="M{fmt(92*s)} 0L{fmt(108*s)} {fmt(h/2)}L{fmt(92*s)} {fmt(h)}Z" fill="{T["causa"]}"/>')
    return svg_doc(cuerpo, w, h), w, h

def rellenar(plantilla, destino, valores):
    s = (AQUI / 'plantillas' / plantilla).read_text(encoding='utf-8')
    for k, v in valores.items():
        s = s.replace('@@' + k + '@@', v)
    faltan = re.findall(r'@@[A-Z_0-9]+@@', s)
    if faltan: raise SystemExit(f'{plantilla}: marcadores sin valor {sorted(set(faltan))}')
    return escribir(MARCA / destino, s)

# ======================================================================== Construcción
def construir():
    lg = logos()
    barra, _, _ = barra_svg()
    comunes = {
        'TOKENS': tokens_scss() + '\n\n' + ALIAS_SCSS,
        'FUENTES': fuentes_css(),
        'BARRA': data_uri(barra),
        'MOTIVO_CLARO': data_uri(lg['motivo-claro.svg']),
        'MOTIVO_OSCURO': data_uri(lg['motivo-oscuro.svg']),
        'MOTIVO_NOCHE': data_uri(lg['motivo-noche.svg']),
        'FIRMA_CLARO': data_uri(lg['firma-claro.svg']),
        'FIRMA_OSCURO': data_uri(lg['firma-oscuro.svg']),
        'FIRMA_PIE_CLARO': data_uri(lg['firma-pie-claro.svg']),
        'FIRMA_PIE_OSCURO': data_uri(lg['firma-pie-oscuro.svg']),
        'COLORES_TEX': colores_tex(),
        'ISO_TIKZ': tikz_de(g_isotipo(), u=r'\caicedo@isou'),
        'MOTIVO_TIKZ': tikz_de(g_motivo()),
        'ISO_CLARO': data_uri(lg['isotipo-claro.svg']),
        'ISO_OSCURO': data_uri(lg['isotipo-oscuro.svg']),
        'ISO_NOCHE': data_uri(svg_doc(svg_de(g_isotipo(), 'noche'), 64, 64)),
        'TOKENS_PY': tokens_py(),
    }
    comunes.update(CALIB)
    comunes['ICONOS'] = (AQUI / 'plantillas' / '_iconos-beamer.tex').read_text(encoding='utf-8').rstrip()
    comunes['ICONOS_DOC'] = (AQUI / 'plantillas' / '_iconos-doc.tex').read_text(encoding='utf-8').rstrip()
    comunes.update({k: v for k, v in T.items()})
    hechos = []
    raiz = AQUI / 'plantillas'
    for p in sorted(raiz.rglob('*')):
        if p.is_dir() or p.name.startswith('_') or '__pycache__' in p.parts: continue
        rel = p.relative_to(raiz).as_posix()
        hechos.append(rellenar(rel, rel, comunes))
    for extra in EXTRAS:
        hechos += extra()
    return hechos

EXTRAS = []
# Constantes de calce beamer <-> revealjs (medidas comparando las dos salidas; ver fuente/LEEME.md)
CALIB = {'AJUSTE': '-0.2pt', 'TRASLISTA': '12.67pt', 'ARRIBA': '6.36pt', 'INICIO': '1.06pt'}

# ======================================================================== Temas de resaltado (Pandoc/Skylighting)
def temas():
    estilos = ['Alert', 'Annotation', 'Attribute', 'BaseN', 'BuiltIn', 'Char', 'Comment', 'CommentVar', 'Constant',
               'ControlFlow', 'DataType', 'DecVal', 'Documentation', 'Error', 'Extension', 'Float', 'Function',
               'Import', 'Information', 'Keyword', 'Operator', 'Other', 'Preprocessor', 'SpecialChar',
               'SpecialString', 'String', 'Variable', 'VerbatimString', 'Warning']
    # Papel de cada estilo: palabras clave = grafo (estructura), funciones = dato, literales = causa,
    # comentarios = tenue en cursiva, errores = aviso en negrita. Todos >= 6.4:1 sobre su fondo.
    papel = {'Keyword': 'grafo', 'ControlFlow': 'grafo', 'Import': 'grafo', 'Preprocessor': 'grafo',
             'Function': 'dato', 'BuiltIn': 'dato', 'Attribute': 'dato', 'DataType': 'dato', 'Extension': 'dato',
             'String': 'causa', 'Char': 'causa', 'VerbatimString': 'causa', 'SpecialString': 'causa', 'SpecialChar': 'causa',
             'DecVal': 'causa', 'BaseN': 'causa', 'Float': 'causa', 'Constant': 'causa',
             'Comment': 'tenue', 'CommentVar': 'tenue', 'Documentation': 'tenue', 'Annotation': 'tenue',
             'Alert': 'aviso', 'Error': 'aviso', 'Warning': 'aviso', 'Information': 'aviso'}
    hechos = []
    for modo, fondo, texto, suf in [('claro', T['papel'], T['tinta'], '-d'), ('oscuro', T['sala-2'], T['luz'], '-luz')]:
        ts = {}
        for e in estilos:
            p = papel.get(e)
            if p is None: col = texto
            elif p == 'tenue': col = T['tenue'] if modo == 'claro' else T['tenue-luz']
            else: col = T[p + suf]
            ts[e] = {'text-color': col, 'background-color': None, 'bold': e in ('Alert', 'Error', 'Warning'),
                     'italic': p == 'tenue', 'underline': False}
        tema = {'text-color': texto, 'background-color': fondo,
                'line-number-color': T['tenue'] if modo == 'claro' else T['tenue-luz'],
                'line-number-background-color': None, 'text-styles': ts}
        hechos.append(escribir(MARCA / f'caicedo-{modo}.theme', json.dumps(tema, indent=2, ensure_ascii=False) + '\n'))
    return hechos
EXTRAS.append(temas)

# ======================================================================== PNG (requiere Playwright + Chromium)
def tarjeta_social():
    """Imagen para compartir (1200 x 630): noche, firma y motivo."""
    lg_firma = firma('noche')[0]
    mot = svg_de(g_motivo(), 'noche')
    cuerpo = (f'<rect width="1200" height="630" fill="{T["noche"]}"/>'
              f'<g transform="translate(72 64) scale(1.55)">{lg_firma[lg_firma.index(">")+1:-6]}</g>'
              f'<g transform="translate(60 270) scale(0.72)">{mot}</g>')
    return svg_doc(cuerpo, 1200, 630, 'P. E. Caicedo-Rodríguez')

def exportar_png():
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print('  (sin Playwright: no se exportan PNG)'); return []
    escribir(LOGO / 'tarjeta-social.svg', tarjeta_social())
    trabajos = [('isotipo-claro.svg', 'isotipo-claro.png', 1024, 1024), ('isotipo-oscuro.svg', 'isotipo-oscuro.png', 1024, 1024),
                ('insignia.svg', 'insignia.png', 512, 512), ('insignia.svg', 'apple-touch-icon.png', 180, 180),
                ('favicon.svg', 'favicon-32.png', 32, 32), ('favicon.svg', 'favicon-192.png', 192, 192),
                ('motivo-claro.svg', 'motivo-claro.png', 3000, 680), ('motivo-noche.svg', 'motivo-noche.png', 3000, 680),
                ('motivo-noche.svg', 'red-causal.png', 3000, 680),
                ('bioforge-claro.svg', 'bioforge-claro.png', 1024, 1024), ('bioforge-oscuro.svg', 'bioforge-oscuro.png', 1024, 1024),
                ('tarjeta-social.svg', 'tarjeta-social.png', 1200, 630)]
    for n in ['firma-claro', 'firma-oscuro', 'firma-pie-claro', 'firma-pie-oscuro', 'firma-vertical-claro', 'firma-vertical-oscuro',
              'bioforge-firma-claro', 'bioforge-firma-oscuro']:
        s = (LOGO / f'{n}.svg').read_text(); m = re.search(r'viewBox="0 0 ([\d.]+) ([\d.]+)"', s)
        w, h = float(m.group(1)), float(m.group(2)); k = 1600 / w
        trabajos.append((f'{n}.svg', f'{n}.png', 1600, round(h * k)))
    trabajos += [('firma-claro.svg', 'logo-horizontal-claro.png', 1600, None), ('firma-oscuro.svg', 'logo-horizontal-oscuro.png', 1600, None)]
    hechos = []
    with sync_playwright() as p:
        b = p.chromium.launch()
        for src, dst, w, h in trabajos:
            if h is None:
                s = (LOGO / src).read_text(); m = re.search(r'viewBox="0 0 ([\d.]+) ([\d.]+)"', s); h = round(float(m.group(2)) * w / float(m.group(1)))
            pg = b.new_page(viewport={'width': w, 'height': h})
            pg.set_content(f'<html><body style="margin:0;background:transparent"><img src="data:image/svg+xml;base64,{base64.b64encode((LOGO / src).read_bytes()).decode()}" style="width:{w}px;height:{h}px;display:block"></body></html>')
            pg.wait_for_timeout(60)
            pg.screenshot(path=str(LOGO / dst), omit_background=True); pg.close(); hechos.append(LOGO / dst)
        b.close()
    return hechos
EXTRAS.append(exportar_png)

# ======================================================================== Principal
if __name__ == '__main__':
    for p in construir():
        print('  escrito', p.relative_to(MARCA))
