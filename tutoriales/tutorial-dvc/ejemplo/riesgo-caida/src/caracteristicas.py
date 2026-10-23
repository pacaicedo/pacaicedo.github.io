"""Análisis: una fila de características por participante."""

from pathlib import Path

import pandas as pd
from scipy import signal

filas = []
for archivo in sorted(Path("data/curated").glob("*.parquet")):
    df = pd.read_parquet(archivo)
    f, pxx = signal.welch(df["ta_limpia"].to_numpy(), fs=2000, nperseg=1024)
    acumulada = pxx.cumsum() / pxx.sum()
    filas.append({
        "participante": archivo.stem[:4],
        "rms_medio": df["ta_rms"].mean(),
        "rms_max": df["ta_rms"].max(),
        "frecuencia_mediana": f[(acumulada >= 0.5).argmax()],
        "riesgo_caida": df["riesgo_caida"].iloc[0],
    })
tabla = pd.DataFrame(filas).groupby("participante").mean().reset_index()
Path("data/derived").mkdir(parents=True, exist_ok=True)
tabla.to_csv("data/derived/caracteristicas.csv", index=False)
