import re,json,os,urllib.parse,html
urls=[l.strip() for l in open('migration/post-urls.txt') if l.strip()]
PRIO=['mood','wine','stories','uncorked','recipes']
def meta(t,prop):
    m=re.search(r'<meta[^>]+(?:property|name)="'+re.escape(prop)+r'"[^>]+content="([^"]*)"',t) or \
      re.search(r'<meta[^>]+content="([^"]*)"[^>]+(?:property|name)="'+re.escape(prop)+r'"',t)
    return html.unescape(m.group(1)) if m else ''
def ld(t):
    m=re.search(r'<script type="application/ld\+json">(.*?)</script>', t, re.S)
    if not m: return {}
    try: return json.loads(m.group(1))
    except: return {}
out=[]
for u in urls:
    slug=urllib.parse.unquote(u.rsplit('/post/',1)[-1])
    raw=f'migration/raw/{re.sub(r"[^A-Za-z0-9_.-]","_",slug)}.html'
    t=open(raw,encoding='utf-8',errors='ignore').read()
    d=ld(t)
    cats=sorted(set(re.findall(r'/categories/([a-z]+)',t)))
    primary=next((c for c in PRIO if c in cats),'recipes')
    title=d.get('headline') or meta(t,'og:title')
    title=re.sub(r'\s*\|\s*.*$','',title).strip()
    date=(d.get('datePublished') or meta(t,'article:published_time'))[:10]
    hero=''
    if isinstance(d.get('image'),dict): hero=d['image'].get('url','')
    if not hero: hero=meta(t,'og:image')
    rec={'slug':slug,'url':u,'title':title,'date':date,
         'excerpt':(d.get('description') or meta(t,'og:description'))[:400],
         'hero':hero,'category':primary,'categories':cats}
    out.append(rec)
out.sort(key=lambda r:r['date'],reverse=True)
json.dump(out,open('migration/index.json','w'),ensure_ascii=False,indent=1)
from collections import Counter
print('by category:',dict(Counter(r['category'] for r in out)))
print('missing title:',[r['slug'] for r in out if not r['title']])
print('missing date:',[r['slug'] for r in out if not r['date']])
print('TOTAL',len(out))
