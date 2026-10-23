"""Figuras de la charla «Imágenes médicas: ver el cuerpo como dato» (fantoma sintético)."""
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = next(p for p in AQUI.parents if (p / "_quarto.yml").exists())
sys.path[:0] = [str(RAIZ / "recursos/marca/python"), str(RAIZ / "recursos/python")]

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Rectangle
import caicedo_mpl as cm
from datos_ejemplo import fantoma_uh, ventana

FIG = AQUI / "fig"


def matriz(contexto, modo, nombre):
    cm.usar(contexto, modo)
    uh = fantoma_uh(256, ruido=4)
    w, l = 80, 40
    f0, c0, n = 124, 118, 8  # recorte de 8 x 8 en el borde de un ventrículo (LCR y cerebro)
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(9.6, 4.4), gridspec_kw={"width_ratios": [1, 1]})
    a1.imshow(ventana(uh, w, l), vmin=0, vmax=1)
    a1.add_patch(Rectangle((c0 - .5, f0 - .5), n, n, fill=False, ec=cm.T["causa"], lw=2.2))
    a1.set_title("Corte (ventana de cerebro)", loc="center"); a1.axis("off")
    rec = uh[f0:f0 + n, c0:c0 + n]
    a2.imshow(ventana(rec, w, l), vmin=0, vmax=1)
    for i in range(n):
        for j in range(n):
            g = ventana(rec[i, j], w, l)
            a2.text(j, i, f"{rec[i, j]:.0f}", ha="center", va="center", fontsize=8.5 if contexto == "documento" else 11,
                    color=cm.T["tinta"] if g > .55 else cm.T["luz"])
    a2.set_title("Los mismos píxeles: números en UH", loc="center")
    a2.set_xticks([]); a2.set_yticks([])
    for s in a2.spines.values():
        s.set_visible(True); s.set_color(cm.T["causa"]); s.set_linewidth(2.2)
    cm.guardar(fig, FIG / nombre); plt.close(fig)


def perfil(contexto, modo, nombre):
    cm.usar(contexto, modo)
    uh = fantoma_uh(256, ruido=4)
    fila = 128
    fig, ax = plt.subplots(figsize=(9.6, 3.6))
    ax.axhspan(0, 80, color=cm.T["dato"], alpha=.10, lw=0)
    ax.plot(np.arange(256), uh[fila])
    ax.set_ylim(-60, 140); ax.set_xlim(20, 236)
    ax.text(232, 72, "ventana de cerebro (0 a 80 UH)", ha="right", va="top", fontsize=9 if contexto == "documento" else 12,
            color=cm.TENUE[modo])
    ax.set_xlabel("Columna (píxel)"); ax.set_ylabel("UH")
    ax.set_title("Perfil de intensidad de la fila central")
    cm.guardar(fig, FIG / nombre); plt.close(fig)


def main():
    for modo in ("claro", "oscuro"):
        sufijo = "" if modo == "claro" else "-oscuro"
        matriz("diapositiva", modo, "matriz" + sufijo)
        perfil("diapositiva", modo, "perfil" + sufijo)


if __name__ == "__main__":
    main()
