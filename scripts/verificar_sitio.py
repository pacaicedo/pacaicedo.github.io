"""Comprueba páginas, navegación, secciones y enlaces del sitio renderizado.

Uso: python3 scripts/verificar_sitio.py [directorio_de_salida]
No requiere paquetes externos ni acceso a Internet.
"""

from html.parser import HTMLParser
from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]
SECTIONS = {
    "cursos": [
        "Introducción",
        "Resultados de Aprendizaje",
        "Calendario y fechas importantes",
        "Presentaciones",
        "Laboratorios",
        "Recursos y tutoriales",
        "Referentes",
    ],
    "charlas-y-conferencias": ["Evento", "Presentación", "Código"],
    "proyectos": ["Problema", "Métodos", "Resultados"],
    "herramientas-y-tutoriales": [],
}


class Page(HTMLParser):
    def __init__(self, path):
        super().__init__()
        self.ids = set()
        self.links = []
        self.headings = []
        self.nav_links = []
        self.in_nav = False
        self.in_main = False
        self.heading = None
        self.feed(path.read_text(encoding="utf-8"))

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if "id" in attrs:
            self.ids.add(attrs["id"])
        if tag == "nav" and attrs.get("id") == "quarto-header":
            self.in_nav = True
        # Quarto's navigation is inside a header with this ID.
        if tag == "header" and attrs.get("id") == "quarto-header":
            self.in_nav = True
        if tag == "main":
            self.in_main = True
        for key in ("href", "src", "data-src", "poster"):
            if attrs.get(key):
                self.links.append(attrs[key])
                if self.in_nav and tag == "a" and key == "href":
                    self.nav_links.append(attrs[key])
        if tag == "h2" and self.in_main:
            self.heading = []

    def handle_endtag(self, tag):
        if tag in ("nav", "header"):
            self.in_nav = False
        if tag == "main":
            self.in_main = False
        if tag == "h2" and self.heading is not None:
            self.headings.append(" ".join("".join(self.heading).split()))
            self.heading = None

    def handle_data(self, data):
        if self.heading is not None:
            self.heading.append(data)


def local_target(source, reference, output):
    url = urlsplit(reference)
    if url.scheme or url.netloc:
        return None
    path = unquote(url.path)
    target = output / path.lstrip("/") if path.startswith("/") else source.parent / path
    if not path:
        target = source
    target = target.resolve()
    if target.is_dir():
        target /= "index.html"
    return target, unquote(url.fragment)


def main():
    output = (Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "_site").resolve()
    if not (output / "index.html").is_file():
        raise SystemExit("Falta el sitio generado. Ejecuta primero quarto render.")

    pages = {path: Page(path) for path in output.rglob("*.html")}
    errors = []
    checked_links = 0
    for source, page in pages.items():
        for reference in page.links:
            result = local_target(source, reference, output)
            if result is None:
                continue
            target, fragment = result
            checked_links += 1
            if not target.is_relative_to(output) or not target.is_file():
                errors.append(f"{source.relative_to(output)}: recurso ausente {reference}")
            elif fragment and target in pages and not fragment.startswith(("category=", "/")):
                if fragment not in pages[target].ids:
                    errors.append(f"{source.relative_to(output)}: ancla ausente {reference}")

    expected_nav = {output / "index.html"} | {output / section / "index.html" for section in SECTIONS}
    for section, headings in SECTIONS.items():
        landing = output / section / "index.html"
        if landing not in pages:
            errors.append(f"Falta la página principal de {section}")
        if not headings:
            continue
        for source in sorted((ROOT / section).glob("*/index.qmd")):
            target = output / source.relative_to(ROOT).with_suffix(".html")
            page = pages.get(target)
            if page is None:
                errors.append(f"Falta la página {target.relative_to(output)}")
            elif page.headings != headings:
                errors.append(f"{target.relative_to(output)}: apartados incorrectos {page.headings}")

    for source, page in pages.items():
        # Redirects and Revealjs decks do not carry the site's navigation.
        if "quarto-content" not in page.ids:
            continue
        nav = {local_target(source, link, output)[0] for link in page.nav_links
               if local_target(source, link, output) is not None}
        if not expected_nav.issubset(nav):
            errors.append(f"{source.relative_to(output)}: navegación incompleta")

    for css in output.rglob("*.css"):
        for reference in re.findall(r"url\(\s*['\"]?([^)'\"\s]+)", css.read_text(encoding="utf-8")):
            result = local_target(css, reference, output)
            if result is not None and not result[0].is_file():
                errors.append(f"{css.relative_to(output)}: recurso CSS ausente {reference}")

    if errors:
        raise SystemExit("\n".join(errors))
    print(f"OK: {len(pages)} páginas HTML, {checked_links} enlaces locales, navegación y apartados.")


if __name__ == "__main__":
    main()
