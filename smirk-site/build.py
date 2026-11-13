#!/usr/bin/env python3
"""Builds the Smirk site into ./dist.

Notes live in content/notes/*.md. Each file has a small header, then the text:

    ---
    title: The tool is not the moat
    slug: tools-are-not-moats        (the page address: /thinking/<slug>)
    number: 02
    date: 2026-10-01
    excerpt: One or two sentences shown in lists and link previews.
    quote: The one line worth remembering. Shown in blue handwriting mid-note.
    rule: The closing takeaway, one or two sentences. Shown under "One rule".
    draft: false                     (true = visible on the site, hidden from search engines)
    topic: Operations                (optional. One word or two. Becomes a filter on /thinking)
    ---

    The setup. One to three paragraphs, blank line between each.

    ***

    The turn. One to three paragraphs after the quote.

Every note follows the same layout: setup, blue quote, turn, one rule.
The line with three asterisks marks where the quote goes.

Run:  python3 build.py
"""
import glob, html, json, os, shutil, datetime
BASE = 'https://smirk.io'
ROOT = os.path.dirname(os.path.abspath(__file__))
DIST = os.path.join(ROOT, 'dist')
HOME_COUNT = 5  # how many notes the home page lists
MONTHS = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
esc = lambda t: html.escape(t, quote=True)

def load_notes():
    notes = []
    for path in glob.glob(os.path.join(ROOT, 'content', 'notes', '*.md')):
        raw = open(path, encoding='utf-8').read()
        if not raw.startswith('---'): raise SystemExit(f'{path}: missing the --- header')
        _, head, body = raw.split('---', 2)
        meta = {}
        for line in head.strip().splitlines():
            if ':' in line:
                k, v = line.split(':', 1); meta[k.strip().lower()] = v.strip()
        for req in ('title', 'slug', 'number', 'date', 'excerpt', 'quote', 'rule'):
            if not meta.get(req): raise SystemExit(f'{path}: header is missing "{req}"')
        d = datetime.date.fromisoformat(meta['date'])
        notes.append(dict(title=meta['title'], slug=meta['slug'], n=meta['number'], date=d,
                          shown=f'{MONTHS[d.month-1]} {d.year}', ex=meta['excerpt'],
                          draft=meta.get('draft', 'false').lower() in ('true', 'yes', '1'),
                          quote=meta['quote'], rule=meta['rule'], topic=meta.get('topic', '').strip(), parts=split_body(body, path)))
    notes.sort(key=lambda n: (n['date'], n['n']), reverse=True)
    slugs = [n['slug'] for n in notes]
    if len(set(slugs)) != len(slugs): raise SystemExit('two notes share the same slug')
    return notes

def split_body(body, path):
    blocks = [' '.join(b.split()) for b in body.strip().split('\n\n') if b.strip()]
    if blocks.count('***') != 1: raise SystemExit(f'{path}: the text needs exactly one line of *** where the blue quote goes')
    i = blocks.index('***'); before, after = blocks[:i], blocks[i+1:]
    if not before or not after: raise SystemExit(f'{path}: write at least one paragraph before and after the *** line')
    return before, after

def note_body(n):
    paras = lambda bs: '\n      '.join(f'<p>{esc(b)}</p>' for b in bs)
    return (f'{paras(n["parts"][0])}\n      <p class="pull">{esc(n["quote"])}</p>\n      {paras(n["parts"][1])}\n'
            f'      <div class="rule"><span class="mono">One rule</span><p>{esc(n["rule"])}</p></div>')

def body_html(blocks):
    out = []
    for b in blocks:
        b = ' '.join(b.split('\n'))
        if b.startswith('> '): out.append(f'<p class="pull">{esc(b[2:])}</p>')
        elif b.startswith('## '): out.append(f'<h2>{esc(b[3:])}</h2>')
        else: out.append(f'<p>{esc(b)}</p>')
    return '\n      '.join(out)

def row(n, prefix):
    return (f'<a class="nr2" data-topic="{esc(n["topic"])}" href="/thinking/{n["slug"]}"><span class="n">{esc(n["n"])}</span>'
            f'<span><span class="t">{esc(n["title"])}</span><span class="e">{esc(n["ex"])}</span></span>'
            f'<span class="d">{n["shown"]}</span><span class="rd2 hand">read it →</span></a>')

FAV = ("data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'><rect width='64' height='64' rx='14' fill='%233553E0'/>"
       "<g fill='%23F2F0EB'><rect x='9' y='40' width='6' height='6'/><rect x='17' y='40' width='6' height='6'/><rect x='25' y='40' width='6' height='6'/>"
       "<rect x='33' y='40' width='6' height='6'/><rect x='41' y='32' width='6' height='6'/></g><rect x='49' y='24' width='6' height='6' fill='%23B9C4FF'/></svg>")
MARK = ('<svg viewBox="0 0 54 22" aria-hidden="true"><g fill="currentColor"><rect x="0" y="16" width="6" height="6"/><rect x="8" y="16" width="6" height="6"/>'
        '<rect x="16" y="16" width="6" height="6"/><rect x="24" y="16" width="6" height="6"/><rect x="32" y="16" width="6" height="6"/>'
        '<rect x="40" y="8" width="6" height="6"/></g><rect class="ld" x="48" y="0" width="6" height="6" fill="#8EA0FF"/></svg>')
CIRC = ('<svg viewBox="0 0 400 120" preserveAspectRatio="none" aria-hidden="true"><path vector-effect="non-scaling-stroke" '
        'd="M200 8 C80 2 10 26 10 62 C10 100 110 116 220 112 C330 108 396 86 390 52 C384 20 300 4 190 12"/></svg>')
CSS = r'''
:root{--cob:#3553E0;--cream:#F2F0EB;--paper:#FBFAF7;--ink:#121211;--body:#3A3935;--muted:#6B6A64;--peri:#8EA0FF;--pad:clamp(20px,4vw,56px)}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--cream);color:var(--ink);font-family:'Archivo',system-ui,sans-serif;-webkit-font-smoothing:antialiased;overflow-x:hidden}
a{color:inherit;text-decoration:none}
::selection{background:var(--cob);color:var(--cream)}
.blue ::selection,.blue::selection{background:var(--ink);color:var(--cream)}
.hand{font-family:'Caveat',cursive;font-weight:700}
.mono{font-family:'JetBrains Mono',monospace;font-size:11px;letter-spacing:.12em;text-transform:uppercase}
.pad{padding-left:var(--pad);padding-right:var(--pad)}
.brand{display:flex;align-items:center;gap:10px}
.brand svg{width:40px;height:auto;display:block}
.brand .wm{font-family:'Inter Tight',sans-serif;font-weight:600;font-size:23px;letter-spacing:-.06em;line-height:1}
.back{font-size:27px;line-height:1;transform:rotate(-1.5deg);transform-origin:left center;display:inline-block}
.back:hover{color:var(--peri)}
footer{background:var(--ink);color:var(--cream)}
footer .in{display:flex;justify-content:space-between;align-items:center;gap:20px;height:76px}
footer .meta{display:flex;opacity:.72}
footer .meta span+span{margin-left:14px;padding-left:14px;border-left:1px solid currentColor}
@media (max-width:520px){footer .meta span:first-child{display:none}footer .meta span:nth-child(2){margin-left:0;padding-left:0;border-left:0}.back{font-size:23px}}
/* note page */
.rbar{position:sticky;top:0;background:var(--cob);color:var(--cream);z-index:5}
.rbar .in{height:60px;display:flex;justify-content:space-between;align-items:center;gap:16px}
.rbar .bkw{display:flex;align-items:baseline;gap:22px;min-width:0}
.rbar .ra{font-size:20px;line-height:1;opacity:.75;transform:rotate(-1.5deg);display:inline-block;white-space:nowrap;border-bottom:1px solid rgba(242,240,235,.45);padding-bottom:1px}
.rbar .ra:hover{opacity:1;color:var(--peri);border-color:var(--peri)}
.rbar .ra[hidden]{display:none}
@media (max-width:520px){.rbar .bkw{gap:14px}.rbar .ra{font-size:18px}}
.rbar .brand svg{width:34px}.rbar .brand .wm{font-size:20px}
.rp{position:absolute;left:0;bottom:0;height:3px;background:var(--cream);width:0}
.art{max-width:720px;margin:0 auto;padding:clamp(56px,7vw,90px) 24px clamp(80px,9vw,130px)}
.art .ah{padding-bottom:32px;margin-bottom:38px;border-bottom:1.5px solid var(--ink)}
.art .ah{position:relative;isolation:isolate}
.art .ah .bgn{position:absolute;z-index:-1;right:-6%;bottom:8px;font-size:clamp(150px,22vw,250px);line-height:.74;font-stretch:125%;font-weight:800;letter-spacing:-.02em;color:transparent;-webkit-text-stroke:1.5px rgba(18,18,17,.1);pointer-events:none;user-select:none}
@media (max-width:760px){.art .ah .bgn{right:-2%;-webkit-text-stroke-width:1.2px}}
.art .ah .mono{color:var(--muted)}
.art h1{font-weight:500;font-size:clamp(32px,4.4vw,58px);line-height:1;letter-spacing:-.04em;margin:18px 0 0}
.art .ab p{font-size:clamp(18px,1.5vw,20px);line-height:1.65;color:#22211E;margin:0 0 24px}
.art .ab p.pull{font-family:'Caveat',cursive;font-weight:700;font-size:clamp(32px,3.6vw,44px);line-height:1.04;color:var(--cob);margin:40px 0 42px;transform:rotate(-1.2deg);transform-origin:left center}
.art .ab h2{font-weight:600;font-size:24px;letter-spacing:-.02em;margin:46px 0 14px}
.art .rule{margin-top:44px;padding-top:22px;border-top:1.5px solid var(--ink)}
.art .rule .mono{color:var(--cob)}
.art .ab .rule p{margin:12px 0 0;font-size:clamp(24px,2.7vw,34px);line-height:1.12;letter-spacing:-.03em;font-weight:500;color:var(--ink)}
.art .sig{color:var(--cob);font-size:40px;margin-top:30px;transform:rotate(-3deg);display:inline-block}
.art .next{display:block;margin-top:64px;padding-top:26px;border-top:1.5px solid var(--ink)}
.art .next b{display:block;font-weight:500;letter-spacing:-.035em;font-size:clamp(24px,2.8vw,32px);line-height:1.05;margin-top:8px}
.art .next:hover b{color:var(--cob)}
.art .all{display:inline-block;margin-top:34px;font-size:17px;font-weight:500;border-bottom:1.5px solid var(--ink);padding-bottom:3px}
.art .all:hover{color:var(--cob);border-color:var(--cob)}
/* index page */
header.abs{position:absolute;top:0;left:0;right:0;z-index:5;color:var(--cream)}
header.abs .in{height:68px;display:flex;align-items:center;justify-content:space-between;gap:20px}
.top{background:var(--cob);color:var(--cream);padding-top:clamp(120px,15vw,190px);padding-bottom:clamp(48px,6vw,84px);background-image:radial-gradient(70% 60% at 76% 20%,rgba(142,160,255,.36),rgba(142,160,255,0)),linear-gradient(rgba(242,240,235,.07) 1px,transparent 1px),linear-gradient(90deg,rgba(242,240,235,.07) 1px,transparent 1px);background-size:auto,32px 32px,32px 32px}
.top .kick{font-size:clamp(24px,2.3vw,34px);line-height:1;transform:rotate(-2deg);transform-origin:left;display:inline-block;margin-bottom:18px}
.top h1{margin:0;font-weight:500;font-size:clamp(44px,9.6vw,168px);line-height:.9;letter-spacing:-.045em}
.top h1 .c{position:relative;display:inline-block;white-space:nowrap}
.top h1 .c svg{position:absolute;left:-4%;top:-8%;width:108%;height:120%;overflow:visible;pointer-events:none}
.top h1 .c path{fill:none;stroke:var(--cream);stroke-width:3.4;stroke-linecap:round;stroke-dasharray:2400;stroke-dashoffset:2400;animation:dr 1.4s .5s cubic-bezier(.5,0,.2,1) forwards}
@keyframes dr{to{stroke-dashoffset:0}}
.top .sub{margin:clamp(28px,3.4vw,48px) 0 0;max-width:34em;font-size:clamp(17px,1.5vw,22px);line-height:1.45;color:rgba(242,240,235,.9)}
main.list{padding-top:clamp(28px,4vw,56px);padding-bottom:clamp(64px,7vw,110px)}
.pf{padding-top:clamp(36px,5vw,72px);padding-bottom:clamp(56px,6vw,96px)}
.pf .grp{margin-top:clamp(56px,7vw,96px)}
.pf .grp:first-child{margin-top:0}
.pf .gh{display:flex;flex-wrap:wrap;align-items:baseline;gap:8px 28px;padding-bottom:18px;border-bottom:1.5px solid var(--ink)}
.pf .gh h2{margin:0;font-weight:500;font-size:clamp(26px,3vw,40px);letter-spacing:-.035em;line-height:1}
.pf .gh p{margin:0;max-width:44em;font-size:16px;line-height:1.45;color:var(--muted)}
.pi{display:grid;grid-template-columns:120px 1fr;gap:30px;padding:34px 0 38px;border-bottom:1px solid rgba(18,18,17,.15)}
.pi .n{font-size:64px;line-height:.8;font-stretch:125%;font-weight:800;color:transparent;-webkit-text-stroke:1.5px var(--ink);transition:color .4s,-webkit-text-stroke-color .4s;padding-top:4px}
.pi:hover .n,.pi.hv .n{color:var(--cob);-webkit-text-stroke-color:var(--cob)}
.pi .hd{display:flex;flex-wrap:wrap;align-items:baseline;gap:8px 18px}
.pi h3{margin:0;font-size:clamp(26px,3vw,42px);line-height:1;letter-spacing:-.03em;font-weight:600}
.pi .st{color:var(--muted);order:-1;flex-basis:100%;margin-bottom:4px}
.pi .st.on{color:var(--cob)}
.pi .hn{margin-left:auto;color:var(--cob);font-size:clamp(24px,2.2vw,30px);line-height:1;white-space:nowrap;transform:rotate(-3deg);transform-origin:right center}
.pi:nth-of-type(even) .hn{transform:rotate(2deg)}
.pi .st.on::before{content:"";display:inline-block;width:6px;height:6px;margin-right:7px;background:var(--cob);vertical-align:1px;animation:blink 2.4s steps(1) infinite}
@keyframes blink{0%,70%{opacity:1}71%,100%{opacity:.25}}
.pi .pso .oc p{font-size:clamp(17px,1.5vw,20px);line-height:1.4;letter-spacing:-.01em}
.top h1 .u{position:relative;display:inline-block}
.top h1 .u svg{position:absolute;left:-2%;bottom:-.12em;width:104%;height:.3em;overflow:visible;pointer-events:none}
.top h1 .u path{fill:none;stroke:var(--peri);stroke-width:3.4;stroke-linecap:round;stroke-dasharray:1400;stroke-dashoffset:1400;animation:dr 1.2s .5s cubic-bezier(.5,0,.2,1) forwards}
.pband{background:var(--cob);color:var(--cream);padding-top:clamp(56px,7vw,110px);padding-bottom:clamp(44px,5vw,76px);display:flex;justify-content:space-between;align-items:flex-end;flex-wrap:wrap;gap:30px;background-image:linear-gradient(rgba(242,240,235,.07) 1px,transparent 1px),linear-gradient(90deg,rgba(242,240,235,.07) 1px,transparent 1px);background-size:32px 32px}
.pband .big{margin:0;font-weight:500;font-size:clamp(40px,7vw,112px);line-height:.92;letter-spacing:-.045em}
.pband .big span{display:block;opacity:.55}
.pband .fin{color:var(--peri);font-size:clamp(26px,2.6vw,38px);line-height:1;transform:rotate(-3deg);transform-origin:right bottom}
@media (max-width:700px){.pband{flex-direction:column;align-items:flex-start}.pband .fin{align-self:flex-end}.pi .hn{margin-left:0;flex-basis:100%;transform-origin:left center;margin-top:4px}}
.pi .pso{display:grid;grid-template-columns:repeat(3,1fr);gap:0;margin:22px 0 0}
.pi .pso .mono{display:block;margin-bottom:10px;color:var(--muted)}
.pi .pso p{margin:0;font-size:16px;line-height:1.5;color:var(--body)}
.pi{padding:0}
.pi .n{margin-top:60px}
.pi>div{padding:34px 0 38px;background:linear-gradient(90deg,transparent 33.333%,rgba(18,18,17,.04) 33.333%,rgba(18,18,17,.04) 66.666%,rgba(53,83,224,.07) 66.666%)}
.pi .pso>div{padding:0 22px}
.pi .pso>div:first-child{padding-left:0}
.pi .hn{margin-right:22px}
@media (max-width:900px){.pi>div{background:none;padding:28px 0 0}.pi .n{margin-top:52px}.pi .pso{margin:16px 0 0 -18px}.pi .pso>div,.pi .pso>div:first-child{padding:14px 18px 16px}.pi .pso>div:nth-child(2){background:rgba(18,18,17,.04)}.pi .pso .oc{background:rgba(53,83,224,.07)}.pi .hn{margin-right:0}}
.pi .pso .oc .mono{color:var(--cob)}
.pi .pso .oc p{color:var(--ink);font-weight:500}
@media (max-width:900px){.pi .pso{grid-template-columns:1fr;gap:0}}
@media (max-width:760px){.pi{grid-template-columns:70px 1fr;gap:16px}.pi .n{font-size:40px}}
@media (max-width:520px){.pi{grid-template-columns:1fr;gap:0}.pi .n{margin-top:28px}.pi>div{padding-top:16px}}
.filt{display:flex;flex-wrap:wrap;align-items:baseline;gap:6px 26px;padding:0 0 18px}
.filt .lb{color:var(--muted)}
.filt button{font-family:'JetBrains Mono',monospace;font-size:11px;letter-spacing:.12em;text-transform:uppercase;background:none;border:0;padding:6px 0;color:var(--ink);opacity:.55;cursor:pointer;background-image:linear-gradient(var(--cob),var(--cob));background-repeat:no-repeat;background-position:0 100%;background-size:0 1.5px;transition:opacity .3s,color .3s,background-size .4s cubic-bezier(.16,1,.3,1)}
.filt button:hover{opacity:1}
.filt button[aria-pressed="true"]{opacity:1;color:var(--cob);background-size:100% 1.5px}
.filt button:focus-visible{outline:1.5px solid var(--cob);outline-offset:4px}
.filt button sup{font-size:9px;margin-left:3px;opacity:.7}
.nr2[hidden]{display:none}
.nlist{border-top:1.5px solid var(--ink)}
.nr2{position:relative;display:grid;grid-template-columns:120px 1fr auto;gap:30px;align-items:center;padding:26px 0;border-bottom:1px solid rgba(18,18,17,.15)}
.nr2 .n{font-size:64px;line-height:.8;font-stretch:125%;font-weight:800;color:transparent;-webkit-text-stroke:1.5px var(--ink);transition:color .4s,-webkit-text-stroke-color .4s}
.nr2 .t{display:block;font-size:clamp(26px,3vw,46px);line-height:1;letter-spacing:-.025em;font-weight:600;transition:transform .5s cubic-bezier(.16,1,.3,1)}
.nr2 .e{display:block;font-size:16px;margin-top:10px;opacity:.7;max-width:640px;line-height:1.45}
.nr2 .d{font-family:'JetBrains Mono',monospace;font-size:11px;letter-spacing:.08em;text-transform:uppercase;opacity:.7;transition:opacity .3s}
.nr2 .rd2{position:absolute;right:0;top:50%;color:var(--cob);font-size:30px;transform:translateY(-50%) rotate(-4deg);opacity:0;transition:opacity .3s}
.nr2:hover .t,.nr2.hv .t{transform:translateX(14px)}
.nr2:hover .n,.nr2.hv .n{color:var(--cob);-webkit-text-stroke-color:var(--cob)}
.nr2:hover .rd2,.nr2.hv .rd2{opacity:1}
.nr2:hover .d,.nr2.hv .d{opacity:0}
@media (max-width:760px){.nr2{grid-template-columns:70px 1fr;padding-bottom:44px}.nr2 .d{display:none}.nr2 .n{font-size:40px}.nr2 .rd2{top:auto;bottom:10px;right:2px;font-size:21px;transform:rotate(-3deg)}.nr2:hover .t,.nr2.hv .t{transform:translateX(8px)}}
@media (prefers-reduced-motion:reduce){.top h1 .c path,.top h1 .u path{animation:none;stroke-dashoffset:0}.pi .st.on::before{animation:none}*{transition:none!important}}
'''
FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
         '<link href="https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@62..125,100..900&family=Caveat:wght@500;700&family=Inter+Tight:wght@600&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">')

def head(title, desc, path, noindex=False, extra=''):
    url = BASE + path
    robots = '<meta name="robots" content="noindex, follow">' if noindex else '<meta name="robots" content="index, follow, max-image-preview:large">'
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{url}">
{robots}
<meta name="theme-color" content="#3553E0">
<link rel="icon" href="{FAV}" type="image/svg+xml">
<link rel="icon" href="/favicon.ico" sizes="32x32">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<meta property="og:site_name" content="Smirk">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{BASE}/og.png">
<meta name="twitter:card" content="summary_large_image">
{extra}{FONTS}
<style>{CSS}</style>
</head>'''

FOOT = f'''<footer><div class="in pad">
  <a class="brand" href="/" aria-label="Smirk home">{MARK}<span class="wm">smirk</span></a>
  <span class="meta mono"><span>A systems studio</span><span>Austin, Texas</span><span>© 2026</span></span>
</div></footer>'''
TOUCH_JS = '''<script>
(function(){ if(!(window.matchMedia&&matchMedia('(hover:none)').matches)||!('IntersectionObserver' in window)) return;
  var o=new IntersectionObserver(function(es){ es.forEach(function(e){ e.target.classList.toggle('hv',e.isIntersecting); }); },{rootMargin:'-44% 0px -44% 0px'});
  document.querySelectorAll('.nr2').forEach(function(el){ o.observe(el); }); })();
</script>'''

def note_page(n, nxt):
    ld = ''
    if not n['draft']:
        ld = '<script type="application/ld+json">' + json.dumps({
            '@context': 'https://schema.org', '@type': 'BlogPosting', 'headline': n['title'], 'description': n['ex'],
            'datePublished': n['date'].isoformat(), 'url': f'{BASE}/thinking/{n["slug"]}', 'image': f'{BASE}/og.png',
            'author': {'@type': 'Organization', 'name': 'Smirk', 'url': BASE + '/'},
            'publisher': {'@type': 'Organization', 'name': 'Smirk', 'logo': {'@type': 'ImageObject', 'url': f'{BASE}/icon-512.png'}}},
            separators=(',', ':')) + '</script>\n'
    extra = f'<meta property="og:type" content="article">\n<meta property="article:published_time" content="{n["date"].isoformat()}">\n{ld}'
    return head(f'{n["title"]} — Thinking in Systems — Smirk', n['ex'], f'/thinking/{n["slug"]}', noindex=n['draft'], extra=extra) + f'''
<body>
<div class="rbar blue"><div class="in pad">
  <span class="bkw"><a class="back hand" id="bk" href="/thinking">← Thinking in Systems</a><a class="ra hand" id="ra" href="/thinking" hidden>read all</a></span>
  <script>(function(){{ var k='smirk_from',f='';
    try{{ var r=document.referrer?new URL(document.referrer):null;
      if(r&&r.origin===location.origin){{ var p=r.pathname.replace(/[/]+$/,'');
        if(p===''||p==='/index.html') sessionStorage.setItem(k,'home'); else if(p==='/thinking') sessionStorage.setItem(k,'thinking'); }}
      else sessionStorage.removeItem(k);
      f=sessionStorage.getItem(k)||''; }}catch(e){{}}
    if(f==='home'){{ var a=document.getElementById('bk'); a.href='/#notes'; a.textContent='\u2190 back to Smirk'; document.getElementById('ra').hidden=false; }} }})();</script>
  <a class="brand" href="/" aria-label="Smirk home">{MARK}<span class="wm">smirk</span></a>
</div><span class="rp" id="rp"></span></div>
<main>
  <article class="art">
    <header class="ah"><span class="bgn" aria-hidden="true">{esc(n["n"])}</span><span class="mono">Thinking in Systems · No. {esc(n["n"])} · {n["shown"]}</span><h1>{esc(n["title"])}</h1></header>
    <div class="ab">
      {note_body(n)}
      <span class="sig hand">— T.</span>
    </div>
    <a class="next" href="/thinking/{nxt["slug"]}"><span class="mono">Next note</span><b>{esc(nxt["title"])} →</b></a>
    <a class="all" href="/thinking">All notes</a>
  </article>
</main>
{FOOT}
<script>
(function(){{ var rp=document.getElementById('rp'); function f(){{ var m=document.documentElement.scrollHeight-innerHeight; rp.style.width=(m>0?Math.min(1,scrollY/m)*100:0)+'%'; }} addEventListener('scroll',f,{{passive:true}}); f(); }})();
</script>
</body>
</html>
'''

FILTER_JS = """<script>
(function(){ var bs=[].slice.call(document.querySelectorAll('.filt button')); if(!bs.length) return;
  var rows=[].slice.call(document.querySelectorAll('.nlist .nr2'));
  function set(t){ var ok=bs.some(function(b){return b.dataset.f===t;}); if(!ok) t='';
    bs.forEach(function(b){ b.setAttribute('aria-pressed', String(b.dataset.f===t)); });
    rows.forEach(function(r){ r.hidden = !!t && r.dataset.topic!==t; }); }
  bs.forEach(function(b){ b.addEventListener('click', function(){ var t=b.dataset.f; set(t);
    try{ history.replaceState(null,'', t ? '#'+encodeURIComponent(t.toLowerCase()) : location.pathname); }catch(e){} }); });
  var h=decodeURIComponent(location.hash.slice(1)).toLowerCase();
  if(h){ var m=bs.filter(function(b){return b.dataset.f.toLowerCase()===h;})[0]; if(m) set(m.dataset.f); } })();
</script>"""

def index_page(notes):
    rows = '\n      '.join(row(n, '') for n in notes)
    topics = sorted({n['topic'] for n in notes if n['topic']})
    filt = ''
    if len(topics) > 1:
        btns = f'<button type="button" data-f="" aria-pressed="true">All<sup>{len(notes)}</sup></button>' + ''.join(
            f'<button type="button" data-f="{esc(t)}" aria-pressed="false">{esc(t)}<sup>{sum(1 for n in notes if n["topic"] == t)}</sup></button>' for t in topics)
        filt = f'<div class="filt" role="group" aria-label="Filter notes by topic"><span class="lb mono">Filter</span>{btns}</div>'
    return head('Thinking in Systems — notes from Smirk', 'Notes, mind dumps and half-built ideas from Smirk on systems, software and how businesses actually run.', '/thinking') + f'''
<body>
<header class="abs"><div class="in pad">
  <a class="brand" href="/" aria-label="Smirk home">{MARK}<span class="wm">smirk</span></a>
  <a class="back hand" href="/#notes">← back to Smirk</a>
</div></header>
<section class="top pad blue">
  <span class="kick hand">notes, mind dumps &amp; half-built ideas ↓</span>
  <h1>Thinking in <span class="c">systems{CIRC}</span></h1>
  <p class="sub">What we’re learning while building software, systems and products. Written mostly for us.</p>
</section>
<main class="list pad">
  {filt}
  <div class="nlist">
      {rows}
  </div>
</main>
{FOOT}
{TOUCH_JS}
{FILTER_JS}
</body>
</html>
'''

def proof_page():
    data = json.load(open(os.path.join(ROOT, 'content', 'proof.json'), encoding='utf-8'))
    i, out = 0, []
    for g in data['groups']:
        rows = []
        for it in g['items']:
            i += 1
            live = ' on' if it['status'].lower() == 'live' else ''
            rows.append(f'''<article class="pi"><span class="n" aria-hidden="true">{i:02d}</span><div>
        <div class="hd"><h3>{esc(it["title"])}</h3><span class="st mono{live}">{esc(it["status"])}</span>{('<span class="hn hand">' + esc(it["note"]) + '</span>') if it.get("note") else ''}</div>
        <div class="pso"><div><span class="mono">Problem</span><p>{esc(it["problem"])}</p></div><div><span class="mono">What we built</span><p>{esc(it["built"])}</p></div><div class="oc"><span class="mono">Outcome</span><p>{esc(it["outcome"])}</p></div></div>
      </div></article>''')
        lead = f'<p>{esc(g["lead"])}</p>' if g.get('lead') else ''
        out.append(f'<section class="grp"><div class="gh"><h2>{esc(g["label"])}</h2>{lead}</div>\n      ' + '\n      '.join(rows) + '\n    </section>')
    return head('Proof — what Smirk has built', 'The systems, tools and products Smirk has built or is building. No client names: the problem, what we built, and what changed.', '/proof') + f'''
<body>
<header class="abs"><div class="in pad">
  <a class="brand" href="/" aria-label="Smirk home">{MARK}<span class="wm">smirk</span></a>
  <a class="back hand" href="/">← back to Smirk</a>
</div></header>
<section class="top pad blue">
  <span class="kick hand">show, don’t tell ↓</span>
  <h1><span class="u">Proof<svg viewBox="0 0 400 40" preserveAspectRatio="none" aria-hidden="true"><path vector-effect="non-scaling-stroke" d="M6 16 C90 5 210 7 394 13 M48 31 C150 22 262 23 366 27"/></svg></span></h1>
  <p class="sub">Some of what we’ve built. No client names; the work is theirs to talk about. Just the problem, what we built, and what changed.</p>
</section>
<main class="pf pad">
    {chr(10).join(out)}
</main>
<section class="pband blue pad"><p class="big">No screenshots.<span>Their systems. Their business.</span></p><span class="fin hand">we’ll walk you through one, though.</span></section>
{FOOT}
{TOUCH_JS.replace(".nr2", ".pi")}
</body>
</html>
'''

def not_found_page():
    css = """
.nf{min-height:100svh;display:flex;flex-direction:column;background:var(--cob);color:var(--cream);background-image:radial-gradient(70% 60% at 76% 20%,rgba(142,160,255,.36),rgba(142,160,255,0)),linear-gradient(rgba(242,240,235,.07) 1px,transparent 1px),linear-gradient(90deg,rgba(242,240,235,.07) 1px,transparent 1px);background-size:auto,32px 32px,32px 32px}
.nf header{height:68px;display:flex;align-items:center}
.nf .mid{flex:1;display:flex;flex-direction:column;justify-content:center;padding-top:20px;padding-bottom:clamp(60px,10vh,120px)}
.nf .kick{font-size:clamp(24px,2.3vw,34px);line-height:1;transform:rotate(-2deg);transform-origin:left;display:inline-block;margin-bottom:10px}
.nf h1{margin:0;font-weight:500;font-size:clamp(120px,30vw,460px);line-height:.82;letter-spacing:-.06em}
.nf h1 span{color:var(--peri)}
.nf p{margin:clamp(22px,2.6vw,36px) 0 0;max-width:30em;font-size:clamp(18px,1.6vw,24px);line-height:1.4;color:rgba(242,240,235,.92)}
.nf .acts{display:flex;flex-wrap:wrap;align-items:center;gap:16px 26px;margin-top:clamp(28px,3.4vw,44px)}
.nf .btn{display:inline-block;font-size:19px;font-weight:500;letter-spacing:-.01em;background:var(--cream);color:var(--ink);border:1.5px solid var(--cream);padding:16px 26px;transition:background .2s,color .2s,border-color .2s}
.nf .btn:hover{background:var(--ink);color:var(--cream);border-color:var(--ink)}
.nf .alt{font-size:17px;border-bottom:1.5px solid currentColor;padding-bottom:3px}
.nf .alt:hover{color:var(--peri)}
"""
    return head('Page not found — Smirk', 'That page does not exist.', '/404', noindex=True).replace('</style>', css + '</style>') + f'''
<body>
<div class="nf pad blue">
  <header><a class="brand" href="/" aria-label="Smirk home">{MARK}<span class="wm">smirk</span></a></header>
  <div class="mid">
    <span class="kick hand">well, that broke ↓</span>
    <h1>4<span>0</span>4</h1>
    <p>This page doesn’t exist. The system’s fine. The link isn’t.</p>
    <div class="acts"><a class="btn" href="/">Return home →</a><a class="alt" href="/thinking">Read the notes</a></div>
  </div>
</div>
</body>
</html>
'''

def main():
    notes = load_notes()
    if os.path.exists(DIST): shutil.rmtree(DIST)
    os.makedirs(os.path.join(DIST, 'thinking'))
    for f in os.listdir(os.path.join(ROOT, 'static')): shutil.copy(os.path.join(ROOT, 'static', f), os.path.join(DIST, f))
    home = open(os.path.join(ROOT, 'src', 'home.html'), encoding='utf-8').read()
    assert home.count('<!--NOTES-->') == 1
    home = home.replace('<!--NOTES-->', '\n      ' + '\n      '.join(row(n, '') for n in notes[:HOME_COUNT]) + '\n    ')
    open(os.path.join(DIST, 'index.html'), 'w', encoding='utf-8').write(home)
    shutil.copy(os.path.join(ROOT, 'src', 'work-together.html'), os.path.join(DIST, 'work-together.html'))
    open(os.path.join(DIST, 'thinking', 'index.html'), 'w', encoding='utf-8').write(index_page(notes))
    for i, n in enumerate(notes):
        open(os.path.join(DIST, 'thinking', n['slug'] + '.html'), 'w', encoding='utf-8').write(note_page(n, notes[(i + 1) % len(notes)]))
    open(os.path.join(DIST, '404.html'), 'w', encoding='utf-8').write(not_found_page())
    open(os.path.join(DIST, 'proof.html'), 'w', encoding='utf-8').write(proof_page())
    today = datetime.date.today().isoformat()
    urls = [('/', today), ('/proof', today), ('/work-together', today), ('/thinking', today)] + [(f'/thinking/{n["slug"]}', n['date'].isoformat()) for n in notes if not n['draft']]
    open(os.path.join(DIST, 'sitemap.xml'), 'w').write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + ''.join(f'  <url><loc>{BASE}{u}</loc><lastmod>{d}</lastmod></url>\n' for u, d in urls) + '</urlset>\n')
    print(f'built {len(notes)} notes ({sum(n["draft"] for n in notes)} drafts hidden from search) -> dist/')

if __name__ == '__main__':
    main()
