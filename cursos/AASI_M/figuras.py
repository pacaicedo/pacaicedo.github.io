"""Figuras de PSIM: el fantoma, ventana y nivel, e histograma (fantoma sintético en UH aproximadas)."""
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = next(p for p in AQUI.parents if (p / "_quarto.yml").exists())
sys.path[:0] = [str(RAIZ / "recursos/marca/python"), str(RAIZ / "recursos/python")]

import matplotlib.pyplot as plt
import numpy as np
import caicedo_mpl as cm
from datos_ejemplo import fantoma_uh, shepp_logan, ventana

FIG = AQUI / "fig"
VENTANAS = [("Rango completo", 2000, 0), ("Tejido blando", 400, 40), ("Cerebro", 80, 40)]


def main():
    FIG.mkdir(exist_ok=True)
    plt.imsave(FIG / "fantoma.png", shepp_logan(512), cmap="gray", vmin=0, vmax=1)
    uh = fantoma_uh(256)

    cm.usar("documento")
    fig, ejes = plt.subplots(1, 3, figsize=(8.4, 3.1))
    for ax, (nombre, w, l) in zip(ejes, VENTANAS):
        ax.imshow(ventana(uh, w, l), vmin=0, vmax=1)
        ax.set_title(f"{nombre}\nW {w} · L {l} UH", fontsize=9.5, loc="center", linespacing=1.3)
        ax.axis("off")
    cm.guardar(fig, FIG / "ventanas"); plt.close(fig)

    # Histograma dentro de la cabeza: la ventana de cerebro solo usa una franja estrecha.
    # Versión para documentos (histograma) y para diapositivas (histograma-diapositiva).
    yy, xx = np.mgrid[1:-1:256j, -1:1:256j]
    dentro = uh[(xx / .69) ** 2 + (yy / .92) ** 2 <= 1]
    for contexto, sufijo in [("documento", ""), ("diapositiva", "-diapositiva")]:
        cm.usar(contexto)
        k = 1.5 if contexto == "diapositiva" else 1.0       # escala de figura y de letra
        fig, ax = plt.subplots(figsize=(6.4 * 1.3 if k > 1 else 6.4, 3.0 * 1.3 if k > 1 else 3.0))
        ax.axvspan(0, 80, color=cm.T["dato"], alpha=.10, lw=0)
        cuentas, bordes, _ = ax.hist(dentro[(dentro > -150) & (dentro < 250)], bins=np.arange(-150, 252, 4),
                                     color=cm.T["dato"], rwidth=.8)
        tope = cuentas.max()
        ax.set_ylim(0, tope * 1.25)
        ax.text(40, tope * 1.12, "ventana de cerebro: W 80 · L 40", ha="center", fontsize=8.5 * k,
                color=cm.TINTA["claro"])
        for x, txt in [(5, "LCR"), (35, "cerebro")]:
            y = cuentas[np.searchsorted(bordes, x) - 1]
            ax.annotate(txt, (x, y), xytext=(-8, 2), textcoords="offset points", ha="right", fontsize=8.5 * k,
                        color=cm.TENUE["claro"])
        ax.set_xlabel("Unidades Hounsfield (UH)"); ax.set_ylabel("Píxeles")
        ax.set_title("Histograma del fantoma entre -150 y 250 UH")
        cm.guardar(fig, FIG / f"histograma{sufijo}"); plt.close(fig)

if __name__ == "__main__":
    main()
