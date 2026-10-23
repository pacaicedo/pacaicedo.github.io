# Sitio de ejemplo: marca P. E. Caicedo-Rodríguez (v2.1)

Un sitio Quarto completo hecho con la marca: cuatro secciones, tres cursos, dos charlas, tres proyectos y seis tutoriales. Todas las páginas, diapositivas (revealjs y beamer), guías (HTML y PDF) y figuras salen de los archivos de esta carpeta.

## Renderizar

```bash
uv sync                  # entorno de Python (pyproject.toml)
uv run quarto preview    # sitio en el navegador
uv run quarto render     # todo el sitio en _site/
```

Hace falta Quarto 1.6 o posterior y LuaLaTeX para los PDF. Antes de cada render, `recursos/figuras.py` regenera las figuras que cambiaron. El tutorial `tutoriales/entorno-uv-quarto` explica la instalación paso a paso.

`_site/` ya viene renderizado: se puede abrir `_site/index.html` sin instalar nada (las fórmulas necesitan conexión a internet).

## Organización

```
_quarto.yml                 tema, filtro, barra de navegación y pie (todas las páginas)
index.qmd                   portada: lo último de cada sección
cursos/
  index.qmd                 listado de cursos
  psim/  sysb/  tau/        un curso por carpeta
    index.qmd               Introducción, Resultados de Aprendizaje, Calendario y fechas
                            importantes, Presentaciones, Laboratorios, Recursos y tutoriales,
                            Referentes
    referentes.bib          la bibliografía de «Referentes»
    figuras.py, fig/        figuras del curso
    tarjeta.png             imagen del curso en el listado
    presentaciones/
      _metadata.yml         formatos comunes: revealjs + beamer, pie, autoría
      01-....qmd            una presentación por archivo (title, rotulo, date)
    laboratorios/
      _metadata.yml         formatos comunes: HTML + PDF
      lab1-....qmd
charlas/
  index.qmd
  2026-.../
    index.qmd               Evento, Presentación, Código
    diapositivas.qmd        revealjs + beamer (y diapositivas-sala.qmd para sala oscura)
proyectos/
  index.qmd
  .../index.qmd             Problema, Métodos, Resultados
tutoriales/                 Herramientas y Tutoriales
  index.qmd                 listado con categorías (Tutorial, Herramienta, PSIM, SYSB, TAU…)
  .../index.qmd
recursos/
  marca/                    la marca (no se edita a mano: ver recursos/marca/LEEME.md)
  python/datos_ejemplo.py   datos sintéticos: fantoma, ECG, sEMG y marcha
  python/diagramas.py       diagrama de BioForge
  figuras.py                pre-render: regenera las figuras que cambiaron
pyproject.toml              dependencias de Python para uv
```

## Agregar contenido

- **Un curso**: copiar `cursos/tau/` con otro nombre, cambiar `index.qmd`, `referentes.bib` y los materiales, y generar la tarjeta:
  ```bash
  uv run python recursos/marca/fuente/tarjeta.py --antetitulo "Curso · 2027-1" \
      --titulo "SIGLA" --subtitulo "Nombre del curso" -o cursos/sigla/tarjeta.png
  ```
- **Una presentación o un laboratorio**: un `.qmd` nuevo en `presentaciones/` o `laboratorios/` con `title`, `description`, `rotulo` y `date`. Aparece solo en la página del curso, con sus botones de HTML y PDF.
- **Una charla**: copiar `charlas/2026-experimentos-reproducibles/`. Para tener también la versión de sala oscura, ver `charlas/2026-ver-el-cuerpo-como-dato/`.
- **Un proyecto**: copiar una carpeta de `proyectos/` y mantener las tres secciones.
- **Un tutorial**: una carpeta en `tutoriales/` con su `index.qmd`. Con la categoría de un curso (`PSIM`, `SYSB`, `TAU`), aparece también en «Recursos y tutoriales» de ese curso.

## Contenido de ejemplo que hay que revisar

Las páginas usan contenido real donde se conocía y contenido de ejemplo en lo demás. Antes de publicar, revisar:

| Dónde | Qué es de ejemplo |
|:--|:--|
| Fichas de los cursos | Horarios, intensidad, prerrequisitos y pesos de evaluación |
| Calendarios | Fechas de entregas y temas por semana (los festivos de 2026-2 sí son los de Colombia) |
| Charla del XII Seminario de Automática | Fecha (5 de noviembre de 2026), modalidad, duración y público |
| Charla «Experimentos biomédicos reproducibles» | El evento completo (seminario, fecha y público) |
| Proyectos | Estado de cada componente según lo registrado hasta septiembre de 2026 |
| Resultados de riesgo de caída y sEMG | **Datos simulados**, y la página lo dice; se reemplazan por los reales cambiando la fuente de datos en `figuras.py` |
| Pie de página | Licencia CC BY 4.0 del contenido |
| `_quarto.yml` | `repo-url` comentado: poner la dirección del repositorio para los enlaces «Ver código fuente» |
