#!/usr/bin/env python3
# Builds the full xinomavri.com static mirror from migration/index.json + migration/bodies/*.json
import json, os, re, html, glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, 'site')
idx = json.load(open(os.path.join(ROOT,'migration','index.json')))
bodies = {}
for f in glob.glob(os.path.join(ROOT,'migration','bodies','*.json')):
    try:
        d = json.load(open(f)); bodies[d['slug']] = d
    except Exception as e:
        print('bad body', f, e)

CAT_LABEL = {'recipes':'Recipes','wine':'Wine','stories':'Stories','mood':'Mood','uncorked':'Uncorked'}
GR_MONTH = ['Ιανουαρίου','Φεβρουαρίου','Μαρτίου','Απριλίου','Μαΐου','Ιουνίου','Ιουλίου','Αυγούστου','Σεπτεμβρίου','Οκτωβρίου','Νοεμβρίου','Δεκεμβρίου']
def gr_date(d):
    m = re.match(r'(\d{4})-(\d{2})-(\d{2})', d or '')
    if not m: return ''
    y,mo,da = m.groups(); return f"{int(da)} {GR_MONTH[int(mo)-1]} {y}"

def esc(s): return html.escape(s or '', quote=True)
def post_href(slug): return f"post-{re.sub(r'[^A-Za-z0-9_-]','-',slug)}.html"
def thumb(r):
    return r.get('hero_local') or (f"images/posts/{r['slug']}/01.jpg" if os.path.isdir(os.path.join(SITE,'images','posts',r['slug'])) else '')

CSS = """
:root{--paper:#FFFFFF;--ink:#2B2B2B;--soft:#8B8B8B;--line:#ECECEC;--coral:#E44650}
*{box-sizing:border-box;margin:0;padding:0}
html{scroll-behavior:smooth}
body{background:var(--paper);color:var(--ink);font-family:'Commissioner',Helvetica,Arial,sans-serif;font-weight:300;font-size:16px;line-height:1.7;-webkit-font-smoothing:antialiased;text-rendering:optimizeLegibility;overflow-x:clip}
a{color:inherit;text-decoration:none}
img{display:block;max-width:100%}
.wrap{max-width:1080px;margin:0 auto;padding:0 32px}
.narrow{max-width:720px}
.masthead{padding:34px 0 0;text-align:center}
.masthead .logo{max-width:220px;margin:0 auto}
.masthead .tagline{margin:16px auto 0;font-weight:200;font-size:15px;letter-spacing:.02em;color:#6f6f6f;max-width:34ch}
.mainnav{margin-top:26px;border-top:1px solid var(--line);border-bottom:1px solid var(--line)}
.mainnav ul{list-style:none;display:flex;justify-content:center;flex-wrap:wrap;gap:34px;padding:16px 0}
.mainnav a{font-size:13px;font-weight:400;letter-spacing:.08em;color:var(--ink);text-transform:uppercase;transition:color .25s}
.mainnav a:hover,.mainnav a.on{color:var(--coral)}
.carousel{position:relative;height:74vh;min-height:460px;overflow:hidden;background:#c9c4bd}
.slides{height:100%;position:relative}
.slide{position:absolute;inset:0;background:#c9c4bd center/cover no-repeat;display:flex;align-items:center;justify-content:center;text-align:center;opacity:0;transition:opacity 1s ease;pointer-events:none}
.slide.on{opacity:1;pointer-events:auto}
.slide::after{content:"";position:absolute;inset:0;background:rgba(30,26,24,.32)}
.slide .cap{position:relative;z-index:2;color:#fff;padding:0 24px;max-width:900px}
.slide .cat{font-size:12px;letter-spacing:.24em;text-transform:uppercase;font-weight:400;opacity:.92}
.slide h1{font-weight:200;font-size:clamp(30px,5vw,58px);letter-spacing:.06em;text-transform:uppercase;line-height:1.14;margin:16px 0 10px;text-shadow:0 2px 24px rgba(0,0,0,.4)}
.slide .sub{font-weight:300;font-size:clamp(15px,2vw,20px);letter-spacing:.02em;text-shadow:0 1px 14px rgba(0,0,0,.45)}
.slide .go{display:inline-block;margin-top:26px;font-size:12px;letter-spacing:.18em;text-transform:uppercase;color:#fff;border-bottom:1px solid rgba(255,255,255,.6);padding-bottom:5px;transition:border-color .3s}
.slide:hover .go{border-color:#fff}
.car-btn{position:absolute;top:50%;transform:translateY(-50%);z-index:5;width:46px;height:46px;border:none;background:rgba(0,0,0,.22);color:#fff;font-size:20px;cursor:pointer;display:flex;align-items:center;justify-content:center;transition:background .25s}
.car-btn:hover{background:rgba(228,70,80,.85)}
.car-prev{left:18px}.car-next{right:18px}
.car-dots{position:absolute;bottom:22px;left:0;right:0;z-index:5;display:flex;justify-content:center;gap:10px}
.car-dots button{width:9px;height:9px;border-radius:50%;border:none;background:rgba(255,255,255,.5);cursor:pointer;padding:0;transition:background .25s,transform .25s}
.car-dots button.on{background:#fff;transform:scale(1.25)}
.pagehead{text-align:center;padding:60px 0 8px}
.pagehead .k{font-size:12px;letter-spacing:.22em;text-transform:uppercase;color:var(--coral);font-weight:500}
.pagehead h1{font-weight:200;font-size:clamp(32px,5vw,52px);letter-spacing:.02em;margin-top:8px}
.pagehead p{color:var(--soft);font-size:15px;margin-top:8px}
.sec-title{text-align:center;margin:74px 0 40px}
.sec-title span{font-size:12px;letter-spacing:.22em;text-transform:uppercase;color:var(--coral);font-weight:500}
.sec-title h2{font-weight:200;font-size:32px;letter-spacing:.02em;margin-top:8px}
.posts{display:grid;grid-template-columns:repeat(3,1fr);gap:44px 34px;margin-top:44px}
.post{display:block}
.post .ph{aspect-ratio:3/2;overflow:hidden;background:#EFEDE9;position:relative}
.post .ph img{width:100%;height:100%;object-fit:cover;transition:transform .6s ease}
.post .ph .noimg{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;background:var(--coral);color:#fff;font-weight:200;font-size:22px;letter-spacing:.05em;padding:16px;text-align:center}
.post:hover .ph img{transform:scale(1.045)}
.post .cat{margin-top:16px;font-size:11px;letter-spacing:.16em;text-transform:uppercase;color:var(--coral);font-weight:500}
.post h3{font-weight:400;font-size:20px;line-height:1.3;margin-top:7px}
.post p{margin-top:8px;color:var(--soft);font-size:14px;font-weight:300;line-height:1.6}
.post .meta{margin-top:10px;font-size:11.5px;letter-spacing:.03em;color:#b3b3b3}
.morebtn{text-align:center;margin-top:56px}
.morebtn a{display:inline-block;font-size:12px;letter-spacing:.16em;text-transform:uppercase;color:var(--ink);border:1px solid var(--ink);padding:13px 34px;transition:all .25s}
.morebtn a:hover{background:var(--ink);color:#fff}
.subscribe{margin-top:96px;border-top:1px solid var(--line);border-bottom:1px solid var(--line);padding:64px 0;text-align:center}
.subscribe h3{font-weight:200;font-size:26px;letter-spacing:.03em}
.subscribe p{color:var(--soft);font-size:14px;margin-top:8px}
.subscribe form{margin:26px auto 0;max-width:440px;display:flex;border:1px solid #d9d9d9}
.subscribe input{flex:1;border:none;padding:13px 16px;font-family:inherit;font-size:14px;outline:none;background:transparent}
.subscribe button{border:none;background:var(--coral);color:#fff;font-family:inherit;font-size:12px;letter-spacing:.14em;text-transform:uppercase;padding:0 24px;cursor:pointer}
article{padding:52px 0 20px}
.crumb{font-size:11.5px;letter-spacing:.1em;text-transform:uppercase;color:var(--coral);font-weight:500}
article h1.title{font-weight:200;font-size:clamp(30px,4.6vw,50px);letter-spacing:.01em;line-height:1.12;margin:14px 0 12px}
.byline{font-size:12.5px;letter-spacing:.04em;color:#a9a9a9;display:flex;gap:10px;flex-wrap:wrap;align-items:center}
.byline b{font-weight:500;color:#7d7d7d}
.arthero{margin:34px 0 8px}
.arthero img{width:100%;aspect-ratio:16/10;object-fit:cover;background:#EFEDE9}
.body{font-size:17px;line-height:1.85;color:#333}
.body p{margin:20px 0}
.body h2{font-weight:300;font-size:28px;margin:38px 0 6px;color:#222}
.body h3{font-weight:500;font-size:13px;letter-spacing:.12em;text-transform:uppercase;color:var(--coral);margin:30px 0 10px}
.body ul,.body ol{margin:16px 0 20px;padding-left:22px}
.body li{margin:8px 0}
.body img{width:100%;height:auto;margin:30px 0;background:#EFEDE9}
.body figure{margin:30px 0}
.body figcaption{margin-top:8px;font-size:12px;color:var(--soft);text-align:center}
.backline{border-top:1px solid var(--line);margin-top:64px;padding:30px 0;text-align:center}
.backline a{font-size:12px;letter-spacing:.14em;text-transform:uppercase;color:var(--soft)}
.backline a:hover{color:var(--coral)}
footer{padding:56px 0 64px;text-align:center;border-top:1px solid var(--line);margin-top:80px}
footer .fl{max-width:150px;margin:0 auto 16px;opacity:.9}
footer .fnav{list-style:none;display:flex;justify-content:center;flex-wrap:wrap;gap:22px;font-size:12px;letter-spacing:.06em;text-transform:uppercase;color:var(--soft)}
footer .cr{margin-top:20px;font-size:12px;color:#b3b3b3}
footer a.mail{color:var(--ink);border-bottom:1px solid var(--coral);padding-bottom:2px}
.reveal{opacity:0;transform:translateY(20px);transition:opacity .8s ease,transform .8s ease}
.reveal.in{opacity:1;transform:none}
@media(max-width:860px){.posts{grid-template-columns:repeat(2,1fr)}.mainnav ul{gap:20px}}
@media(max-width:540px){.wrap{padding:0 22px}.posts{grid-template-columns:1fr;gap:38px}.mainnav ul{gap:15px;font-size:12px}.carousel{height:64vh}.masthead .logo{max-width:190px}}
@media(prefers-reduced-motion:reduce){.reveal{opacity:1;transform:none;transition:none}}
"""

FONT = '<link href="https://fonts.googleapis.com/css2?family=Commissioner:wght@200;300;400;500;600;700&display=swap" rel="stylesheet">'

def head(title, desc, canonical):
    return f"""<!DOCTYPE html>
<html lang="el">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="index,follow">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="https://xinomavri.com/{canonical}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:type" content="website">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
{FONT}
<style>{CSS}</style>
</head>
<body>
"""

def mast(active=''):
    def a(href,label,key):
        cls=' class="on"' if key==active else ''
        return f'<li><a href="{href}"{cls}>{label}</a></li>'
    return f"""<header class="masthead"><div class="wrap">
  <a href="index.html"><img class="logo" src="images/logo.png" alt="Ξινόμαυρη"></a>
  <p class="tagline">ιστορίες για το φαγητό και τις καλύτερες πάρτι στη ζωή μου</p>
</div>
<nav class="mainnav"><ul>
  {a('recipes.html','Recipes','recipes')}
  {a('wine.html','Wine','wine')}
  {a('stories.html','Stories','stories')}
  {a('about.html','About','about')}
  {a('blog.html','All Posts','blog')}
  {a('contact.html','Contact','contact')}
</ul></nav>
</header>
"""

FOOT = """<footer><div class="wrap">
  <img class="fl" src="images/logo.png" alt="Ξινόμαυρη">
  <ul class="fnav">
    <li><a href="recipes.html">Recipes</a></li>
    <li><a href="wine.html">Wine</a></li>
    <li><a href="stories.html">Stories</a></li>
    <li><a href="mood.html">Mood</a></li>
    <li><a href="about.html">About</a></li>
    <li><a href="contact.html">Contact</a></li>
  </ul>
  <p class="cr">© Ξινόμαυρη · <a class="mail" href="mailto:xinomavri@gmail.com">xinomavri@gmail.com</a></p>
</div></footer>
"""

REVEAL_JS = """<script>
(function(){var els=document.querySelectorAll('.reveal');if(!('IntersectionObserver' in window)){els.forEach(function(e){e.classList.add('in')});return;}
var io=new IntersectionObserver(function(en){en.forEach(function(x){if(x.isIntersecting){x.target.classList.add('in');io.unobserve(x.target);}})},{threshold:.08});
els.forEach(function(e){io.observe(e);});})();
</script>
</body></html>"""

def card(r):
    t = thumb(r)
    if t and os.path.exists(os.path.join(SITE,t)):
        ph = f'<div class="ph"><img src="{t}" alt="{esc(r["title"])}" loading="lazy"></div>'
    else:
        ph = f'<div class="ph"><div class="noimg">{esc(r["title"])}</div></div>'
    meta = f'xinomavri · {gr_date(r["date"])}' if r.get('date') else 'xinomavri'
    exc = esc((r.get('excerpt') or '')[:150])
    return f"""<a class="post reveal" href="{post_href(r['slug'])}">
  {ph}
  <div class="cat">{CAT_LABEL.get(r['category'],r['category'])}</div>
  <h3>{esc(r['title'])}</h3>
  <p>{exc}</p>
  <div class="meta">{meta}</div>
</a>"""

posts = sorted(idx, key=lambda r:r['date'], reverse=True)

# ---------- HOME ----------
feat = [r for r in posts if r.get('hero_local')][:5]
slides=[]
for k,r in enumerate(feat):
    slides.append(f"""<a class="slide{' on' if k==0 else ''}" href="{post_href(r['slug'])}" style="background-image:url('{r['hero_local']}')">
      <div class="cap"><div class="cat">{CAT_LABEL.get(r['category'],r['category'])}</div>
      <h1>{esc(r['title'])}</h1>
      <div class="sub">{esc((r.get('excerpt') or '')[:90])}</div>
      <span class="go">Διάβασε το άρθρο</span></div></a>""")
recent = ''.join(card(r) for r in posts[:9])
home = head('Ξινόμαυρη — ιστορίες για το φαγητό','Ιστορίες για το φαγητό και τις καλύτερες πάρτι στη ζωή μου. Συνταγές, κρασί και ιστορίες.','')
home += mast()
home += f"""<section class="carousel" id="carousel" aria-label="Featured">
  <div class="slides">{''.join(slides)}</div>
  <button class="car-btn car-prev" aria-label="Προηγούμενο">‹</button>
  <button class="car-btn car-next" aria-label="Επόμενο">›</button>
  <div class="car-dots" id="carDots"></div>
</section>
<div class="wrap">
  <div class="sec-title reveal"><span>Το ημερολόγιο</span><h2>Πρόσφατα στο τραπέζι</h2></div>
  <div class="posts">{recent}</div>
  <div class="morebtn reveal"><a href="blog.html">Όλες οι αναρτήσεις</a></div>
</div>
<section class="subscribe reveal"><div class="wrap">
  <h3>Subscribe</h3><p>Νέες συνταγές και ιστορίες, κατευθείαν στο inbox σου.</p>
  <form onsubmit="this.querySelector('button').textContent='Ευχαριστώ';return false;">
    <input type="email" placeholder="Το email σου" required><button type="submit">Εγγραφή</button>
  </form>
</div></section>
"""
home += FOOT
home += """<script>
(function(){var root=document.getElementById('carousel');if(!root)return;var slides=[].slice.call(root.querySelectorAll('.slide')),dw=document.getElementById('carDots'),i=0,t=null,n=slides.length;var reduce=window.matchMedia&&window.matchMedia('(prefers-reduced-motion: reduce)').matches;slides.forEach(function(_,k){var b=document.createElement('button');if(k===0)b.className='on';b.onclick=function(e){e.preventDefault();go(k);reset();};dw.appendChild(b);});var dots=[].slice.call(dw.children);function go(k){i=(k+n)%n;slides.forEach(function(s,x){s.classList.toggle('on',x===i);});dots.forEach(function(d,x){d.classList.toggle('on',x===i);});}function next(){go(i+1);}function prev(){go(i-1);}function reset(){if(reduce||n<2)return;clearInterval(t);t=setInterval(next,5500);}root.querySelector('.car-next').onclick=function(e){e.preventDefault();next();reset();};root.querySelector('.car-prev').onclick=function(e){e.preventDefault();prev();reset();};root.addEventListener('mouseenter',function(){clearInterval(t);});root.addEventListener('mouseleave',reset);var x0=null;root.addEventListener('touchstart',function(e){x0=e.touches[0].clientX;},{passive:true});root.addEventListener('touchend',function(e){if(x0===null)return;var dx=e.changedTouches[0].clientX-x0;if(Math.abs(dx)>40){dx<0?next():prev();reset();}x0=null;});reset();})();
(function(){var els=document.querySelectorAll('.reveal');if(!('IntersectionObserver' in window)){els.forEach(function(e){e.classList.add('in')});return;}var io=new IntersectionObserver(function(en){en.forEach(function(x){if(x.isIntersecting){x.target.classList.add('in');io.unobserve(x.target);}})},{threshold:.08});els.forEach(function(e){io.observe(e);});})();
</script></body></html>"""
open(os.path.join(SITE,'index.html'),'w').write(home)

# ---------- LISTING PAGES ----------
def listing(fname, active, kicker, h1, intro, subset):
    h = head(f'{h1} — Ξινόμαυρη', intro, fname)
    h += mast(active)
    grid = ''.join(card(r) for r in subset) or '<p style="text-align:center;color:#8b8b8b">Σύντομα.</p>'
    h += f"""<div class="pagehead"><div class="wrap"><div class="k">{kicker}</div><h1>{esc(h1)}</h1><p>{esc(intro)}</p></div></div>
<div class="wrap"><div class="posts" style="margin-top:44px">{grid}</div></div>
"""
    h += FOOT + REVEAL_JS
    open(os.path.join(SITE,fname),'w').write(h)

listing('blog.html','blog','Ξινόμαυρη','Όλες οι αναρτήσεις',f'{len(posts)} ιστορίες για το φαγητό και το κρασί.', posts)
for cat,label in CAT_LABEL.items():
    sub=[r for r in posts if r['category']==cat]
    intro={'recipes':'Συνταγές από ένα τραπέζι κάτω από τον κυκλαδίτικο ήλιο.','wine':'Ιστορίες για το κρασί και τους ανθρώπους του.','stories':'Ιστορίες γύρω από το φαγητό.','mood':'Η διάθεση της ημέρας.','uncorked':'Ξεβουλωμένες σκέψεις για το αμπέλι και το κρασί.'}[cat]
    listing(f'{cat}.html',cat,'Κατηγορία',label,intro,sub)

# ---------- POST PAGES ----------
built=0; missing=[]
for r in posts:
    b = bodies.get(r['slug'])
    if not b or not b.get('body_html','').strip():
        missing.append(r['slug']); continue
    hero = r.get('hero_local')
    hero_html = f'<div class="arthero"><img src="{hero}" alt="{esc(r["title"])}"></div>' if hero and os.path.exists(os.path.join(SITE,hero)) else ''
    h = head(f"{esc(r['title'])} — Ξινόμαυρη", (r.get('excerpt') or '')[:200], post_href(r['slug']))
    h += mast(r['category'] if r['category'] in CAT_LABEL else '')
    h += f"""<article><div class="wrap narrow">
  <div class="crumb">{CAT_LABEL.get(r['category'],r['category'])}</div>
  <h1 class="title">{esc(r['title'])}</h1>
  <div class="byline"><b>xinomavri</b><span>·</span><span>{gr_date(r['date'])}</span></div>
  {hero_html}
  <div class="body">{b['body_html']}</div>
</div></article>
<div class="backline"><a href="blog.html">← Όλες οι αναρτήσεις</a></div>
"""
    h += FOOT + REVEAL_JS
    open(os.path.join(SITE,post_href(r['slug'])),'w').write(h)
    built+=1

# ---------- CONTACT ----------
contact = head('Contact — Ξινόμαυρη','Επικοινωνία με την Ξινόμαυρη.','contact.html') + mast('contact')
contact += """<div class="pagehead"><div class="wrap"><div class="k">Ξινόμαυρη</div><h1>Contact</h1><p>Πες μου την ιστορία σου.</p></div></div>
<div class="wrap narrow" style="text-align:center;padding:20px 0 40px">
  <p style="font-size:18px;color:#333;margin:0 0 24px">Για συνταγές, ιστορίες, συνεργασίες ή απλώς για ένα γεια:</p>
  <p style="font-size:20px"><a href="mailto:xinomavri@gmail.com" style="color:#2B2B2B;border-bottom:1px solid var(--coral);padding-bottom:3px">xinomavri@gmail.com</a></p>
</div>
""" + FOOT + REVEAL_JS
open(os.path.join(SITE,'contact.html'),'w').write(contact)

print(f'HOME + {len(CAT_LABEL)} category pages + blog + contact built.')
print(f'POST pages built: {built} / {len(posts)}   (missing bodies: {len(missing)})')
if missing: print('missing:', ', '.join(missing[:40]))
