"""Figuras de TAU: PCA y k-means sobre parámetros de marcha simulados."""
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = next(p for p in AQUI.parents if (p / "_quarto.yml").exists())
sys.path[:0] = [str(RAIZ / "recursos/marca/python"), str(RAIZ / "recursos/python")]

import matplotlib.pyplot as plt
import numpy as np
import caicedo_mpl as cm
from datos_ejemplo import marcha_sintetica
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

FIG = AQUI / "fig"


def main():
    largo, part = marcha_sintetica()
    medias = largo.groupby(["participante", "parametro"])["valor"].mean().unstack()
    medias = medias.loc[part.loc[part.sppb != "sin clasificar", "participante"]]
    z = StandardScaler().fit_transform(medias.values)
    pca = PCA().fit(z)
    pcs = pca.transform(z)[:, :2]
    grupos = KMeans(n_clusters=2, n_init=20, random_state=0).fit_predict(pcs)

    v = pca.explained_variance_ratio_ * 100
    # Versión para documentos (sin sufijo) y para diapositivas (letra más grande).
    for contexto, sufijo in [("documento", ""), ("diapositiva", "-diapositiva")]:
        dispersion(pcs, grupos, v, contexto, sufijo)
        varianza(v, contexto, sufijo)


def dispersion(pcs, grupos, v, contexto, sufijo):
    cm.usar(contexto)
    grande = contexto == "diapositiva"
    fig, ax = plt.subplots(figsize=(7.4, 5.0) if grande else (5.6, 4.2))
    for g, marca in zip(range(2), ["o", "s"]):
        sel = grupos == g
        ax.scatter(pcs[sel, 0], pcs[sel, 1], s=90 if grande else 46, marker=marca, color=cm.SERIES["claro"][g],
                   edgecolor=cm.FONDO["claro"], linewidth=1.5, label=f"Grupo {g + 1} (k-means)")
    ax.set_xlabel(f"CP1 ({v[0]:.0f} % de la varianza)"); ax.set_ylabel(f"CP2 ({v[1]:.0f} %)")
    ax.set_title("42 participantes simulados en las dos primeras componentes")
    ax.legend(loc="upper right")
    ax.axhline(0, color=cm.TENUE["claro"], lw=.6); ax.axvline(0, color=cm.TENUE["claro"], lw=.6)
    cm.guardar(fig, FIG / f"pca-dispersion{sufijo}"); plt.close(fig)


def varianza(v, contexto, sufijo):
    cm.usar(contexto)
    grande = contexto == "diapositiva"
    fig, ax = plt.subplots(figsize=(7.4, 4.0) if grande else (5.6, 3.2))
    k = np.arange(1, 9)
    ax.bar(k, v[:8], width=.55, color=cm.T["dato"], label="Por componente")
    ax.plot(k, np.cumsum(v)[:8], "o-", color=cm.T["grafo"], ms=9 if grande else 6, mec=cm.FONDO["claro"], mew=1.5,
            label="Acumulada")
    ax.set_xticks(k); ax.set_xlabel("Componente principal"); ax.set_ylabel("Varianza explicada (%)")
    ax.set_ylim(0, 105); ax.grid(axis="x", visible=False)
    ax.set_title("Varianza explicada"); ax.legend(loc="center right")
    cm.guardar(fig, FIG / f"varianza{sufijo}"); plt.close(fig)


if __name__ == "__main__":
    main()
