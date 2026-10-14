"""Modelado: bosque aleatorio con validación cruzada por participante."""

import json
from pathlib import Path

import joblib
import pandas as pd
import yaml
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import StratifiedKFold, cross_val_predict

p = yaml.safe_load(open("params.yaml"))["modelado"]
tabla = pd.read_csv("data/derived/caracteristicas.csv")
X = tabla[["rms_medio", "rms_max", "frecuencia_mediana"]]
y = tabla["riesgo_caida"]
modelo = RandomForestClassifier(
    n_estimators=p["n_arboles"], max_depth=p["profundidad"], random_state=p["semilla"]
)
cv = StratifiedKFold(n_splits=p["pliegues"], shuffle=True, random_state=p["semilla"])
prob = cross_val_predict(modelo, X, y, cv=cv, method="predict_proba")[:, 1]
Path("data/derived").mkdir(exist_ok=True)
pd.DataFrame({"participante": tabla["participante"], "y": y, "prob": prob}).to_csv(
    "data/derived/predicciones.csv", index=False
)
joblib.dump(modelo.fit(X, y), "data/derived/modelo.joblib")
