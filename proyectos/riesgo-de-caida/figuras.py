"""Riesgo de caída y parámetros de marcha: el análisis completo sobre datos SIMULADOS.

Flujo: ICC(2,1) por parámetro -> promedio de las 5 marchas por participante ->
estandarización -> regresión logística de Firth (un parámetro a la vez, OR por 1 DE) ->
IC 95 % por bootstrap de participantes -> p por razón de verosimilitud penalizada ->
corrección de Benjamini-Hochberg. Escribe fig/fiabilidad, fig/asociaciones y _tabla-resultados.md.
"""
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = next(p for p in AQUI.parents if (p / "_quarto.yml").exists())
sys.path[:0] = [str(RAIZ / "recursos/marca/python"), str(RAIZ / "recursos/python")]

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats
import caicedo_mpl as cm
from datos_ejemplo import marcha_sintetica

FIG = AQUI / "fig"
B = 2000  # remuestreos bootstrap


def icc_2_1(m):
    """ICC(2,1) de Shrout y Fleiss: efectos aleatorios de dos vías, acuerdo absoluto, una medida.
    m: matriz participantes x ensayos."""
    n, k = m.shape
    gran = m.mean()
    msr = k * ((m.mean(axis=1) - gran) ** 2).sum() / (n - 1)
    msc = n * ((m.mean(axis=0) - gran) ** 2).sum() / (k - 1)
    sse = ((m - m.mean(axis=1, keepdims=True) - m.mean(axis=0, keepdims=True) + gran) ** 2).sum()
    mse = sse / ((n - 1) * (k - 1))
    return (msr - mse) / (msr + (k - 1) * mse + k * (msc - mse) / n)


def firth(X, y, libres=None, iteraciones=100, tol=1e-9):
    """Regresión logística con la penalización de Firth (1993).

    libres: índices de los coeficientes que se estiman (los demás quedan en 0). La penalización
    usa siempre la información del modelo completo, como en la prueba de razón de verosimilitud
    penalizada de Heinze y Schemper (2002). Devuelve (beta, logverosimilitud penalizada).
    """
    k = X.shape[1]
    libres = np.arange(k) if libres is None else np.asarray(libres)
    b = np.zeros(k)
    for _ in range(iteraciones):
        p = 1 / (1 + np.exp(-X @ b)); w = p * (1 - p)
        info = X.T @ (X * w[:, None])
        inv = np.linalg.inv(info)
        xw = X * np.sqrt(w)[:, None]
        h = np.einsum("ij,jk,ik->i", xw, inv, xw)
        u = X.T @ (y - p + h * (.5 - p))
        paso = np.linalg.solve(info[np.ix_(libres, libres)], u[libres])
        paso = np.clip(paso, -5, 5)
        b[libres] += paso
        if np.abs(paso).max() < tol:
            break
    p = np.clip(1 / (1 + np.exp(-X @ b)), 1e-12, 1 - 1e-12)
    info = X.T @ (X * (p * (1 - p))[:, None])
    ll = (y * np.log(p) + (1 - y) * np.log(1 - p)).sum() + .5 * np.linalg.slogdet(info)[1]
    return b, ll


def benjamini_hochberg(p):
    p = np.asarray(p); n = p.size
    orden = np.argsort(p)
    q = p[orden] * n / np.arange(1, n + 1)
    q = np.minimum.accumulate(q[::-1])[::-1]
    salida = np.empty(n); salida[orden] = np.minimum(q, 1)
    return salida


def analizar():
    largo, part = marcha_sintetica()
    clasificados = part[part.sppb != "sin clasificar"]
    y = (clasificados.set_index("participante").sppb == "riesgo").astype(float)
    rng = np.random.default_rng(2026)
    filas = []
    for parametro, d in largo.groupby("parametro", sort=False):
        m = d.pivot(index="participante", columns="ensayo", values="valor").loc[y.index].values
        icc = icc_2_1(m)
        x = m.mean(axis=1)
        z = (x - x.mean()) / x.std(ddof=1)
        X = np.column_stack([np.ones_like(z), z])
        b, ll = firth(X, y.values)
        _, ll0 = firth(X, y.values, libres=[0])   # pendiente fija en 0, misma penalización
        p = stats.chi2.sf(2 * (ll - ll0), 1)
        boot = []
        for _ in range(B):
            i = rng.integers(0, len(z), len(z))
            boot.append(firth(X[i], y.values[i])[0][1])
        lo, hi = np.exp(np.percentile(boot, [2.5, 97.5]))
        filas.append(dict(parametro=parametro, icc=icc, OR=np.exp(b[1]), lo=lo, hi=hi, p=p))
    r = pd.DataFrame(filas)
    r["q"] = benjamini_hochberg(r.p)
    return r, int(y.sum()), int((1 - y).sum())


def fig_fiabilidad(r):
    cm.usar("documento")
    r = r.sort_values("icc")
    fig, ax = plt.subplots(figsize=(6.6, 4.6))
    for x0, x1, txt in [(0, .5, "pobre"), (.5, .75, "moderada"), (.75, .9, "buena"), (.9, 1, "excelente")]:
        ax.text((x0 + x1) / 2, len(r) - .1, txt, ha="center", va="bottom", fontsize=8.5, color=cm.TENUE["claro"])
        ax.axvline(x0, color=cm.REJILLA["claro"], lw=1.2, zorder=0)
    baja = r.icc < .5
    yy = np.arange(len(r))
    ax.scatter(r.icc[~baja], yy[~baja], s=48, color=cm.T["dato"], zorder=3, label="ICC ≥ 0,5")
    ax.scatter(r.icc[baja], yy[baja], s=48, facecolor=cm.FONDO["claro"], edgecolor=cm.T["dato-d"], lw=1.6, zorder=3,
               label="ICC < 0,5: interpretar con cautela")
    ax.set_yticks(yy, r.parametro); ax.set_xlim(0, 1); ax.set_ylim(-.7, len(r) + .3)
    ax.grid(axis="y", visible=False)
    ax.set_xlabel("ICC(2,1) entre las 5 marchas")
    ax.set_title("Repetibilidad de cada parámetro", pad=16)
    ax.legend(loc="center left", fontsize=8.5)
    cm.guardar(fig, FIG / "fiabilidad"); plt.close(fig)


def fig_asociaciones(r):
    cm.usar("documento")
    r = r.sort_values("OR")
    fig, ax = plt.subplots(figsize=(7.2, 4.8))
    yy = np.arange(len(r))
    sig = (r.q < .05).values
    ax.axvline(1, color=cm.TENUE["claro"], lw=1)
    ax.hlines(yy, r.lo, r.hi, color=np.where(sig, cm.T["dato-d"], cm.TENUE["claro"]), lw=1.8)
    ax.scatter(r.OR[sig], yy[sig], s=52, color=cm.T["dato-d"], zorder=3, label="q < 0,05 (BH)")
    ax.scatter(r.OR[~sig], yy[~sig], s=52, facecolor=cm.FONDO["claro"], edgecolor=cm.TENUE["claro"], lw=1.6, zorder=3,
               label="q ≥ 0,05")
    ax.set_xscale("log")
    ax.set_xticks([.0625, .125, .25, .5, 1, 2, 4], ["1/16", "1/8", "1/4", "1/2", "1", "2", "4"]); ax.minorticks_off()
    ax.set_xlim(.04, 12)
    for yi, q in zip(yy, r.q):
        ax.text(11.4, yi, f"q = {q:.3f}".replace(".", ","), va="center", ha="right", fontsize=8.5, color=cm.TENUE["claro"])
    ax.set_yticks(yy, r.parametro); ax.grid(axis="y", visible=False)
    ax.set_xlabel("OR por 1 DE (IC 95 % bootstrap), escala logarítmica")
    ax.set_title("Asociación de cada parámetro con el riesgo de caída")
    ax.legend(loc="upper left", fontsize=8.5)
    cm.guardar(fig, FIG / "asociaciones"); plt.close(fig)


def tabla(r, n_riesgo, n_sin):
    r = r.sort_values("q")
    c = lambda v, d=2: f"{v:.{d}f}".replace(".", ",")
    lineas = ["| Parámetro | ICC(2,1) | OR por 1 DE | IC 95 % | p | q (BH) |",
              "|:--|--:|--:|--:|--:|--:|"]
    for _, f in r.iterrows():
        lineas.append(f"| {f.parametro} | {c(f.icc)} | {c(f.OR)} | {c(f.lo)} a {c(f.hi)} | {c(f.p, 3)} | {c(f.q, 3)} |")
    lineas.append("")
    lineas.append(f": Resultados con datos simulados: {n_riesgo} participantes con riesgo y {n_sin} sin riesgo, "
                  f"{B} remuestreos bootstrap. {{#tbl-resultados}}")
    (AQUI / "_tabla-resultados.md").write_text("\n".join(lineas) + "\n", encoding="utf-8")


def main():
    r, n_riesgo, n_sin = analizar()
    fig_fiabilidad(r)
    fig_asociaciones(r)
    tabla(r, n_riesgo, n_sin)


if __name__ == "__main__":
    main()
