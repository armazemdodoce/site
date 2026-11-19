"""Gera site/index.html a partir do canvas (project/Main.dc.html).
Uso: python3 build_site.py
"""
import re, json

SRC = '/home/claude/lpcanvas/project/Main.dc.html'
OUT = '/home/claude/site/index.html'
ext = json.load(open('/tmp/extmap.json'))

src = open(SRC, encoding='utf-8').read()
src = src.replace("'/_blob/' + id", "'img/' + id + '.jpg'")
src = re.sub(r'/_blob/([0-9a-f]{32})', lambda m: 'img/' + m.group(1) + ext[m.group(1)], src)

helmet = re.search(r'<helmet>(.*?)</helmet>', src, re.S).group(1)
body = re.search(r'</helmet>(.*?)</x-dc>', src, re.S).group(1)
script = re.search(r'<script type="text/x-dc"[^>]*>(.*?)</script>', src, re.S).group(1)

runtime = r'''
class DCLogic { constructor(){ this.props = {}; this.state = {}; }
  setState(p){ this.state = Object.assign({}, this.state, p); render(); } forceUpdate(){ render(); } }
const TPL = document.getElementById('tpl');
const ROOT = document.getElementById('app');
const comp = new Component();
const get = (scope, path) => { path = path.trim();
  if (path === 'true') return true; if (path === 'false') return false;
  if (/^-?\d+(\.\d+)?$/.test(path)) return Number(path);
  return path.split('.').reduce((o, k) => (o == null ? undefined : o[k]), scope); };
const whole = s => { const m = /^\s*\{\{([^}]+)\}\}\s*$/.exec(s); return m ? m[1] : null; };
const interp = (s, scope) => s.replace(/\{\{([^}]+)\}\}/g, (_, p) => { const v = get(scope, p); return v == null ? '' : v; });
function walk(node, scope, out){
  if (node.nodeType === 3) { out.appendChild(document.createTextNode(interp(node.nodeValue, scope))); return; }
  if (node.nodeType !== 1) return;
  const tag = node.tagName.toLowerCase();
  if (tag === 'sc-for') { const list = get(scope, whole(node.getAttribute('list')) || '') || [];
    const as = node.getAttribute('as') || 'item';
    list.forEach((it, i) => { const s = Object.assign(Object.create(scope), {[as]: it, $index: i});
      node.childNodes.forEach(c => walk(c, s, out)); }); return; }
  if (tag === 'sc-if') { const v = get(scope, whole(node.getAttribute('value')) || '');
    if (v) node.childNodes.forEach(c => walk(c, scope, out)); return; }
  const el = document.createElement(tag);
  for (const a of node.attributes) { if (a.name.startsWith('hint-')) continue;
    const w = whole(a.value);
    if (/^on[a-z]/i.test(a.name) && w) { const fn = get(scope, w); if (typeof fn === 'function') el.addEventListener(a.name.slice(2).toLowerCase(), fn); continue; }
    el.setAttribute(a.name, interp(a.value, scope)); }
  const kids = tag === 'template' ? node.content.childNodes : node.childNodes;
  kids.forEach(c => walk(c, scope, el)); out.appendChild(el); }
function render(){ const vals = comp.renderVals(); const frag = document.createDocumentFragment();
  TPL.content.childNodes.forEach(c => walk(c, vals, frag)); ROOT.replaceChildren(frag); }
render();
'''

schema = {
  "@context": "https://schema.org", "@type": "Store", "name": "Armazém do Doce",
  "description": "Distribuidora de doces em Catanduva: atacado e varejo de balas, chocolates, confeitaria, sorveteria e embalagens.",
  "url": "https://armazemdodoce.com.br", "telephone": "+55-17-99276-4304",
  "image": "https://armazemdodoce.com.br/img/" + "f80397a6b6c06bce7515cde78281a78f" + ext.get("f80397a6b6c06bce7515cde78281a78f", ".jpg"),
  "address": {"@type": "PostalAddress", "streetAddress": "Rua Campinas, 418 - Higienópolis",
              "addressLocality": "Catanduva", "addressRegion": "SP", "addressCountry": "BR"},
  "openingHoursSpecification": [
    {"@type": "OpeningHoursSpecification", "dayOfWeek": ["Monday","Tuesday","Wednesday","Thursday","Friday"], "opens": "06:30", "closes": "18:30"},
    {"@type": "OpeningHoursSpecification", "dayOfWeek": "Saturday", "opens": "07:00", "closes": "14:00"}],
  "sameAs": ["https://instagram.com/armazemdoce.catanduva"],
  "aggregateRating": {"@type": "AggregateRating", "ratingValue": "5.0", "reviewCount": "79"}
}

page = f'''<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Armazém do Doce Catanduva | Atacado e varejo de doces, chocolates e confeitaria</title>
<meta name="description" content="Distribuidora de doces em Catanduva/SP. Balas, chocolates, coberturas, produtos para confeitaria e sorveteria, embalagens e doces caseiros com preço de atacado. Rua Campinas, 418. Peça pelo WhatsApp (17) 99276-4304.">
<meta property="og:title" content="Armazém do Doce Catanduva">
<meta property="og:description" content="Atacado e varejo de doces, chocolates, confeitaria, sorveteria e embalagens em Catanduva/SP.">
<meta property="og:image" content="{schema['image']}">
<meta property="og:url" content="https://armazemdodoce.com.br">
<link rel="icon" href="img/20f13a055e3966c11ce1c82b8d1a9a30{ext.get('20f13a055e3966c11ce1c82b8d1a9a30','.png')}">
<link rel="canonical" href="https://armazemdodoce.com.br/">
<script type="application/ld+json">{json.dumps(schema, ensure_ascii=False)}</script>
{helmet}
</head>
<body>
<div id="app"></div>
<template id="tpl">{body}</template>
<noscript><p>Armazém do Doce — Rua Campinas, 418, Higienópolis, Catanduva/SP. WhatsApp (17) 99276-4304.</p></noscript>
<script>
{runtime.split('const TPL')[0]}
{script}
const TPL{runtime.split('const TPL',1)[1]}
</script>
</body>
</html>
'''
open(OUT, 'w', encoding='utf-8').write(page)
print('ok', len(page))
