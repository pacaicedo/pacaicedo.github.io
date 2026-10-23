"""caicedo_mpl — figuras de matplotlib con la marca P. E. Caicedo-Rodríguez (v2.1).

Archivo generado por fuente/construir_marca.py: los colores salen de la misma tabla de
tokens que los .scss y los .sty.

Uso:
    import sys; sys.path.insert(0, "recursos/marca/python")   # ruta a esta carpeta
    import caicedo_mpl as cm
    cm.usar()                              # documentos y sitio, fondo blanco
    cm.usar("diapositiva")                 # letra más grande, para revealjs y beamer
    cm.usar("diapositiva", modo="oscuro")  # para el modo sala oscura
    fig, ax = plt.subplots()
    ax.plot(t, x)                          # primera serie: dato; segunda: grafo; tercera: causa
    cm.guardar(fig, "fig/senal")           # fig/senal.svg (web) y fig/senal.pdf (LaTeX)

Reglas (las mismas del manual):
- Series en orden fijo: dato (turquesa), grafo (violeta), causa (naranja). Más de tres
  series en un mismo gráfico se agrupan («Otras») o se separan en paneles.
- El naranja es la causa: si una serie es el efecto o la intervención, va en naranja.
- El texto nunca lleva el color de la serie: etiquetas y leyendas en tinta o tenue.
- Imágenes médicas en gris (cmap="gray"); magnitudes en CMAP_SECUENCIAL (un solo tono);
  diferencias con signo en CMAP_DIVERGENTE (dos tonos y gris en el centro).
"""
import logging
from pathlib import Path

import matplotlib as mpl
from matplotlib import font_manager
from matplotlib.colors import LinearSegmentedColormap

T = {
    'tinta':      '#14173A',  # títulos, texto de diapositivas, isotipo (17.3:1 sobre blanco)
    'texto':      '#1D2142',  # texto corrido de documentos y sitio (15.6:1)
    'tenue':      '#4D5375',  # metadatos, pies, leyendas (7.5:1)
    'filete':     '#C9CEDF',  # filetes decorativos, nunca para información
    'papel':      '#F3F5FA',  # fondo de código, callouts y citas
    'blanco':     '#FFFFFF',
    'dato-d':     '#0B626D',  # dato, texto sobre claro (7.0:1)
    'dato':       '#13A3BA',  # dato, rellenos y trazos
    'dato-luz':   '#1EC6AE',  # dato, sobre oscuro (8.6:1)
    'grafo-d':    '#7435BD',  # grafo, texto sobre claro (7.0:1)
    'grafo':      '#9257E0',  # grafo, rellenos y trazos
    'grafo-luz':  '#C29FFE',  # grafo, sobre oscuro (8.5:1)
    'causa-d':    '#8B4606',  # causa, texto sobre claro (7.1:1)
    'causa':      '#D4820E',  # causa, rellenos y trazos
    'causa-luz':  '#F89B24',  # causa, sobre oscuro (8.5:1)
    'aviso-d':    '#B5041D',  # aviso, texto sobre claro (7.0:1)
    'aviso':      '#DB383B',  # aviso, rellenos y trazos
    'aviso-luz':  '#FE928A',  # aviso, sobre oscuro (8.5:1)
    'sala':       '#111419',  # fondo del modo sala oscura (neutro: no tiñe las imágenes en gris)
    'sala-2':     '#1B1F27',  # código y callouts sobre sala
    'noche':      '#1B1D4A',  # campo de marca: separadores, portada del sitio, barra de navegación
    'noche-2':    '#262A63',  # superficie sobre noche
    'luz':        '#EEF1F6',  # texto sobre oscuro (16.3:1 sobre sala)
    'tenue-luz':  '#A9B0C8',  # metadatos sobre oscuro (8.6:1)
    'filete-luz': '#3B4256',  # filetes sobre oscuro
}

# Series categóricas, validadas para daltonismo (todas las parejas, OKLab ΔE >= 13 en
# deuteranopía y >= 3:1 contra el fondo). En oscuro el naranja baja un paso para quedar
# dentro de la banda de luminosidad.
SERIES = {"claro": [T["dato"], T["grafo"], T["causa"]],
          "oscuro": [T["dato"], T["grafo"], "#C97A07"]}
FONDO = {"claro": T["blanco"], "oscuro": T["sala"]}
TINTA = {"claro": T["tinta"], "oscuro": T["luz"]}
TENUE = {"claro": T["tenue"], "oscuro": T["tenue-luz"]}
REJILLA = {"claro": "#E4E7EF", "oscuro": "#2A2F3A"}
# Un acento para resaltar una sola cosa (texto incluido) y el gris para lo demás.
ACENTO = {"claro": T["dato-d"], "oscuro": T["dato-luz"]}
CAUSA = {"claro": T["causa-d"], "oscuro": T["causa-luz"]}
AVISO = {"claro": T["aviso-d"], "oscuro": T["aviso-luz"]}

CMAP_SECUENCIAL = LinearSegmentedColormap.from_list(
    "caicedo_dato", ["#EAF5F8", T["dato"], T["dato-d"], "#06353B"])
CMAP_DIVERGENTE = LinearSegmentedColormap.from_list(
    "caicedo_divergente", [T["dato-d"], T["dato"], "#E9ECF2", T["causa"], T["causa-d"]])
for _c in (CMAP_SECUENCIAL, CMAP_DIVERGENTE):
    try:
        mpl.colormaps.register(_c)
    except ValueError:
        pass

_TAMANOS = {  # contexto: (texto, títulos, marcas)
    "documento": (9.5, 10.5, 1.0),
    "diapositiva": (15.0, 17.0, 1.5),
}


def registrar_fuentes(carpeta=None):
    """Registra Atkinson Hyperlegible Next y Mono desde recursos/marca/fuentes/."""
    carpeta = Path(carpeta) if carpeta else Path(__file__).resolve().parent.parent / "fuentes"
    for f in sorted(carpeta.glob("AtkinsonHyperlegible*.ttf")) + sorted(carpeta.glob("DejaVuSans*.ttf")):
        try:
            font_manager.fontManager.addfont(str(f))
        except Exception:
            pass


def usar(contexto="documento", modo="claro"):
    """Aplica la marca a matplotlib. contexto: documento | diapositiva; modo: claro | oscuro."""
    registrar_fuentes()
    # DejaVu (respaldo) no tiene pesos 500 ni 800: matplotlib avisa en cada figura; no hace falta.
    logging.getLogger("matplotlib.font_manager").setLevel(logging.ERROR)
    t, ti, k = _TAMANOS[contexto]
    tinta, tenue, rejilla, fondo = TINTA[modo], TENUE[modo], REJILLA[modo], FONDO[modo]
    mpl.rcParams.update({
        # Lista de familias: lo que Atkinson no trae (subíndices, griego, flechas) sale de DejaVu.
        "font.family": ["Atkinson Hyperlegible Next", "DejaVu Sans"],
        "font.sans-serif": ["Atkinson Hyperlegible Next", "DejaVu Sans"],
        "font.monospace": ["Atkinson Hyperlegible Mono", "DejaVu Sans Mono"],
        "font.weight": 500 if contexto == "diapositiva" else 400,
        "font.size": t,
        "mathtext.fontset": "dejavusans",
        "text.color": tinta,
        "axes.labelcolor": tinta,
        "axes.titlesize": ti, "axes.titleweight": 800, "axes.titlelocation": "left", "axes.titlepad": 10,
        "axes.labelsize": t, "axes.labelweight": 500,
        "axes.facecolor": fondo, "figure.facecolor": fondo, "savefig.facecolor": fondo,
        "axes.edgecolor": tenue, "axes.linewidth": 0.8 * k,
        "axes.spines.top": False, "axes.spines.right": False,
        "axes.grid": True, "axes.grid.which": "major", "axes.axisbelow": True,
        "grid.color": rejilla, "grid.linewidth": 0.8 * k, "grid.linestyle": "-",
        "axes.prop_cycle": mpl.cycler(color=SERIES[modo]),
        "xtick.color": tenue, "ytick.color": tenue, "xtick.labelcolor": tenue, "ytick.labelcolor": tenue,
        "xtick.labelsize": t * 0.92, "ytick.labelsize": t * 0.92,
        "xtick.major.width": 0.8 * k, "ytick.major.width": 0.8 * k, "xtick.major.size": 3.5 * k, "ytick.major.size": 3.5 * k,
        "lines.linewidth": 1.6 * k, "lines.solid_capstyle": "round", "lines.solid_joinstyle": "round",
        "lines.markersize": 6 * k, "lines.markeredgewidth": 0,
        "patch.linewidth": 0, "patch.edgecolor": fondo,
        "legend.frameon": False, "legend.fontsize": t * 0.92, "legend.labelcolor": tinta, "legend.handlelength": 1.4,
        "image.cmap": "gray", "image.interpolation": "nearest",
        "figure.dpi": 110, "savefig.dpi": 220, "savefig.bbox": "tight", "savefig.pad_inches": 0.06,
        "svg.fonttype": "path",   # texto en trazos: el SVG se ve igual dentro de <img>, sin la fuente
        "pdf.fonttype": 42,       # TrueType incrustada en el PDF
        "svg.hashsalt": "caicedo",  # identificadores estables: el SVG no cambia si la figura no cambia
    })


def guardar(fig, ruta, formatos=("svg", "pdf"), **kw):
    """Guarda la figura creando la carpeta.

    Sin extensión (guardar(fig, "fig/senal")) escribe fig/senal.svg y fig/senal.pdf: en el qmd
    se enlaza ![](fig/senal) y la opción default-image-extension de cada formato elige
    (svg en HTML y revealjs, pdf en PDF y beamer). Con extensión escribe solo ese archivo.
    """
    ruta = Path(ruta)
    ruta.parent.mkdir(parents=True, exist_ok=True)
    sin_fecha = {"svg": {"Date": None}, "pdf": {"CreationDate": None, "ModDate": None}}
    destinos = [ruta] if ruta.suffix else [ruta.with_suffix("." + f) for f in formatos]
    for destino in destinos:
        extra = {"metadata": sin_fecha[destino.suffix[1:]]} if destino.suffix[1:] in sin_fecha else {}
        fig.savefig(destino, **{**extra, **kw})
    return destinos
