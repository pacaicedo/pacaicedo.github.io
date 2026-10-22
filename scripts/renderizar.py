"""Renderiza y verifica el sitio usando una caché dentro del proyecto."""

import os
from pathlib import Path
import shutil
import subprocess
import sys


def main():
    root = Path(__file__).resolve().parents[1]
    quarto = shutil.which("quarto")
    if quarto is None:
        raise SystemExit("Instala Quarto y vuelve a ejecutar este comando.")
    cache = root / ".quarto" / "cache"
    cache.mkdir(parents=True, exist_ok=True)
    environment = os.environ.copy()
    # Quarto can otherwise reuse a read-only user cache in managed environments.
    environment["XDG_CACHE_HOME"] = str(cache)
    subprocess.run([quarto, "render"], cwd=root, env=environment, check=True)
    subprocess.run([sys.executable, str(root / "scripts/verificar_sitio.py")], cwd=root, check=True)


if __name__ == "__main__":
    main()
