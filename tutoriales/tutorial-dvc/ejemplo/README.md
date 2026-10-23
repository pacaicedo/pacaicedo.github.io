# Ejemplo del tutorial de DVC

`riesgo-caida/` es un proyecto con señales sEMG sintéticas y un pipeline de cuatro etapas
(preprocesamiento, análisis, modelado, evaluación) declarado en `dvc.yaml`.

`demo.sh` recorre todo el tutorial en una carpeta temporal `trabajo/`: `dvc init`, `dvc add`,
un remote local, `push`, `repro`, cambio de parámetros, experimentos y `pull` desde un clon.
Guarda la salida de cada paso en `salidas/`.

`demo-dropbox.sh` hace el mismo recorrido del tutorial con Dropbox: usa `~/Dropbox/beos-dvc` como remote
(con un `HOME` simulado dentro de `trabajo/`) y simula la sincronización de Dropbox copiando la carpeta
a un segundo `HOME` antes del `dvc pull`.

```bash
uv venv
uv pip install "dvc[ssh]" pandas scipy scikit-learn pyarrow pyyaml
bash demo.sh            # remote local (versión SSH)
bash demo-dropbox.sh    # remote en una carpeta de Dropbox
```

Probado con DVC 3.67.1 en Python 3.13 y 3.14.
