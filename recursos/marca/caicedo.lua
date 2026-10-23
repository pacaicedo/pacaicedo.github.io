-- caicedo.lua: filtro de la marca P. E. Caicedo-Rodríguez (v2.1). Generado por fuente/construir_marca.py.
-- Uso en el qmd:  filters: [recursos/marca/caicedo.lua]
--
-- 1. Clases de color en PDF y beamer: [texto]{.dato}, {.grafo}, {.causa}, {.alert},
--    {.aviso} y {.tenue} se ven igual que en HTML y revealjs (que ya las tienen en los .scss).
--    Los colores caicedo* los define cada .sty según el fondo (claro o sala oscura).
-- 2. revealjs: los separadores de sección (# Título) van sobre noche, el campo de marca,
--    salvo que el encabezado ya traiga su propio background-color o background-image.
--    Con {.sin-campo} en el encabezado se deja el fondo normal.
-- 3. beamer: la afiliación de author: pasa a \institute (ver Meta, al final).
-- 4. Código desde un archivo (v2.1): un bloque vacío con el atributo archivo muestra el
--    contenido real del archivo, con su nombre como rótulo:
--      ```{.python archivo="figuras.py"}
--      ```
--    lineas="12-40" muestra solo ese tramo. La ruta es relativa al qmd. Así el código que se
--    ve en la página es exactamente el que generó las figuras.
-- 5. Ficha (v2.1): en HTML, cada par rótulo/valor de ::: {.ficha} (lista de definiciones)
--    queda envuelto en <div class="ficha-dato">, para que la rejilla los acomode en columnas.

local NOCHE = "#1B1D4A"   -- token noche (lo escribe fuente/construir_marca.py)

local colores = {
  dato = "caicedodato", grafo = "caicedografo", causa = "caicedocausa",
  alert = "caicedocausa", aviso = "caicedoaviso", tenue = "caicedotenue",
}

local function es_latex()
  return FORMAT:match("latex") or FORMAT:match("beamer")
end

function Span(el)
  if not es_latex() then return nil end
  for _, clase in ipairs(el.classes) do
    local color = colores[clase]
    if color then
      local abre = "\\textcolor{" .. color .. "}{"
      if clase == "alert" and FORMAT:match("beamer") then abre = "\\alert{" end
      local out = { pandoc.RawInline("latex", abre) }
      for _, i in ipairs(el.content) do table.insert(out, i) end
      table.insert(out, pandoc.RawInline("latex", "}"))
      return out
    end
  end
end

function Header(el)
  if not FORMAT:match("revealjs") or el.level ~= 1 then return nil end
  local nivel = PANDOC_WRITER_OPTIONS and PANDOC_WRITER_OPTIONS.slide_level
  if nivel ~= nil and nivel < 2 then return nil end
  if el.classes:includes("sin-campo") then return nil end
  if el.attributes["background-color"] or el.attributes["background-image"] then return nil end
  el.attributes["background-color"] = NOCHE
  return el
end

-- 3. beamer: Quarto no pasa las afiliaciones de author: a \institute. Si el qmd no trae
--    institute:, se arma con las afiliaciones (como en la portada de revealjs).
function Meta(m)
  if not FORMAT:match("beamer") or m.institute ~= nil then return nil end
  local vistos, nombres = {}, {}
  local function agregar(af)
    if af == nil then return end
    local n = af.name or af
    local s = pandoc.utils.stringify(n)
    if s ~= "" and not vistos[s] then vistos[s] = true; table.insert(nombres, s) end
  end
  if m.affiliations then
    for _, af in ipairs(m.affiliations) do agregar(af) end
  end
  if #nombres == 0 and m.authors then
    for _, au in ipairs(m.authors) do
      if au.affiliations then for _, af in ipairs(au.affiliations) do agregar(af) end end
    end
  end
  if #nombres == 0 then return nil end
  m.institute = pandoc.MetaInlines(pandoc.Inlines(table.concat(nombres, "; ")))
  return m
end

-- 4. Código desde un archivo.
local function carpeta_doc()
  local f = (quarto and quarto.doc and quarto.doc.input_file)
    or (PANDOC_STATE and PANDOC_STATE.input_files and PANDOC_STATE.input_files[1])
  if not f then return "." end
  return pandoc.path.directory(f)
end

function CodeBlock(el)
  local ruta = el.attributes["archivo"]
  if not ruta then return nil end
  local completo = pandoc.path.join({ carpeta_doc(), ruta })
  local h = io.open(completo, "r")
  if not h then
    io.stderr:write("caicedo.lua: no se encontró " .. completo .. "\n")
    el.text = "# (no se encontró " .. ruta .. ")"
    el.attributes["archivo"] = nil
    return el
  end
  local texto = h:read("a"); h:close()
  local tramo = el.attributes["lineas"]
  if tramo then
    local a, b = tramo:match("^(%d+)%-(%d+)$")
    a, b = tonumber(a), tonumber(b)
    if a and b then
      local sel, n = {}, 0
      for linea in (texto .. "\n"):gmatch("(.-)\n") do
        n = n + 1
        if n >= a and n <= b then table.insert(sel, linea) end
      end
      texto = table.concat(sel, "\n")
    end
    el.attributes["lineas"] = nil
  end
  el.text = (texto:gsub("%s+$", ""))
  el.attributes["archivo"] = nil
  if not el.attributes["filename"] then el.attributes["filename"] = ruta end
  return el
end

-- 5. Ficha: agrupa cada término con su definición.
function Div(el)
  if not el.classes:includes("ficha") then return nil end
  if not (FORMAT:match("html") or FORMAT:match("revealjs")) then return nil end
  local salida = {}
  for _, bloque in ipairs(el.content) do
    if bloque.t == "DefinitionList" then
      table.insert(salida, pandoc.RawBlock("html", "<dl>"))
      for _, item in ipairs(bloque.content) do
        table.insert(salida, pandoc.RawBlock("html", '<div class="ficha-dato"><dt>'))
        table.insert(salida, pandoc.Plain(item[1]))
        table.insert(salida, pandoc.RawBlock("html", "</dt><dd>"))
        for _, definicion in ipairs(item[2]) do
          for _, b in ipairs(definicion) do
            if b.t == "Para" then b = pandoc.Plain(b.content) end
            table.insert(salida, b)
          end
        end
        table.insert(salida, pandoc.RawBlock("html", "</dd></div>"))
      end
      table.insert(salida, pandoc.RawBlock("html", "</dl>"))
    else
      table.insert(salida, bloque)
    end
  end
  el.content = salida
  return el
end
