"""Figuras del tutorial «Filtrado de fase cero» (también las usa SYSB)."""
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = next(p for p in AQUI.parents if (p / "_quarto.yml").exists())
sys.path[:0] = [str(RAIZ / "recursos/marca/python"), str(RAIZ / "recursos/python")]

import matplotlib.pyplot as plt
import numpy as np
import caicedo_mpl as cm
from datos_ejemplo import ecg_sintetico
from scipy import signal

FIG = AQUI / "fig"


def main():
    fs = 500
    t, limpio, sucio = ecg_sintetico(fs=fs, duracion=10)
    b, a = signal.butter(4, [0.5, 40], btype="band", fs=fs)
    causal = signal.lfilter(b, a, sucio)
    fase_cero = signal.filtfilt(b, a, sucio)

    # Versión para documentos (fase-cero) y para diapositivas (fase-cero-diapositiva, la usa SYSB).
    for contexto, sufijo in [("documento", ""), ("diapositiva", "-diapositiva")]:
        cm.usar(contexto)
        grande = contexto == "diapositiva"
        fig, ax = plt.subplots(figsize=(9.6, 4.2) if grande else (7.2, 3.4))
        sel = (t > 4.0) & (t < 5.6)
        ax.plot(t[sel], limpio[sel], color=cm.TENUE["claro"], lw=1.2, label="Referencia sin contaminar")
        ax.plot(t[sel], causal[sel], label="lfilter (causal): la onda R llega tarde")
        ax.plot(t[sel], fase_cero[sel], label="filtfilt (fase cero)")
        ax.set_xlabel("Tiempo (s)"); ax.set_ylabel("mV")
        ax.set_title("Pasabanda Butterworth 0,5–40 Hz de orden 4")
        ax.legend(loc="upper right", fontsize=None if grande else 8.5)
        ax.set_ylim(-.6, 1.75 if grande else 1.6)
        cm.guardar(fig, FIG / f"fase-cero{sufijo}"); plt.close(fig)

    cm.usar("documento")
    f, p_sucio = signal.welch(sucio, fs=fs, nperseg=2048)
    _, p_filt = signal.welch(fase_cero, fs=fs, nperseg=2048)
    fig, ax = plt.subplots(figsize=(7.2, 3.2))
    ax.semilogy(f, p_sucio, label="Antes de filtrar")
    ax.semilogy(f, p_filt, label="Después de filtfilt")
    ax.annotate("red 60 Hz", (60, p_sucio[np.argmin(abs(f - 60))]), xytext=(10, 0), textcoords="offset points",
                fontsize=9, va="center")
    ax.set_xlim(0, 100); ax.set_ylim(1e-8, None); ax.set_xlabel("Frecuencia (Hz)"); ax.set_ylabel("DEP (mV²/Hz)")
    ax.set_title("Densidad espectral de potencia (Welch)")
    ax.legend(loc="upper right")
    cm.guardar(fig, FIG / "espectro"); plt.close(fig)


if __name__ == "__main__":
    main()
