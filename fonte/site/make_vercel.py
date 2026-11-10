# -*- coding: utf-8 -*-
"""Monta o repositório de publicação no Vercel a partir de site/dist-web/.

Uso (da pasta site/):
  python3 build.py --web && python3 make_vercel.py ../repo

Resultado em ../repo:
  index.html, criadores/, ...   site estático (o Vercel serve a raiz do repositório)
  api/lead.js                   envia os formulários de marcas e de suporte ao CRM Comercial (webhook)
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
# Endereço de teste para a equipe (ramo melhorias-seo): nunca indexado pelos buscadores
TESTE_HOST = 'teste.hypeapp.com.br'
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

def teste_host():
    # no endereço de teste, robots.txt bloqueia tudo (além do cabeçalho noindex)
    return [{'source': '/robots.txt', 'has': [{'type': 'host', 'value': TESTE_HOST}], 'destination': '/robots-homologacao.txt', 'permanent': False}]

def so_teste():
    # artigos do blog em revisão (build.py grava _so_teste.json): fora do endereço de teste, voltam para a Início
    f = os.path.join(DIST, '_so_teste.json')
    caminhos = json.load(open(f)) if os.path.exists(f) else []
    fora = [{'type': 'host', 'value': TESTE_HOST}]
    return [{'source': c.rstrip('/') + '(/.*)?', 'missing': fora, 'destination': '/', 'permanent': False} for c in caminhos]

def sem_index_html():
    # /marcas/index.html e /index.html abrem a mesma página: leva ao endereço limpo
    return [{'source': '/index.html', 'destination': '/', 'permanent': True},
            {'source': '/:path([A-Za-z0-9._~-]+(?:/[A-Za-z0-9._~-]+)*)/index.html', 'destination': '/:path/', 'permanent': True}]   # só caracteres de caminho comuns (auditoria 10/11: com \\ virava redirecionamento para fora)

def headers():
    out, cur = [], None
    for line in open(os.path.join(DIST, '_headers'), encoding='utf-8'):
        if not line.strip():
            continue
        if not line.startswith(' '):
            src = line.strip()
            src = src[:-1] + '(.*)' if src.endswith('*') else src
            if src == '/(.*)' and os.path.exists(os.path.join(ROOT, 'vercel', 'backoffice_origem.txt')):
                src = '/((?!backoffice).*)'   # só quando o painel é servido pelo www (rewrite): ele tem os próprios cabeçalhos
            cur = {'source': src, 'headers': []}
            out.append(cur)
        else:
            k, v = line.strip().split(':', 1)
            cur['headers'].append({'key': k.strip(), 'value': v.strip()})
    return out

RELATORIO_EMAIL_YML = """name: Relatório semanal (e-mail)
# Envia o relatório da semana por e-mail. Disparado pelo agente de análise com o relatório em JSON.
# Destinatários fixos na variável RELATORIO_EMAILS; SMTP nos segredos SMTP_USER e SMTP_PASS.
on:
  workflow_dispatch:
    inputs:
      relatorio:
        description: Relatório da semana em JSON
        required: true
permissions:
  contents: read
jobs:
  email:
    runs-on: ubuntu-latest
    timeout-minutes: 5
    steps:
      - uses: actions/checkout@11d5960a326750d5838078e36cf38b85af677262 # v4.4.0
        with:
          persist-credentials: false
          sparse-checkout: |
            relatorio
            api
      - uses: actions/setup-node@49933ea5288caeca8642d1e84afbd3f7d6820020 # v4.4.0
        with:
          node-version: 20
      - name: Enviar
        env:
          RELATORIO_JSON: ${{ inputs.relatorio }}
          RELATORIO_EMAILS: ${{ vars.RELATORIO_EMAILS }}
          SMTP_USER: ${{ secrets.SMTP_USER }}
          SMTP_PASS: ${{ secrets.SMTP_PASS }}
        run: node relatorio/envia-email.mjs
"""

RELATORIO_YML = """name: Relatório semanal (coleta)
# Coleta GA4 e Search Console da última semana fechada (segunda a domingo) e das 4 anteriores.
# Resultado: dados/AAAA-MM-DD.json e dados/ultimo.json no ramo "dados-relatorio" (contagens e rótulos; os rótulos de campanha, página e busca vêm de visitantes e são texto não confiável),
# lidos pelo agente que escreve o relatório. Esse ramo tem deploy desligado no Vercel.
# Precisa de: secret GA_SA_JSON e variáveis GA4_PROPERTY_ID e GSC_SITE (veja relatorio/LEIA-ME.md).
on:
  schedule:
    - cron: '7 11 * * 1'   # segunda, 08h07 de Brasília
  workflow_dispatch:
permissions:
  contents: write
jobs:
  coleta:
    runs-on: ubuntu-latest
    timeout-minutes: 10
    steps:
      - uses: actions/checkout@11d5960a326750d5838078e36cf38b85af677262 # v4.4.0
        with:
          persist-credentials: false
          sparse-checkout: relatorio
      - uses: actions/setup-node@49933ea5288caeca8642d1e84afbd3f7d6820020 # v4.4.0
        with:
          node-version: 20
      - name: Coletar dados
        env:
          GA_SA_JSON: ${{ secrets.GA_SA_JSON }}
          GA4_PROPERTY_ID: ${{ vars.GA4_PROPERTY_ID }}
          GSC_SITE: ${{ vars.GSC_SITE }}
        run: node relatorio/coleta.mjs > dados-semana.json
      - name: Guardar no ramo dados-relatorio
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          SEMANA=$(jq -r '.semanas[-1].inicio' dados-semana.json)
          mkdir -p /tmp/dr && cd /tmp/dr
          git init -q
          git config user.name "relatorio-semanal"
          git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
          git remote add origin "https://x-access-token:${GH_TOKEN}@github.com/${GITHUB_REPOSITORY}.git"
          if git fetch -q origin dados-relatorio; then git checkout -q -b dados-relatorio FETCH_HEAD; else git checkout -q --orphan dados-relatorio; fi
          mkdir -p dados
          cp "$GITHUB_WORKSPACE/dados-semana.json" "dados/$SEMANA.json"
          cp "$GITHUB_WORKSPACE/dados-semana.json" dados/ultimo.json
          echo '{"git":{"deploymentEnabled":false}}' > vercel.json
          echo 'Dados do relatório semanal (gerados pelo GitHub Actions). Não editar.' > README.md
          git add -A
          git commit -q -m "Dados da semana de $SEMANA" || echo "sem mudanças"
          git push -q origin dados-relatorio
"""

INDEXNOW_YML = r"""name: Avisar buscadores (IndexNow)
# Envia as URLs do sitemap ao IndexNow (Bing, Yandex, Seznam, Naver e outros).
# Rode manualmente depois de publicar mudanças: Actions > Avisar buscadores (IndexNow) > Run workflow.
on:
  workflow_dispatch:
permissions:
  contents: read
jobs:
  indexnow:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@11d5960a326750d5838078e36cf38b85af677262 # v4.4.0
        with:
          persist-credentials: false
      - name: Enviar URLs do sitemap
        run: |
          KEY=$(ls | grep -E '^[0-9a-f]{32}\.txt$' | head -1 | sed 's/\.txt$//')
          URLS=$(grep -o '<loc>[^<]*</loc>' sitemap.xml | sed -e 's#<loc>##' -e 's#</loc>##' | python3 -c "import sys,json;print(json.dumps([l.strip() for l in sys.stdin if l.strip()]))")
          BODY="{\"host\":\"www.hypeapp.com.br\",\"key\":\"$KEY\",\"keyLocation\":\"https://www.hypeapp.com.br/$KEY.txt\",\"urlList\":$URLS}"
          curl -sS -X POST https://api.indexnow.org/indexnow -H 'Content-Type: application/json; charset=utf-8' -d "$BODY" -w '\nHTTP %{http_code}\n'
"""

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
        if f in ('_redirects', '_headers', '_so_teste.json'):
            continue
        s = os.path.join(DIST, f)
        (shutil.copytree if os.path.isdir(s) else shutil.copy)(s, os.path.join(OUT, f))
    # imagens dos e-mails de confirmação, embutidas na função (site/assets/email → vercel/api/_imagens.js)
    import base64, glob as _g, json as _j
    imgs = {}
    for f in sorted(_g.glob(os.path.join(ROOT, 'site', 'assets', 'email', '*'))):
        nome, ext = os.path.splitext(os.path.basename(f))
        imgs[nome] = {'tipo': 'image/png' if ext == '.png' else 'image/jpeg', 'ext': ext[1:], 'b64': base64.b64encode(open(f, 'rb').read()).decode()}
    open(os.path.join(ROOT, 'vercel', 'api', '_imagens.js'), 'w').write(
        '// Gerado pelo make_vercel.py a partir de site/assets/email: imagens dos e-mails de confirmação, anexadas no próprio e-mail (cid).\n'
        'module.exports = ' + _j.dumps(imgs) + ';\n')
    shutil.copytree(os.path.join(ROOT, 'vercel', 'api'), os.path.join(OUT, 'api'))
    # /backoffice continua no projeto do painel (mesma conta do Vercel): repassa para o endereço dele.
    # Preencha vercel/backoffice_origem.txt com o endereço do projeto do backoffice, ex.: https://hypeapp-backoffice.vercel.app
    origem_f = os.path.join(ROOT, 'vercel', 'backoffice_origem.txt')
    origem = open(origem_f).read().strip().rstrip('/') if os.path.exists(origem_f) else ''
    rewrites = [{'source': '/backoffice', 'destination': origem + '/backoffice'},
                {'source': '/backoffice/:path*', 'destination': origem + '/backoffice/:path*'}] if origem else []
    # Sem origem (decisão de 06/11): o painel fica no próprio endereço; links antigos de www/backoffice/... vão para lá.
    PAINEL = 'https://backoffice-v2.hypeapp.com.br'
    painel_redir = [] if origem else [
        {'source': '/backoffice(/)?', 'destination': PAINEL + '/sign-in', 'permanent': False},
        {'source': '/backoffice/:path+', 'destination': PAINEL + '/:path+', 'permanent': False}]
    # Perfis públicos da versão anterior (/u/<nome>, /pt-BR/<nome>): mostram o aviso de /perfil-antigo/, sem índice (06/11)
    # Padrões com a barra final opcional, como os outros redirecionamentos (trailingSlash ligado)
    rewrites = rewrites + [{'source': '/u/(.+)', 'destination': '/perfil-antigo/'}, {'source': '/pt-BR/(.+)', 'destination': '/perfil-antigo/'}]
    perfis_redir = [{'source': '/u(/)?', 'destination': '/', 'permanent': True}, {'source': '/pt-BR(/)?', 'destination': '/', 'permanent': True}]
    perfis_hdr = [{'source': '/(u|pt-BR|perfil-antigo)/(.*)', 'headers': [{'key': 'X-Robots-Tag', 'value': 'noindex'}]}]
    cfg = {
        '$schema': 'https://openapi.vercel.sh/vercel.json',
        'framework': None, 'buildCommand': '', 'installCommand': '', 'outputDirectory': '.',
        'trailingSlash': True,
        'functions': {'api/lead.js': {'maxDuration': 30}},  # webhook (até 10 s) + e-mail de confirmação (até 6 s)
        'rewrites': rewrites,
        'redirects': painel_redir + perfis_redir + assets_host() + teste_host() + so_teste() + sem_index_html() + redirects(),
        'headers': headers() + perfis_hdr + [{'source': '/(.*)', 'has': [{'type': 'host', 'value': TESTE_HOST}],
                                 'headers': [{'key': 'X-Robots-Tag', 'value': 'noindex, nofollow'}]}],
    }
    json.dump(cfg, open(os.path.join(OUT, 'vercel.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    open(os.path.join(OUT, '.vercelignore'), 'w').write('fonte\nREADME.md\n.github\nrelatorio\n')
    # IndexNow: envio manual pelo GitHub (Actions → Avisar buscadores → Run workflow), depois que o site estiver no ar
    wf = os.path.join(OUT, '.github', 'workflows'); os.makedirs(wf, exist_ok=True)
    open(os.path.join(wf, 'indexnow.yml'), 'w', encoding='utf-8').write(INDEXNOW_YML)
    # Relatório semanal: coleta de GA4 e Search Console toda segunda (08h de Brasília), lida pelo agente de análise
    shutil.copytree(os.path.join(ROOT, 'relatorio'), os.path.join(OUT, 'relatorio'))
    open(os.path.join(wf, 'relatorio-semanal.yml'), 'w', encoding='utf-8').write(RELATORIO_YML)
    open(os.path.join(wf, 'relatorio-email.yml'), 'w', encoding='utf-8').write(RELATORIO_EMAIL_YML)
    open(os.path.join(OUT, '.gitignore'), 'w').write('.vercel\n.env\n.env.*\nfonte/site/dist/\nfonte/site/dist-web/\n__pycache__/\n.DS_Store\n*.log\nfonte/site/ck-*.png\n')
    # código-fonte
    fonte = os.path.join(OUT, 'fonte')
    ign = shutil.ignore_patterns('dist', 'dist-web', '__pycache__', '*.pyc', '*.log', 'ck-*.png')
    shutil.copytree(os.path.join(ROOT, 'seo'), os.path.join(fonte, 'seo'), ignore=ign)
    shutil.copytree(HERE, os.path.join(fonte, 'site'), ignore=ign)
    shutil.copytree(os.path.join(ROOT, 'vercel'), os.path.join(fonte, 'vercel'))
    shutil.copytree(os.path.join(ROOT, 'relatorio'), os.path.join(fonte, 'relatorio'))
    shutil.copy(os.path.join(ROOT, 'vercel', 'README.md'), os.path.join(OUT, 'README.md'))
    n = sum(len(fs) for _, _, fs in os.walk(OUT))
    print('ok', OUT, n, 'arquivos;', len(cfg['redirects']), 'redirecionamentos')

if __name__ == '__main__':
    main()
