#!/usr/bin/env python3
"""tarjeta.py — tarjeta de 1200 × 630 con la marca para un curso, una charla o un proyecto.

Sirve dos veces: como imagen del listado (image: en el front matter) y como imagen al
compartir la página en redes. El texto va en trazos (no depende de tener la fuente).

    python3 recursos/marca/fuente/tarjeta.py \
        --antetitulo "Curso · 2026-2" --titulo "PSIM" \
        --subtitulo "Procesamiento Digital de Imágenes Médicas" \
        -o cursos/psim/tarjeta.png

Escribe el .svg y, si hay Playwright con Chromium, también el .png (el que piden las redes).
"""
import argparse, base64, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from construir_marca import T, F_EXTRA, F_MEDIO, MODOS, g_motivo, svg_de, svg_doc, trazar, ancho, fmt

W, H = 1200, 630
X0 = 72


def partir(texto, fuente, tam, max_ancho, max_lineas):
    """Corta en palabras para que cada línea quepa en max_ancho; la última se acorta con «…»."""
    palabras, lineas, actual = texto.split(), [], ''
    for p in palabras:
        prueba = (actual + ' ' + p).strip()
        if ancho(prueba, fuente, tam) <= max_ancho or not actual:
            actual = prueba
        else:
            lineas.append(actual); actual = p
    if actual:
        lineas.append(actual)
    if len(lineas) > max_lineas:
        lineas = lineas[:max_lineas]
        while ancho(lineas[-1] + '…', fuente, tam) > max_ancho and ' ' in lineas[-1]:
            lineas[-1] = lineas[-1].rsplit(' ', 1)[0]
        lineas[-1] += '…'
    return lineas


def tarjeta(titulo, subtitulo='', antetitulo='', modo='noche'):
    C = MODOS[modo]
    fondo = T['noche'] if modo == 'noche' else (T['blanco'] if modo == 'claro' else T['sala'])
    acento = T['dato-luz'] if modo != 'claro' else T['dato-d']
    partes = [f'<rect width="{W}" height="{H}" fill="{fondo}"/>']
    y = 104
    if antetitulo:
        p, _ = trazar(antetitulo, F_MEDIO, 30, X0, y, color=acento)
        partes.append(p); y += 30
    # Título: hasta dos líneas; baja de tamaño si no cabe.
    for tam in (104, 92, 80, 68, 58):
        lineas = partir(titulo, F_EXTRA, tam, W - 2 * X0, 2)
        if all(ancho(l, F_EXTRA, tam) <= W - 2 * X0 for l in lineas) and not lineas[-1].endswith('…'):
            break
    paso = tam * 1.06
    y += tam * 0.98
    for l in lineas:
        p, _ = trazar(l, F_EXTRA, tam, X0 - tam * 0.04, y, tracking=-0.01, word=-0.04, color=C['tinta'])
        partes.append(p); y += paso
    if subtitulo:
        y += 4
        for l in partir(subtitulo, F_MEDIO, 34, W - 2 * X0, 2):
            p, _ = trazar(l, F_MEDIO, 34, X0, y, color=C['tenue'] if modo == 'claro' else T['luz'])
            partes.append(p); y += 42
    # Motivo abajo a la derecha (ocupa el ancho que deja libre el texto).
    esc = 0.5
    mx, my = W - 1500 * esc - 40, H - 340 * esc - 34
    partes.append(f'<g transform="translate({fmt(mx)} {fmt(my)}) scale({esc})">{svg_de(g_motivo(), modo if modo != "claro" else "claro")}</g>')
    return svg_doc(''.join(partes), W, H, titulo)


def exportar_png(svg_ruta, png_ruta):
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return False
    datos = base64.b64encode(Path(svg_ruta).read_bytes()).decode()
    with sync_playwright() as p:
        b = p.chromium.launch(); pg = b.new_page(viewport={'width': W, 'height': H})
        pg.set_content(f'<html><body style="margin:0"><img src="data:image/svg+xml;base64,{datos}" width="{W}" height="{H}" style="display:block"></body></html>')
        pg.wait_for_timeout(80); pg.screenshot(path=str(png_ruta)); b.close()
    return True


def main():
    a = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    a.add_argument('--titulo', required=True)
    a.add_argument('--subtitulo', default='')
    a.add_argument('--antetitulo', default='')
    a.add_argument('--modo', default='noche', choices=['noche', 'oscuro', 'claro'])
    a.add_argument('-o', '--salida', required=True, help='ruta .png o .svg (se escriben ambas si se puede)')
    x = a.parse_args()
    salida = Path(x.salida)
    salida.parent.mkdir(parents=True, exist_ok=True)
    svg = salida.with_suffix('.svg')
    svg.write_text(tarjeta(x.titulo, x.subtitulo, x.antetitulo, x.modo), encoding='utf-8')
    print('  escrito', svg)
    if exportar_png(svg, salida.with_suffix('.png')):
        print('  escrito', salida.with_suffix('.png'))


if __name__ == '__main__':
    main()
