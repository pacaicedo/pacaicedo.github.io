# Marca P. E. Caicedo-Rodríguez, versión 2.1

Esta carpeta va en `recursos/marca/` del proyecto Quarto. Las rutas de los ejemplos son relativas a la raíz del proyecto; en subcarpetas hay que ajustarlas (por ejemplo `../../recursos/marca/...`), o ponerlas una sola vez en un `_metadata.yml` de la carpeta. Los `.sty` encuentran las fuentes junto a sí mismos: no hace falta definir `\caicedofuentes` (solo si se mueve la carpeta `fuentes/`).

El manual de la versión 2 está en `manual/manual-de-marca.pdf`. El sitio de ejemplo (cursos, charlas, proyectos y tutoriales) muestra todo lo de la versión 2.1 funcionando.

## Archivos

| Archivo | Para qué |
|---------|----------|
| `caicedo-documento.scss` / `.sty` | Documentos HTML y PDF |
| `caicedo-diapositivas.scss` / `.sty` | Diapositivas revealjs y beamer (gemelas) |
| `caicedo-sala-oscura.scss` | Capa del modo sala oscura para revealjs (en beamer: `\usepackage[oscura]{…}`) |
| `caicedo-sitio.scss` | Sitio web |
| `caicedo-claro.theme`, `caicedo-oscuro.theme` | Resaltado de código |
| `caicedo.lua` | Clases de color en PDF y beamer, separadores sobre noche en revealjs, afiliación en beamer, código desde un archivo (`archivo=`) y fichas |
| `sitio/materiales.ejs` | Listado de presentaciones y laboratorios con un botón por formato (v2.1) |
| `sitio/calendario.html` | Marca la semana en curso y la próxima fecha en el calendario de un curso (v2.1) |
| `python/caicedo_mpl.py` | Figuras de matplotlib con la letra y los colores de la marca (v2.1) |
| `categorias-tutoriales.html` | Enlaces de categorías del listado de tutoriales (sin cambios) |
| `logo/` | Isotipo, firmas, motivo, favicon, insignia, tarjeta social y BioForge, en SVG y PNG |
| `fuentes/` | Atkinson Hyperlegible Next y Mono (SIL OFL) y DejaVu (respaldo) |
| `fuente/` | Generador (`construir_marca.py`), plantillas y `tarjeta.py` (tarjetas de 1200 × 630 para listados y redes): de aquí salen todos los archivos anteriores |
| `manual/` | Manual de marca (PDF) |

## Uso rápido

**Documento (HTML y PDF)**

```yaml
filters: [recursos/marca/caicedo.lua]
format:
  html:
    theme: [cosmo, recursos/marca/caicedo-documento.scss]
  pdf:
    documentclass: scrartcl
    papersize: a4
    fontsize: 11pt
    pdf-engine: lualatex
    shift-heading-level-by: -1
    highlight-style: recursos/marca/caicedo-claro.theme
    include-in-header:
      text: \usepackage{recursos/marca/caicedo-documento}
```

**Diapositivas (revealjs y beamer)**

```yaml
shorttitle: "Título corto"
filters: [recursos/marca/caicedo.lua]
format:
  revealjs:
    theme: recursos/marca/caicedo-diapositivas.scss
    width: 1280
    height: 720
    margin: 0
    logo: recursos/marca/logo/firma-pie-claro.svg
    footer: "Título corto"
    slide-number: c/t
    highlight-style: recursos/marca/caicedo-claro.theme
  beamer:
    aspectratio: 169
    fontsize: 12pt
    pdf-engine: lualatex
    slide-level: 2
    highlight-style: recursos/marca/caicedo-claro.theme
    include-in-header:
      text: \usepackage{recursos/marca/caicedo-diapositivas}
```

Para el modo sala oscura:

- En revealjs, `theme: [recursos/marca/caicedo-diapositivas.scss, recursos/marca/caicedo-sala-oscura.scss]`.
- En beamer, `\usepackage[oscura]{recursos/marca/caicedo-diapositivas}`.
- En los dos, `highlight-style: recursos/marca/caicedo-oscuro.theme`.

**Sitio**

```yaml
website:
  favicon: recursos/marca/logo/favicon.svg
  image: recursos/marca/logo/tarjeta-social.png
  navbar:
    logo: recursos/marca/logo/isotipo-oscuro.svg
format:
  html:
    theme: [cosmo, recursos/marca/caicedo-sitio.scss]
```

## Cambiar la marca

No se editan a mano los archivos de esta carpeta. Se cambian los tokens o las plantillas de `fuente/` y se ejecuta:

```bash
python3 recursos/marca/fuente/construir_marca.py
```

Requiere `fontTools`. Para exportar los PNG hace falta Playwright con Chromium.

Para el PDF no hace falta instalar nada: los `.sty` cargan las fuentes desde `fuentes/`, así que esa carpeta tiene que ir completa en el repositorio. Solo si falta algún archivo buscan las fuentes del sistema, y exigen la familia entera: con una instalación parcial (solo la Regular, o la versión variable de Google Fonts) se detienen con un mensaje que nombra la cara que falta. Si LuaLaTeX termina con `cannot find file ''`, se borra la caché de fuentes: `luaotfload-tool --cache=erase`.
