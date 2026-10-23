#!/usr/bin/env python3
"""Pre-render del sitio: regenera las figuras de las páginas que cambiaron.

Cada página con figuras tiene un figuras.py junto al qmd que escribe en su carpeta fig/ (y,
si hace falta, archivos _tabla-*.md que el qmd incluye). Aquí se ejecuta cada figuras.py
solo si él, los datos de ejemplo o el estilo de la marca son más nuevos que sus salidas.
Para forzar todo:  python3 recursos/figuras.py --todo
"""
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
COMUNES = [RAIZ / "recursos/python/datos_ejemplo.py", RAIZ / "recursos/marca/python/caicedo_mpl.py"]


def salidas(script):
    carpeta = script.parent
    return [p for p in (carpeta / "fig").glob("*") if p.is_file()] + list(carpeta.glob("_tabla-*.md"))


def desactualizado(script):
    hechas = salidas(script)
    if not hechas:
        return True
    mas_vieja = min(p.stat().st_mtime for p in hechas)
    return any(f.exists() and f.stat().st_mtime > mas_vieja for f in [script, *COMUNES])


def main():
    todo = "--todo" in sys.argv
    for script in sorted(RAIZ.glob("**/figuras.py")):
        partes = script.relative_to(RAIZ).parts
        if partes[0] in ("_site", "recursos") or any(p.startswith(".") for p in partes):
            continue
        if todo or desactualizado(script):
            print("figuras:", script.relative_to(RAIZ), flush=True)
            subprocess.run([sys.executable, str(script)], check=True, cwd=script.parent)


if __name__ == "__main__":
    main()
