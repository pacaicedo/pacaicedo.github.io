from pathlib import Path
import json
root=Path(__file__).resolve().parents[2]
p=json.loads((root/'recursos/marca/paleta.json').read_text())
def lum(h):
 c=[int(h[i:i+2],16)/255 for i in (1,3,5)]
 c=[v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in c]
 return sum(a*b for a,b in zip(c,[.2126,.7152,.0722]))
def contrast(a,b):
 x,y=sorted([lum(a),lum(b)]);return (y+.05)/(x+.05)
rows=[]
for fg,bg in [('ink','paper'),('violet','paper'),('copper','paper'),('muted','paper'),('white','ink'),('light','ink'),('signal','ink'),('violet','white'),('copper','white')]:
 r=contrast(p[fg],p[bg]);rows.append({'texto':fg,'fondo':bg,'ratio':round(r,2),'AA_normal':r>=4.5,'AAA_normal':r>=7})
for mode in ['claro','oscuro']:
 t=json.loads((root/f'recursos/marca/caicedo-{mode}.theme').read_text());bg=t['background-color']
 ratios=[contrast(v['text-color'],bg) for v in t['text-styles'].values()]
 rows.append({'codigo':mode,'min_ratio':round(min(ratios),2),'AA_normal':min(ratios)>=4.5})
print(json.dumps(rows,ensure_ascii=False,indent=2))
