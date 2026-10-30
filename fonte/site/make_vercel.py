# -*- coding: utf-8 -*-
"""Monta o repositório de publicação no Vercel a partir de site/dist-web/.

Uso (da pasta site/):
  python3 build.py --web && python3 make_vercel.py ../repo

Resultado em ../repo:
  index.html, criadores/, ...   site estático (o Vercel serve a raiz do repositório)
  api/contato.js                função que envia os formulários por e-mail (Resend)
  vercel.json                   redirecionamentos e cabeçalhos (convertidos de _redirects/_headers)
  fonte/                        código-fonte para gerar o site de novo (não vai ao ar: .vercelignore)
"""
import json, os, re, shutil, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DIST = os.path.join(HERE, 'dist-web')
OUT = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, 'repo'))

def splat(p):
    return p[:-2] + '/:path*' if p.endswith('/*') else p

def redirects():
    out = []
    for line in open(os.path.join(DIST, '_redirects'), encoding='utf-8'):
        line = line.split('#', 1)[0] if line.lstrip().startswith('#') else line
        parts = line.split()
        if len(parts) < 3 or parts[0].startswith('http'):
            continue  # domínio canônico: feito em Settings > Domains do Vercel
        src, dst, code = parts[0], parts[1], parts[2].rstrip('!')
        if code == '200':
            continue  # /app já é /app/index.html
        dst = dst.replace(':splat', ':path*')
        out.append({'source': splat(src), 'destination': dst, 'permanent': code == '301'})
    return out

def headers():
    out, cur = [], None
    for line in open(os.path.join(DIST, '_headers'), encoding='utf-8'):
        if not line.strip():
            continue
        if not line.startswith(' '):
            src = line.strip()
            src = src[:-1] + '(.*)' if src.endswith('*') else src
            cur = {'source': src, 'headers': []}
            out.append(cur)
        else:
            k, v = line.strip().split(':', 1)
            cur['headers'].append({'key': k.strip(), 'value': v.strip()})
    return out

def main():
    assert os.path.exists(os.path.join(DIST, 'index.html')), 'rode antes: python3 build.py --web'
    if os.path.exists(OUT):
        for f in os.listdir(OUT):
            if f == '.git':
                continue
            p = os.path.join(OUT, f)
            shutil.rmtree(p) if os.path.isdir(p) else os.remove(p)
    os.makedirs(OUT, exist_ok=True)
    for f in os.listdir(DIST):
        if f in ('_redirects', '_headers'):
            continue
        s = os.path.join(DIST, f)
        (shutil.copytree if os.path.isdir(s) else shutil.copy)(s, os.path.join(OUT, f))
    shutil.copytree(os.path.join(ROOT, 'vercel', 'api'), os.path.join(OUT, 'api'))
    cfg = {
        '$schema': 'https://openapi.vercel.sh/vercel.json',
        'framework': None, 'buildCommand': '', 'installCommand': '', 'outputDirectory': '.',
        'trailingSlash': True,
        'redirects': redirects(),
        'headers': headers(),
    }
    json.dump(cfg, open(os.path.join(OUT, 'vercel.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    open(os.path.join(OUT, '.vercelignore'), 'w').write('fonte\nREADME.md\n')
    open(os.path.join(OUT, '.gitignore'), 'w').write('.vercel\nfonte/site/dist/\nfonte/site/dist-web/\n__pycache__/\n.DS_Store\n')
    # código-fonte
    fonte = os.path.join(OUT, 'fonte')
    ign = shutil.ignore_patterns('dist', 'dist-web', '__pycache__', '*.pyc')
    shutil.copytree(os.path.join(ROOT, 'seo'), os.path.join(fonte, 'seo'), ignore=ign)
    shutil.copytree(HERE, os.path.join(fonte, 'site'), ignore=ign)
    shutil.copytree(os.path.join(ROOT, 'vercel'), os.path.join(fonte, 'vercel'))
    shutil.copy(os.path.join(ROOT, 'vercel', 'README.md'), os.path.join(OUT, 'README.md'))
    n = sum(len(fs) for _, _, fs in os.walk(OUT))
    print('ok', OUT, n, 'arquivos;', len(cfg['redirects']), 'redirecionamentos')

if __name__ == '__main__':
    main()
