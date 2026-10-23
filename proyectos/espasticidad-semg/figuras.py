"""Cuantificación de actividad muscular con sEMG: el pipeline sobre una señal SIMULADA.

Pasabanda 20-450 Hz -> notch de 60 Hz y su tercer armónico -> envolvente (rectificación y
pasa bajos de 8 Hz) y RMS en ventanas de 200 ms -> frecuencias media (MNF) y mediana (MDF)
por contracción. Escribe fig/etapas, fig/espectro y _tabla-metricas.md.
"""
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = next(p for p in AQUI.parents if (p / "_quarto.yml").exists())
sys.path[:0] = [str(RAIZ / "recursos/marca/python"), str(RAIZ / "recursos/python")]

import matplotlib.pyplot as plt
import numpy as np
from scipy import signal
import caicedo_mpl as cm
from datos_ejemplo import semg_sintetico

FIG = AQUI / "fig"
FS = 2000
CONTRACCIONES = [(.6, 1.8), (2.6, 3.6), (4.4, 5.4)]


def procesar(x, fs=FS):
    sos = signal.butter(4, [20, 450], btype="band", fs=fs, output="sos")
    y = signal.sosfiltfilt(sos, x)
    for f0 in (60, 180):
        b, a = signal.iirnotch(f0, Q=30, fs=fs)
        y = signal.filtfilt(b, a, y)
    sos_env = signal.butter(4, 8, btype="low", fs=fs, output="sos")
    envolvente = signal.sosfiltfilt(sos_env, np.abs(y))
    n = int(.2 * fs)
    rms = np.sqrt(np.convolve(y ** 2, np.ones(n) / n, mode="same"))
    return y, envolvente, rms


def frecuencias(y, fs=FS):
    f, p = signal.welch(y, fs=fs, nperseg=256)
    mnf = (f * p).sum() / p.sum()
    acum = np.cumsum(p)
    mdf = f[np.searchsorted(acum, acum[-1] / 2)]
    return f, p, mnf, mdf


def main():
    t, crudo, activacion = semg_sintetico(fs=FS)
    y, env, rms = procesar(crudo)

    cm.usar("documento")
    fig, ejes = plt.subplots(3, 1, figsize=(7.2, 5.6), sharex=True)
    ejes[0].plot(t, crudo, lw=.6); ejes[0].set_title("Señal cruda: deriva por movimiento, red de 60 Hz y actividad")
    ejes[1].plot(t, y, lw=.6); ejes[1].set_title("Pasabanda 20–450 Hz y notch de 60 Hz (y 180 Hz)")
    ejes[2].plot(t, env, label="Envolvente (8 Hz)")
    ejes[2].plot(t, rms, label="RMS (ventanas de 200 ms)")
    ejes[2].set_title("Amplitud de la actividad")
    ejes[2].legend(loc="upper right", ncols=2)
    ejes[2].set_ylim(0, max(env.max(), rms.max()) * 1.45)
    for ax in ejes:
        ax.set_ylabel("mV")
    ejes[2].set_xlabel("Tiempo (s)"); ejes[2].set_xlim(0, 6)
    fig.tight_layout(h_pad=1.0)
    cm.guardar(fig, FIG / "etapas"); plt.close(fig)

    # Espectro de la contracción más fuerte
    sel = (t >= CONTRACCIONES[1][0]) & (t < CONTRACCIONES[1][1])
    f, p, mnf, mdf = frecuencias(y[sel])
    cm.usar("documento")
    fig, ax = plt.subplots(figsize=(7.2, 3.2))
    ax.fill_between(f, p, color=cm.T["dato"], alpha=.10, lw=0)
    ax.plot(f, p)
    for x, nombre, alto in [(mdf, "MDF (mediana)", 1.0), (mnf, "MNF (media)", .86)]:
        ax.axvline(x, color=cm.TINTA["claro"], lw=1)
        ax.annotate(f"{nombre} = {x:.0f} Hz", (x, p.max() * alto), xytext=(6, 0), textcoords="offset points",
                    ha="left", va="center", fontsize=9)
    ax.set_xlim(0, 500); ax.set_ylim(0, p.max() * 1.08)
    ax.set_xlabel("Frecuencia (Hz)"); ax.set_ylabel("DEP (mV²/Hz)")
    ax.set_title("Espectro de la segunda contracción (Welch)")
    cm.guardar(fig, FIG / "espectro"); plt.close(fig)

    c = lambda v, d=0: f"{v:.{d}f}".replace(".", ",")
    filas = ["| Contracción | Intervalo (s) | RMS medio (mV) | MNF (Hz) | MDF (Hz) |", "|:--|--:|--:|--:|--:|"]
    for i, (a, b) in enumerate(CONTRACCIONES, 1):
        s = (t >= a) & (t < b)
        _, _, mnf_i, mdf_i = frecuencias(y[s])
        filas.append(f"| {i} | {c(a, 1)} a {c(b, 1)} | {c(rms[s].mean(), 3)} | {c(mnf_i)} | {c(mdf_i)} |")
    filas += ["", ": Métricas sobre la señal simulada (no describen a ningún paciente). {#tbl-metricas}"]
    (AQUI / "_tabla-metricas.md").write_text("\n".join(filas) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
