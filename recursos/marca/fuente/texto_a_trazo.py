"""Convierte texto en trazos SVG con fontTools (cmap + avances + kerning GPOS de pares).
Sirve para que los logotipos no dependan de tener la fuente instalada."""
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from functools import lru_cache

@lru_cache(None)
def _font(path):
    f = TTFont(path)
    kern = {}
    if 'GPOS' in f:
        g = f['GPOS'].table
        idx = set()
        for fr in g.FeatureList.FeatureRecord:
            if fr.FeatureTag == 'kern':
                idx.update(fr.Feature.LookupListIndex)
        for li in sorted(idx):
            lk = g.LookupList.Lookup[li]
            subs = lk.SubTable; lt = lk.LookupType
            if lt == 9:
                lt = subs[0].ExtensionLookupType
                subs = [s.ExtSubTable for s in subs]
            if lt != 2:
                continue
            for st in subs:
                cov = st.Coverage.glyphs
                if st.Format == 1:
                    for i, g1 in enumerate(cov):
                        for pvr in st.PairSet[i].PairValueRecord:
                            v = pvr.Value1.XAdvance if pvr.Value1 and hasattr(pvr.Value1, 'XAdvance') else 0
                            if v: kern.setdefault((g1, pvr.SecondGlyph), v)
                elif st.Format == 2:
                    c1 = st.ClassDef1.classDefs; c2 = st.ClassDef2.classDefs
                    for g1 in cov:
                        k1 = c1.get(g1, 0)
                        row = st.Class1Record[k1].Class2Record
                        kern.setdefault(('__class__', g1), (row, c2))
    return f, kern

def _pair(kern, a, b):
    if (a, b) in kern: return kern[(a, b)]
    cl = kern.get(('__class__', a))
    if cl:
        row, c2 = cl
        rec = row[c2.get(b, 0)]
        v = rec.Value1
        return getattr(v, 'XAdvance', 0) or 0 if v else 0
    return 0

def ancho(texto, path, size, tracking=0.0, word=0.0):
    return trazar(texto, path, size, 0, 0, tracking, word)[1]

def trazar(texto, path, size, x, y, tracking=0.0, word=0.0, color=None):
    """Devuelve (svg_path_element, ancho). x,y = origen en la línea base; tracking y word en em."""
    f, kern = _font(path)
    cmap = f.getBestCmap(); gs = f.getGlyphSet(); upm = f['head'].unitsPerEm; hmtx = f['hmtx']
    s = size / upm
    pen = SVGPathPen(gs)
    cx = 0.0; prev = None
    for ch in texto:
        gn = cmap.get(ord(ch))
        if gn is None: gn = '.notdef'
        if prev: cx += _pair(kern, prev, gn)
        tp = TransformPen(pen, (s, 0, 0, -s, x + cx * s, y))
        gs[gn].draw(tp)
        cx += hmtx[gn][0] + tracking * upm + (word * upm if ch == ' ' else 0)
        prev = gn
    d = pen.getCommands()
    fill = f' fill="{color}"' if color else ''
    return f'<path{fill} d="{d}"/>', cx * s
