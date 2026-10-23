#!/usr/bin/env python3
"""manifiesto.py — huella SHA-256 de cada archivo de una carpeta de datos originales.

Ejemplo de la charla «Experimentos biomédicos reproducibles». Escribe un manifiesto JSON con
la ruta, el tamaño y el SHA-256 de cada archivo, y comprueba más adelante que nada cambió:

    python3 manifiesto.py crear data/raw manifiesto.json
    python3 manifiesto.py verificar data/raw manifiesto.json
"""
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


def sha256(ruta, bloque=1 << 20):
    h = hashlib.sha256()
    with open(ruta, "rb") as f:
        while trozo := f.read(bloque):
            h.update(trozo)
    return h.hexdigest()


def crear(carpeta, salida):
    carpeta = Path(carpeta)
    archivos = sorted(p for p in carpeta.rglob("*") if p.is_file())
    manifiesto = {
        "creado": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "carpeta": str(carpeta),
        "archivos": [{"ruta": str(p.relative_to(carpeta)), "bytes": p.stat().st_size, "sha256": sha256(p)}
                     for p in archivos],
    }
    Path(salida).write_text(json.dumps(manifiesto, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"{len(archivos)} archivos registrados en {salida}")


def verificar(carpeta, entrada):
    carpeta = Path(carpeta)
    esperado = json.loads(Path(entrada).read_text(encoding="utf-8"))
    problemas = 0
    for a in esperado["archivos"]:
        p = carpeta / a["ruta"]
        if not p.exists():
            print("FALTA      ", a["ruta"]); problemas += 1
        elif sha256(p) != a["sha256"]:
            print("MODIFICADO ", a["ruta"]); problemas += 1
    registrados = {a["ruta"] for a in esperado["archivos"]}
    for p in sorted(q for q in carpeta.rglob("*") if q.is_file()):
        if str(p.relative_to(carpeta)) not in registrados:
            print("NUEVO      ", p.relative_to(carpeta)); problemas += 1
    print("Sin cambios." if problemas == 0 else f"{problemas} diferencias.")
    return problemas


if __name__ == "__main__":
    if len(sys.argv) != 4 or sys.argv[1] not in ("crear", "verificar"):
        sys.exit(__doc__)
    accion, carpeta, archivo = sys.argv[1:]
    if accion == "crear":
        crear(carpeta, archivo)
    else:
        sys.exit(1 if verificar(carpeta, archivo) else 0)
