#!/usr/bin/env bash
# Ejecuta el flujo completo del tutorial y guarda la salida de cada paso en salidas/.
set -euo pipefail
BASE=$(cd "$(dirname "$0")" && pwd)
[ -d "$BASE/.venv" ] && export PATH="$BASE/.venv/bin:$PATH"
export GIT_AUTHOR_NAME="P. E. Caicedo-Rodríguez" GIT_AUTHOR_EMAIL=pablo@example.org
export GIT_COMMITTER_NAME="$GIT_AUTHOR_NAME" GIT_COMMITTER_EMAIL="$GIT_AUTHOR_EMAIL"
export DVC_NO_ANALYTICS=1
TRABAJO=$BASE/trabajo; OUT=$BASE/salidas
rm -rf "$TRABAJO" "$OUT"; mkdir -p "$TRABAJO" "$OUT"
paso() { local n=$1; shift; { echo "\$ $*"; eval "$@" 2>&1; } | sed "s#$TRABAJO#~#g" > "$OUT/$n.txt"; }

cp -r "$BASE/riesgo-caida" "$TRABAJO/riesgo-caida"; cd "$TRABAJO/riesgo-caida"
git init -q -b main
paso 01-init "dvc init"
python src/generar_datos.py data/raw
paso 02-add "dvc add data/raw"
paso 03-dvcfile "cat data/raw.dvc"
paso 04-gitignore "cat data/.gitignore"
git add .dvc .dvcignore data/raw.dvc data/.gitignore src params.yaml dvc.yaml
git commit -qm "Datos crudos sEMG bajo DVC"
mkdir -p "$TRABAJO/servidor/beos-dvc"
paso 05-remote "dvc remote add -d laboratorio $TRABAJO/servidor/beos-dvc && cat .dvc/config"
git add .dvc/config && git commit -qm "Remote del laboratorio"
paso 06-push "dvc push"
paso 07-repro "dvc repro"
paso 08-metrics "dvc metrics show"
git add dvc.lock reports/metricas.json data/.gitignore data/derived/.gitignore && git commit -qm "Pipeline v1" && git tag datos-v1
paso 09a-push "dvc push"
paso 09-status "dvc status"
python - <<'PY'
import yaml
p = yaml.safe_load(open("params.yaml")); p["preprocesamiento"]["rms_ms"] = 50
yaml.safe_dump(p, open("params.yaml", "w"), sort_keys=False)
PY
paso 10-status-cambio "dvc status"
paso 11-repro-cambio "dvc repro"
paso 12-params-diff "dvc params diff"
paso 13-metrics-diff "dvc metrics diff"
git checkout -q params.yaml dvc.lock reports/metricas.json && dvc checkout -q
paso 14-exp-run "dvc exp run -n arboles-500 --set-param modelado.n_arboles=500"
dvc exp run -q -n profundidad-1 -S modelado.n_arboles=200 -S modelado.profundidad=1 >/dev/null
paso 15-exp-show "dvc exp show --no-pager --md --drop 'Created|data/.*|src/.*|preprocesamiento.*|modelado.(pliegues|semilla)'"
dvc push -q
cd "$TRABAJO"
paso 16-clone "git clone -q riesgo-caida otra-maquina && cd otra-maquina && ls data"
cd otra-maquina
paso 17-pull "dvc pull"
paso 18-ls "ls data/raw | head -4"
