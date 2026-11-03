# -*- coding: utf-8 -*-
"""Blog do HypeApp: lê content/blog/*.md (ver content/blog/LEIA-ME.md) e gera os trechos de HTML.
Usado por build.py. Nada aqui inventa data, autor ou tempo de leitura: tudo vem do arquivo do artigo."""
import os, re, math, datetime, html
import markdown as _md

MESES = ['janeiro', 'fevereiro', 'março', 'abril', 'maio', 'junho', 'julho', 'agosto', 'setembro', 'outubro', 'novembro', 'dezembro']

def load_posts(here, web):
    pasta = os.path.join(here, 'content', 'blog')
    posts = []
    for fn in sorted(os.listdir(pasta)):
        if not fn.endswith('.md') or fn.upper().startswith('LEIA-ME'):
            continue
        raw = open(os.path.join(pasta, fn), encoding='utf-8').read()
        m = re.match(r'^---\n(.*?)\n---\n(.*)$', raw, re.S)
        assert m, f'{fn}: falta o cabeçalho entre ---'
        meta = {}
        for line in m.group(1).splitlines():
            if ':' in line:
                k, v = line.split(':', 1)
                meta[k.strip()] = v.strip()
        body = m.group(2).strip()
        st = meta.get('status', 'rascunho')
        if st not in ('publicado', 'exemplo'):
            continue
        slug = fn[:-3]
        assert re.fullmatch(r'[a-z0-9]+(-[a-z0-9]+)*', slug), f'{fn}: o nome do arquivo vira a URL; use minúsculas, sem acento, com hífen'
        for k in ('titulo', 'categoria', 'capa', 'capa_alt', 'resumo'):
            assert meta.get(k), f'{fn}: falta "{k}"'
        assert os.path.exists(os.path.join(here, 'assets', 'blog', meta['capa'])), f'{fn}: capa não encontrada em assets/blog/'
        data = None
        if st == 'publicado':
            assert meta.get('data'), f'{fn}: artigo publicado precisa de data (AAAA-MM-DD)'
            data = datetime.date.fromisoformat(meta['data'])
        texto = re.sub(r'\]\([^)]*\)', ']', body)          # tira o endereço dos links
        texto = re.sub(r'[#*_>`\[\]()|-]', ' ', texto)
        palavras = len(texto.split())
        posts.append(dict(ordem=int(meta.get('ordem', 99)), slug=slug, status=st, titulo=meta['titulo'], categoria=meta['categoria'], capa=meta['capa'],
                          alt=meta['capa_alt'], resumo=meta['resumo'], autor=meta.get('autor', ''), data=data,
                          minutos=max(1, math.ceil(palavras / 200)),
                          html=_md.markdown(body, extensions=['extra', 'sane_lists'])))
    pub = sorted([p for p in posts if p['status'] == 'publicado'], key=lambda p: p['data'], reverse=True)
    ex = sorted([p for p in posts if p['status'] == 'exemplo'], key=lambda p: p['ordem'])
    return pub + ([] if web else ex)   # exemplos só na prévia

def leitura(p):
    return 'Exemplo de layout' if p['status'] == 'exemplo' else f'{p["minutos"]} min de leitura'

def post_card(L, A, p, heading='h3'):
    return (f'<li class="bl-card"><a href="{L("/blog/" + p["slug"] + "/")}">'
            f'<span class="bl-cover"><img src="{A("assets/blog/" + p["capa"])}" alt="{html.escape(p["alt"])}" width="960" height="600" loading="lazy" decoding="async"></span>'
            f'<span class="bl-body"><span class="bl-cat">{html.escape(p["categoria"])}</span>'
            f'<{heading} class="bl-t">{html.escape(p["titulo"])}</{heading}>'
            f'<span class="bl-time">{leitura(p)}</span></span></a></li>')

def blog_section(L, A, posts, ico):
    head = ('<div class="bl-head"><h2 id="bl-t" class="bl-h">Ideias para sua próxima fase.</h2>'
            '<p class="bl-sub">Conteúdo para criar, se conectar e crescer.</p>')
    if not posts:
        return ''  # sem artigo publicado, a seção não aparece (evita cara de site inacabado)
    vis = posts[:6]
    cards = ''.join(post_card(L, A, p) for p in vis)
    n = len(vis)
    dots = ''.join(f'<button type="button" class="bl-dot" data-i="{i}" aria-label="Ir para o artigo {i + 1} de {n}"'
                   f'{" aria-current=" + chr(34) + "true" + chr(34) if i == 0 else ""}></button>' for i in range(n))
    chev_r, chev_l = 'm9 6 6 6-6 6', 'm15 6-6 6 6 6'
    return (f'<section class="bl" aria-labelledby="bl-t" data-rail>{head}'
            f'<a class="bl-more" href="{L("/blog/")}">Explorar o blog {ico(chev_r, 18)}</a></div>'
            f'<ol class="bl-track" aria-label="Artigos recentes do blog" tabindex="0">{cards}</ol>'
            f'<div class="bl-ctrl"><div class="bl-arrows">'
            f'<button type="button" class="bl-arrow" data-rail-prev aria-label="Artigos anteriores">{ico(chev_l, 20)}</button>'
            f'<button type="button" class="bl-arrow" data-rail-next aria-label="Próximos artigos">{ico(chev_r, 20)}</button></div>'
            f'<div class="bl-dots">{dots}</div></div></section>')

def p_blog(posts):
    def f(L, A):
        cards = ''.join(post_card(L, A, p, 'h2') for p in posts)
        return ('<section class="page-hero" aria-labelledby="blog-h"><h1 id="blog-h" class="display" style="font-size:clamp(38px,5.4vw,60px)">Blog do HypeApp</h1>'
                '<p class="lead">Conteúdo para criar, se conectar e crescer: carreira de creator, parcerias, conteúdo e marketing de influência.</p></section>'
                f'<ol class="bl-grid" aria-label="Artigos do blog">{cards}</ol>')
    return f

def p_post(p):
    def f(L, A):
        ex = p['status'] == 'exemplo'
        meta = [] if ex else [f'{p["data"].day} de {MESES[p["data"].month - 1]} de {p["data"].year}', f'{p["minutos"]} min de leitura']
        if p['autor'] and not ex:
            meta.insert(0, 'Por ' + html.escape(p['autor']))
        aviso = ('<p class="bl-ex" role="note">Exemplo de layout na prévia. Este artigo não existe e não vai para o site publicado.</p>' if ex else '')
        meta_html = ('<p class="post-meta">' + ' · '.join(meta) + '</p>') if meta else ''
        return (f'<article class="post">'
                f'<nav class="post-crumbs" aria-label="Caminho"><a href="{L("/")}">Início</a><span aria-hidden="true">/</span><a href="{L("/blog/")}">Blog</a></nav>'
                f'<header class="post-head"><span class="bl-cat">{html.escape(p["categoria"])}</span><h1 class="post-h">{html.escape(p["titulo"])}</h1>'
                f'<p class="lead">{html.escape(p["resumo"])}</p>{aviso}{meta_html}</header>'
                f'<figure class="post-cover"><img src="{A("assets/blog/" + p["capa"])}" alt="{html.escape(p["alt"])}" width="960" height="600" decoding="async"></figure>'
                f'<div class="prose card post-body">{p["html"]}</div>'
                f'<div class="post-foot"><a class="btn btn-grey" href="{L("/blog/")}">Ver todos os artigos</a><a class="btn btn-cta" href="{L("/baixar/")}">Baixar o app</a></div>'
                f'</article>')
    return f

def post_meta(posts, base):
    out = {}
    for p in posts:
        u = '/blog/' + p['slug'] + '/'
        ld = {'@context': 'https://schema.org', '@type': 'Article', 'headline': p['titulo'], 'image': base + '/assets/blog/' + p['capa'],
              'inLanguage': 'pt-BR', 'publisher': {'@type': 'Organization', 'name': 'HypeApp'}}
        if p['data']:
            ld['datePublished'] = p['data'].isoformat()
        if p['autor']:
            ld['author'] = {'@type': 'Person', 'name': p['autor']}
        out[u] = dict(title=p['titulo'] + ' | Blog HypeApp', desc=p['resumo'],
                      robots='noindex, follow' if p['status'] == 'exemplo' else 'index, follow',
                      img='og/blog/' + p['slug'] + '.jpg', pagina=p['titulo'], ld=ld)  # 1200×630 gerada por make_media.py com a capa e o título
    return out
