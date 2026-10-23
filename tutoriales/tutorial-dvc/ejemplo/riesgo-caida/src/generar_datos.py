"""Genera señales sEMG sintéticas: un CSV por participante y prueba."""

import sys
from pathlib import Path

import numpy as np
import pandas as pd

destino = Path(sys.argv[1] if len(sys.argv) > 1 else "data/raw")
destino.mkdir(parents=True, exist_ok=True)
rng = np.random.default_rng(2026)
fs = 2000
t = np.arange(0, 5, 1 / fs)
for p in range(1, 21):
    riesgo = p % 3 == 0
    ganancia = rng.normal(0.85 if riesgo else 1.0, 0.15)
    for prueba in (1, 2):
        amplitud = ganancia * rng.normal(1.0, 0.05)
        senal = amplitud * np.sin(2 * np.pi * 80 * t) * (1 + np.sin(2 * np.pi * 1 * t))
        senal += rng.normal(0, 0.3, t.size) + 0.5 * np.sin(2 * np.pi * 60 * t)
        df = pd.DataFrame({"tiempo_s": t, "ta_mv": senal, "riesgo_caida": int(riesgo)})
        df.to_csv(destino / f"P{p:03d}_S01_T{prueba:02d}.csv", index=False)
