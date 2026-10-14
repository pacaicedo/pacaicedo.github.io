"""Evaluación: métricas y curva ROC para DVC."""

import json
from pathlib import Path

import pandas as pd
from sklearn.metrics import roc_auc_score, roc_curve

pred = pd.read_csv("data/derived/predicciones.csv")
Path("reports").mkdir(exist_ok=True)
metricas = {
    "auc": round(roc_auc_score(pred["y"], pred["prob"]), 3),
    "exactitud": round(((pred["prob"] >= 0.5) == pred["y"]).mean(), 3),
}
json.dump(metricas, open("reports/metricas.json", "w"), indent=2)
fpr, tpr, _ = roc_curve(pred["y"], pred["prob"])
pd.DataFrame({"fpr": fpr, "tpr": tpr}).to_csv("reports/roc.csv", index=False)
