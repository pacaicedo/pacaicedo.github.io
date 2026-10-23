"""Diagramas dibujados con matplotlib y la marca (se exportan a SVG y a PDF)."""
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch
import caicedo_mpl as cm


def flujo_bioforge(contexto="documento", modo="claro"):
    """raw -> curated -> derived -> evidence, con el contrato encima y el manifiesto debajo."""
    cm.usar(contexto, modo)
    tinta, tenue, fondo = cm.TINTA[modo], cm.TENUE[modo], cm.FONDO[modo]
    papel = cm.T["papel"] if modo == "claro" else cm.T["sala-2"]
    etapas = [("data/raw", "originales\nseudonimizados"), ("curated", "normalizados\nsegún el contrato"),
              ("derived", "métricas y\nvariables"), ("evidence", "figuras, tablas\ne informes")]
    bordes = [cm.SERIES[modo][0], cm.SERIES[modo][0], cm.SERIES[modo][1], cm.SERIES[modo][2]]
    t = 1.0 if contexto == "documento" else 1.35
    fig, ax = plt.subplots(figsize=(10, 3.4))
    ax.set_xlim(0, 10); ax.set_ylim(0, 3.4); ax.axis("off")
    ancho, alto, y0 = 2.15, 1.25, 1.05
    xs = [0.15 + i * 2.45 for i in range(4)]
    for x, (titulo, texto), borde in zip(xs, etapas, bordes):
        ax.add_patch(FancyBboxPatch((x, y0), ancho, alto, boxstyle="round,pad=0,rounding_size=0.08",
                                    fc=papel, ec=borde, lw=2.2))
        ax.text(x + .15, y0 + alto - .28, titulo, fontsize=11.5 * t, fontweight=800, color=tinta, va="center",
                family="Atkinson Hyperlegible Mono")
        ax.text(x + .15, y0 + .42, texto, fontsize=9 * t, color=tenue, va="center", linespacing=1.25)
    for x in xs[:-1]:
        ax.add_patch(FancyArrowPatch((x + ancho + .04, y0 + alto / 2), (x + 2.45 - .04, y0 + alto / 2),
                                     arrowstyle="-|>", mutation_scale=16, lw=2, color=tinta))
    ax.annotate("", xy=(9.85, 2.75), xytext=(0.15, 2.75),
                arrowprops=dict(arrowstyle="-", lw=1.2, color=tenue))
    ax.text(0.15, 3.0, "Contrato versionado (YAML / JSON Schema, Pydantic): columnas, unidades y rangos",
            fontsize=9.2 * t, color=tinta, va="center")
    ax.text(0.15, 0.55, "Manifiesto: SHA-256 de cada archivo y versiones del contrato y del código",
            fontsize=9.2 * t, color=tinta, va="center")
    ax.annotate("", xy=(9.85, 0.8), xytext=(0.15, 0.8), arrowprops=dict(arrowstyle="-", lw=1.2, color=tenue))
    return fig
