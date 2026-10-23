"""Figuras de SYSB: componentes de un ECG sintético y convolución discreta."""
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = next(p for p in AQUI.parents if (p / "_quarto.yml").exists())
sys.path[:0] = [str(RAIZ / "recursos/marca/python"), str(RAIZ / "recursos/python")]

import matplotlib.pyplot as plt
import numpy as np
import caicedo_mpl as cm
from datos_ejemplo import ecg_sintetico

FIG = AQUI / "fig"


def main():
    t, limpio, sucio = ecg_sintetico(fs=500, duracion=6)
    deriva = .35 * np.sin(2 * np.pi * .25 * t + .6) + .15 * np.sin(2 * np.pi * .11 * t)
    red = .06 * np.sin(2 * np.pi * 60 * t)

    # Cada figura en versión para documentos (sin sufijo) y para diapositivas (-diapositiva).
    for contexto, sufijo in [("documento", ""), ("diapositiva", "-diapositiva")]:
        k = 1.5 if contexto == "diapositiva" else 1.0
        cm.usar(contexto)
        fig = plt.figure(figsize=(12, 5.8) if k > 1 else (7.2, 5.6))
        rej = fig.add_gridspec(3, 2, width_ratios=[3, 1.4], hspace=.85 if k > 1 else .75, wspace=.32)
        a1 = fig.add_subplot(rej[0, :]); a2 = fig.add_subplot(rej[1, :], sharex=a1)
        a3 = fig.add_subplot(rej[2, 0], sharex=a1); a4 = fig.add_subplot(rej[2, 1])
        a1.plot(t, limpio); a1.set_title("ECG sintético sin contaminar")
        a2.plot(t, sucio); a2.set_title("El mismo ECG con deriva, red de 60 Hz y ruido")
        a3.plot(t, deriva); a3.set_title("Deriva de línea base (< 1 Hz)")
        corto = t < .1
        a4.plot(t[corto] * 1000, red[corto], color=cm.T["grafo"]); a4.set_title("Red: 60 Hz (0,1 s)")
        for ax in (a1, a2, a3, a4):
            ax.set_ylabel("mV")
        a3.set_xlabel("Tiempo (s)"); a4.set_xlabel("Tiempo (ms)"); a4.set_ylabel("")
        a1.set_xlim(0, 6)
        plt.setp(a1.get_xticklabels(), visible=False); plt.setp(a2.get_xticklabels(), visible=False)
        cm.guardar(fig, FIG / f"ecg-componentes{sufijo}"); plt.close(fig)

        # Convolución discreta: x = [1, 2, 1], h = [1, 1]  ->  y = [1, 3, 3, 1]
        x, h = np.array([1, 2, 1]), np.array([1, 1])
        y = np.convolve(x, h)
        cm.usar(contexto)
        fig, ejes = plt.subplots(1, 3, figsize=(7.6 * 1.35, 2.4 * 1.45) if k > 1 else (7.6, 2.4), sharey=True)
        for ax, (nom, s) in zip(ejes, [("x[n]", x), ("h[n]", h), ("y[n] = (x * h)[n]", y)]):
            n = np.arange(len(s))
            ax.vlines(n, 0, s, color=cm.T["dato"], lw=2 * k)
            ax.plot(n, s, "o", color=cm.T["dato"], ms=7 * k, mec=cm.FONDO["claro"], mew=2)
            for ni, si in zip(n, s):
                ax.annotate(f"{si:g}", (ni, si), xytext=(0, 6), textcoords="offset points", ha="center", fontsize=9 * k)
            ax.set_title(nom, loc="center"); ax.set_xticks(range(4)); ax.set_xlim(-.6, 3.6); ax.set_ylim(0, 3.8)
            ax.set_xlabel("n"); ax.grid(axis="x", visible=False)
        cm.guardar(fig, FIG / f"convolucion{sufijo}"); plt.close(fig)

if __name__ == "__main__":
    main()
