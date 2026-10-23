"""Figuras del tutorial «Figuras con la marca»: el mismo gráfico en modo claro y oscuro."""
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = next(p for p in AQUI.parents if (p / "_quarto.yml").exists())
sys.path[:0] = [str(RAIZ / "recursos/marca/python"), str(RAIZ / "recursos/python")]

import matplotlib.pyplot as plt
import numpy as np
from scipy import signal
import caicedo_mpl as cm

FIG = AQUI / "fig"


def respuesta(modo, contexto="documento"):
    cm.usar(contexto, modo)
    fig, ax = plt.subplots(figsize=(6.4, 3.3))
    for orden in (2, 4, 8):
        b, a = signal.butter(orden, 40, fs=500)
        w, h = signal.freqz(b, a, worN=2048, fs=500)
        ax.plot(w, np.abs(h), label=f"Orden {orden}")
    ax.axvline(40, color=cm.TENUE[modo], lw=1)
    ax.annotate("corte: 40 Hz", (40, 1.02), xytext=(5, 0), textcoords="offset points", fontsize=9, color=cm.TENUE[modo])
    ax.set_xlim(0, 120); ax.set_ylim(0, 1.12)
    ax.set_xlabel("Frecuencia (Hz)"); ax.set_ylabel("|H(f)|")
    ax.set_title("Pasa bajos Butterworth: más orden, transición más corta")
    ax.legend(loc="upper right")
    return fig


def main():
    for modo in ("claro", "oscuro"):
        fig = respuesta(modo); cm.guardar(fig, FIG / f"ejemplo-{modo}"); plt.close(fig)


if __name__ == "__main__":
    main()
