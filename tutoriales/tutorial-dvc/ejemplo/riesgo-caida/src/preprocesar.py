"""Preprocesamiento: pasabanda, notch y envolvente RMS de cada archivo."""

from pathlib import Path

import numpy as np
import pandas as pd
import yaml
from scipy import signal

p = yaml.safe_load(open("params.yaml"))["preprocesamiento"]
fs = p["fs_hz"]
b, a = signal.butter(4, [p["pasabanda_hz"][0], p["pasabanda_hz"][1]], btype="band", fs=fs)
bn, an = signal.iirnotch(p["notch_hz"], 30, fs=fs)
ventana = int(p["rms_ms"] * fs / 1000)

salida = Path("data/curated")
salida.mkdir(parents=True, exist_ok=True)
for archivo in sorted(Path("data/raw").glob("*.csv")):
    df = pd.read_csv(archivo)
    x = signal.filtfilt(bn, an, signal.filtfilt(b, a, df["ta_mv"].to_numpy()))
    rms = np.sqrt(np.convolve(x**2, np.ones(ventana) / ventana, mode="same"))
    df.assign(ta_limpia=x, ta_rms=rms).to_parquet(salida / f"{archivo.stem}.parquet")
