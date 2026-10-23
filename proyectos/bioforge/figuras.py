"""Figura de BioForge: el flujo de datos (también la usa la charla de reproducibilidad)."""
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = next(p for p in AQUI.parents if (p / "_quarto.yml").exists())
sys.path[:0] = [str(RAIZ / "recursos/marca/python"), str(RAIZ / "recursos/python")]

import matplotlib.pyplot as plt
import caicedo_mpl as cm
from diagramas import flujo_bioforge

FIG = AQUI / "fig"


def main():
    fig = flujo_bioforge("documento", "claro"); cm.guardar(fig, FIG / "flujo"); plt.close(fig)
    fig = flujo_bioforge("diapositiva", "claro"); cm.guardar(fig, FIG / "flujo-diapositiva"); plt.close(fig)


if __name__ == "__main__":
    main()
