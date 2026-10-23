-- caicedo.lua: clases de color de la marca para salidas LaTeX (PDF y beamer).
-- En HTML y revealjs las clases ya tienen estilo en los .scss; este filtro
-- hace que [texto]{.alert}, {.dato}, {.grafo}, {.causa} y {.tenue} se vean
-- igual en el PDF. Uso en el qmd:  filters: [marca/caicedo.lua]

-- El PDF y el contenido de beamer van sobre blanco: se usan las variantes oscuras
-- de cada acento (las mismas que usan los .scss sobre fondo claro).
local colores = {
  dato = "cdatod", grafo = "cgrafod", causa = "ccausad", alert = "ccausad", tenue = "cmuted",
}

function Span(el)
  if not FORMAT:match("latex") and not FORMAT:match("beamer") then return nil end
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
