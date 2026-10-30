# -*- coding: utf-8 -*-
"""Monta o repositório de publicação no Vercel a partir de site/dist-web/.

Uso (da pasta site/):
  python3 build.py --web && python3 make_vercel.py ../repo

Resultado em ../repo:
  index.html, criadores/, ...   site estático (o Vercel serve a raiz do repositório)
  api/lead.js                   envia o formulário de marcas ao CRM Comercial (webhook)
  api/contato.js                formulário de suporte por e-mail (Resend)
  vercel.json                   redirecionamentos e cabeçalhos (convertidos de _redirects/_headers)
  fonte/                        código-fonte para gerar o site de novo (não vai ao ar: .vercelignore)
"""
import json, os, re, shutil, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DIST = os.path.join(HERE, 'dist-web')
OUT = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, 'repo'))

def splat(p):
    # O Vercel compara barras de forma rígida e, com trailingSlash, a barra final chega antes das regras.
    # '/x/*' vira '/x', '/x/' e qualquer coisa abaixo de '/x/' (com ou sem barra no fim).
    return p[:-2] + '(/.*)?' if p.endswith('/*') else p

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

# assets.hypeapp.com.br era um endereço do site antigo (privacidade e termos usados pelo app e pelas lojas).
# Quando ele chega neste projeto, leva direto à página nova no www.
ASSETS_HOST = 'assets.hypeapp.com.br'
def assets_host():
    has = [{'type': 'host', 'value': ASSETS_HOST}]
    www = 'https://www.hypeapp.com.br'
    regras = [
        ('/politica-de-privacidade(/.*)?', '/privacidade/'), ('/privacidade(/.*)?', '/privacidade/'),
        ('/privacy(/.*)?', '/privacidade/'), ('/privacy-policy(/.*)?', '/privacidade/'),
        ('/termos-de-uso(/.*)?', '/termos/'), ('/termos(/.*)?', '/termos/'), ('/terms(/.*)?', '/termos/'),
        ('/', '/legal/'),
        ('/(.*)', '/$1'),
    ]
    return [{'source': s, 'has': has, 'destination': www + d, 'permanent': True} for s, d in regras]

def headers():
    out, cur = [], None
    for line in open(os.path.join(DIST, '_headers'), encoding='utf-8'):
        if not line.strip():
            continue
        if not line.startswith(' '):
            src = line.strip()
            src = src[:-1] + '(.*)' if src.endswith('*') else src
            if src == '/(.*)':
                src = '/((?!backoffice).*)'   # o painel tem os próprios cabeçalhos
            cur = {'source': src, 'headers': []}
            out.append(cur)
        else:
            k, v = line.strip().split(':', 1)
            cur['headers'].append({'key': k.strip(), 'value': v.strip()})
    return out

def main():
    assert os.path.exists(os.path.join(DIST, 'index.html')), 'rode antes: python3 build.py --web'
    # Nunca publica com texto pendente entre colchetes (placeholder) ou aviso de rascunho
    pend = []
    for raiz, _, fs in os.walk(DIST):
        for f in fs:
            if f.endswith('.html'):
                t = open(os.path.join(raiz, f), encoding='utf-8').read()
                if 'class="ph"' in t or 'Rascunho para revisão' in t:
                    pend.append(os.path.relpath(os.path.join(raiz, f), DIST))
    if pend:
        sys.exit('PARADO: textos pendentes entre colchetes em ' + ', '.join(pend))
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
    # /backoffice continua no projeto do painel (mesma conta do Vercel): repassa para o endereço dele.
    # Preencha vercel/backoffice_origem.txt com o endereço do projeto do backoffice, ex.: https://hypeapp-backoffice.vercel.app
    origem_f = os.path.join(ROOT, 'vercel', 'backoffice_origem.txt')
    origem = open(origem_f).read().strip().rstrip('/') if os.path.exists(origem_f) else ''
    rewrites = [{'source': '/backoffice', 'destination': origem + '/backoffice'},
                {'source': '/backoffice/:path*', 'destination': origem + '/backoffice/:path*'}] if origem else []
    if not origem:
        print('ATENÇÃO: sem vercel/backoffice_origem.txt. Não ligue o domínio neste projeto antes de preencher: /backoffice daria 404.')
    cfg = {
        '$schema': 'https://openapi.vercel.sh/vercel.json',
        'framework': None, 'buildCommand': '', 'installCommand': '', 'outputDirectory': '.',
        'trailingSlash': True,
        'rewrites': rewrites,
        'redirects': assets_host() + redirects(),
        'headers': headers(),
    }
    json.dump(cfg, open(os.path.join(OUT, 'vercel.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    open(os.path.join(OUT, '.vercelignore'), 'w').write('fonte\nREADME.md\n')
    open(os.path.join(OUT, '.gitignore'), 'w').write('.vercel\n.env\n.env.*\nfonte/site/dist/\nfonte/site/dist-web/\n__pycache__/\n.DS_Store\n')
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
