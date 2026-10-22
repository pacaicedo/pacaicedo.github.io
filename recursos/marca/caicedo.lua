-- caicedo.lua v2. No dependence on Quarto's private callout internals.
local colors={dato="cviolet",grafo="cviolet",causa="ccopper",alert="ccopper",tenue="cmuted",muted="cmuted"}
local function tex() return FORMAT:match("latex") or FORMAT:match("beamer") end
function Span(el)
 if not tex() then return nil end
 for _,c in ipairs(el.classes) do
  if colors[c] then
   local out={pandoc.RawInline("latex","\\textcolor{"..colors[c].."}{")}
   for _,v in ipairs(el.content) do table.insert(out,v) end
   table.insert(out,pandoc.RawInline("latex","}"));return out
  end
 end
end
function Div(el)
 local styles={['marca-nota']='cblockviolet',['marca-evidencia']='cblockviolet',['marca-alerta']='cblockcopper'}
 for _,c in ipairs(el.classes) do
  if styles[c] then
   local title=el.attributes.title or (c=='marca-alerta' and 'Límite' or 'Idea clave')
   if tex() then
    local escaped=pandoc.write(pandoc.Pandoc({pandoc.Plain({pandoc.Str(title)})}),"latex"):gsub("%s+$","")
    local out={pandoc.RawBlock("latex","\\begin{caicedonota}{"..styles[c].."}{"..escaped.."}")}
    for _,v in ipairs(el.content) do table.insert(out,v) end
    table.insert(out,pandoc.RawBlock("latex","\\end{caicedonota}"));return out
   else
    el.classes:insert('callout');el.classes:insert(c=='marca-alerta' and 'callout-important' or 'callout-note')
    table.insert(el.content,1,pandoc.Para({pandoc.Strong({pandoc.Str(title)})}));return el
   end
  end
 end
end
