# -*- coding: utf-8 -*-
"""Blog do HypeApp: lê content/blog/*.md (ver content/blog/LEIA-ME.md) e gera os trechos de HTML.
Usado por build.py. Nada aqui inventa data, autor ou tempo de leitura: tudo vem do arquivo do artigo."""
import os, re, math, datetime, html
import markdown as _md

MESES = ['janeiro', 'fevereiro', 'março', 'abril', 'maio', 'junho', 'julho', 'agosto', 'setembro', 'outubro', 'novembro', 'dezembro']

EQUIPE = {}   # content/blog/equipe.json: quem escreve e participa no blog (foto em assets/blog/autores/)
SO_TESTE = ' data-so-teste hidden'   # some no domínio oficial; o site.js mostra só em teste.hypeapp.com.br
WEB = False

def load_posts(here, web):
    global WEB, EQUIPE
    WEB = web
    pasta = os.path.join(here, 'content', 'blog')
    import json
    EQUIPE = json.load(open(os.path.join(pasta, 'equipe.json'), encoding='utf-8'))
    for k, v in EQUIPE.items():
        assert not v['foto'] or os.path.exists(os.path.join(here, 'assets', 'blog', v['foto'])), f'equipe.json: foto de {k} não encontrada'
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
        # participações da equipe no fim do artigo:  :::comentario lucas-ragnoni 2026-11-05  (texto)  :::
        coms = []
        def _com(mm):
            assert mm.group(1) in EQUIPE, f'{fn}: comentário de "{mm.group(1)}", que não está em equipe.json'
            coms.append(dict(autor=mm.group(1), data=datetime.date.fromisoformat(mm.group(2)), html=_md.markdown(mm.group(3).strip())))
            return ''
        body = re.sub(r'^:::comentario\s+([a-z0-9-]+)\s+(\d{4}-\d{2}-\d{2})\s*\n(.*?)\n:::\s*$', _com, body, flags=re.S | re.M).strip()
        autor = meta.get('autor', '') or 'equipe-hypeapp'
        assert autor in EQUIPE, f'{fn}: autor "{autor}" não está em content/blog/equipe.json'
        st = meta.get('status', 'rascunho')
        if st not in ('publicado', 'exemplo', 'revisao'):
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
        posts.append(dict(ordem=int(meta.get('ordem', 99)), slug=slug, status=st, titulo=meta['titulo'], titulo_seo=meta.get('titulo_seo', ''), categoria=meta['categoria'], capa=meta['capa'],
                          alt=meta['capa_alt'], resumo=meta['resumo'], autor=autor, comentarios=coms, data=data, destaque=meta.get('destaque', '') == 'sim',
                          minutos=max(1, math.ceil(palavras / 200)),
                          html=_md.markdown(body, extensions=['extra', 'sane_lists'])))
    pub = sorted([p for p in posts if p['status'] == 'publicado'], key=lambda p: p['data'], reverse=True)
    rev = sorted([p for p in posts if p['status'] == 'revisao'], key=lambda p: p['ordem'])
    ex = sorted([p for p in posts if p['status'] == 'exemplo'], key=lambda p: p['ordem'])
    # prévia: em revisão (e exemplos só enquanto não houver artigo de verdade).
    # --web: publicados e em revisão; os em revisão só aparecem no ambiente de teste (data-so-teste + redirecionamento no www)
    return pub + (rev if web else (rev + (ex if not (pub or rev) else [])))

def so_teste(p):
    return WEB and p['status'] == 'revisao'

def leitura(p):
    if p['status'] == 'exemplo':
        return 'Exemplo de layout'
    return f'{p["minutos"]} min de leitura' + (' · em revisão' if p['status'] == 'revisao' else '')

def data_txt(d, curta=False):
    if not d:
        return ''
    return f'{d.day:02d}/{d.month:02d}/{d.year}' if curta else f'{d.day} de {MESES[d.month - 1]} de {d.year}'

def tema_slug(cat):
    import unicodedata
    t = unicodedata.normalize('NFD', cat.lower())
    return re.sub(r'[^a-z0-9]+', '-', ''.join(c for c in t if unicodedata.category(c) != 'Mn')).strip('-')

def avatar(A, chave, tam=32):
    """Foto de quem escreve (ou o símbolo do HypeApp para a Equipe HypeApp)."""
    a = EQUIPE[chave]
    if a['foto']:
        return f'<img class="au-av" src="{A("assets/blog/" + a["foto"])}" alt="" width="{tam}" height="{tam}" loading="lazy" decoding="async" style="width:{tam}px;height:{tam}px">'
    return f'<span class="au-av au-av-hh" style="width:{tam}px;height:{tam}px" aria-hidden="true"><img src="{A("assets/logo-hypeapp-branco.svg")}" alt="" width="{tam}" height="{tam}"></span>'

def autor_linha(A, chave, quando='', tam=32, cls=''):
    """Linha de autoria: foto, nome, selo de Moderação e data (como nas comunidades com equipe identificada)."""
    a = EQUIPE[chave]
    selo = f'<span class="au-selo">{html.escape(a["selo"])}</span>' if a.get('selo') else ''
    q = f'<span class="au-q">{quando}</span>' if quando else ''
    return f'<span class="au {cls}">{avatar(A, chave, tam)}<span class="au-tx"><span class="au-n">{html.escape(a["nome"])}{selo}</span>{q}</span></span>'

def quando(p):
    if p['status'] == 'publicado' and p['data']:
        return f'{data_txt(p["data"], True)} · {p["minutos"]} min'
    return leitura(p)

def post_card(L, A, p, heading='h3', cls=''):
    return (f'<li class="bl-card {cls}" data-tema="{tema_slug(p["categoria"])}"{SO_TESTE if so_teste(p) else ""}><a href="{L("/blog/" + p["slug"] + "/")}">'
            f'<span class="bl-cover"><img src="{A("assets/blog/" + p["capa"])}" alt="{html.escape(p["alt"])}" width="960" height="600" loading="lazy" decoding="async"></span>'
            f'<span class="bl-body"><span class="bl-cat">{html.escape(p["categoria"])}</span>'
            f'<{heading} class="bl-t">{html.escape(p["titulo"])}</{heading}>'
            f'{autor_linha(A, p["autor"], quando(p), 28, "bl-au")}</span></a></li>')

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
    so = SO_TESTE if all(so_teste(p) for p in vis) else ''
    return (f'<section class="bl" aria-labelledby="bl-t" data-rail{so}>{head}'
            f'<a class="bl-more" href="{L("/blog/")}">Explorar o blog {ico(chev_r, 18)}</a></div>'
            f'<ol class="bl-track" aria-label="Artigos recentes do blog" tabindex="0">{cards}</ol>'
            f'<div class="bl-ctrl"><div class="bl-arrows">'
            f'<button type="button" class="bl-arrow" data-rail-prev aria-label="Artigos anteriores">{ico(chev_l, 20)}</button>'
            f'<button type="button" class="bl-arrow" data-rail-next aria-label="Próximos artigos">{ico(chev_r, 20)}</button></div>'
            f'<div class="bl-dots">{dots}</div></div></section>')

def p_blog(posts):
    """Página do blog (05/11), inspirada nas comunidades com equipe identificada: capa com o artigo principal, menu lateral
    com os tópicos e a equipe, destaques e todos os artigos com foto, nome, data e selo de quem escreveu.
    Os tópicos filtram a lista na própria página (#tema); sem JavaScript, aparecem todos os artigos."""
    def f(L, A):
        if not posts:
            return '<section class="page-hero"><h1 class="display">Blog do HypeApp</h1><p class="lead">Novos conteúdos em breve.</p></section>'
        dest = [p for p in posts if p.get('destaque')] or posts[:1]
        capa = dest[0]
        outros = [p for p in posts if p is not capa][:3]
        temas = {}
        for p in posts:
            temas.setdefault(p['categoria'], []).append(p)
        so_t = lambda ps: SO_TESTE if ps and all(so_teste(x) for x in ps) else ''
        menu = ''.join(f'<li><a class="bh-tema" href="#{tema_slug(c)}" data-tema="{tema_slug(c)}"{so_t(ps)}>{html.escape(c)}<span>{sum(1 for x in ps if not so_teste(x)) or len(ps)}</span></a></li>'
                       for c, ps in sorted(temas.items()))
        equipe = ''.join(f'<li>{autor_linha(A, k, "", 36)}</li>' for k in EQUIPE if k != 'equipe-hypeapp')
        cap_so = SO_TESTE if so_teste(capa) else ''
        destaques = ''.join(post_card(L, A, p, 'h3', 'bl-card-h') for p in outros)
        todos = ''.join(post_card(L, A, p, 'h3') for p in posts)
        return f'''<section class="bh-capa" aria-labelledby="blog-h">
  <div class="bh-capa-tx">
    <span class="bh-eye">Blog do HypeApp</span>
    <h1 id="blog-h" class="bh-h1">Ideias para a sua próxima fase.</h1>
    <p class="bh-lead">Carreira de creator, parcerias com marcas, conteúdo e marketing de influência, escritos por quem faz o HypeApp.</p>
  </div>
  <a class="bh-capa-post" href="{L("/blog/" + capa["slug"] + "/")}"{cap_so}>
    <span class="bh-capa-img"><img src="{A("assets/blog/" + capa["capa"])}" alt="{html.escape(capa["alt"])}" width="960" height="600" decoding="async" fetchpriority="high"></span>
    <span class="bh-capa-body"><span class="bl-cat">Em destaque · {html.escape(capa["categoria"])}</span><b class="bh-capa-t">{html.escape(capa["titulo"])}</b>
      <span class="bh-capa-r">{html.escape(capa["resumo"])}</span>{autor_linha(A, capa["autor"], quando(capa), 32, "bl-au")}</span>
  </a>
</section>
<div class="bh-g" data-bh>
  <aside class="bh-side" aria-label="Navegação do blog">
    <nav aria-labelledby="bh-temas-h"><span id="bh-temas-h" class="bh-side-h">Tópicos</span>
      <ul class="bh-temas"><li><a class="bh-tema" href="#todos" data-tema="todos" aria-current="true">Todos os artigos<span>{sum(1 for x in posts if not so_teste(x)) or len(posts)}</span></a></li>{menu}</ul></nav>
    <div class="bh-eq"><span class="bh-side-h">Quem escreve</span><ul class="bh-eq-l">{equipe}</ul>
      <p class="bh-eq-p">Artigos e respostas da equipe aparecem com o selo de Moderação.</p></div>
    <a class="bh-side-cta" href="{L("/baixar/")}"><b>Faça parte da comunidade</b><span>Grupos, feed e lives com outros creators, no app.</span></a>
  </aside>
  <div class="bh-main">
    {f'<section aria-labelledby="bh-dest-h"{so_t(outros)}><h2 id="bh-dest-h" class="bh-h2">Em destaque</h2><ol class="bh-dest">{destaques}</ol></section>' if outros else ''}
    <section aria-labelledby="bh-todos-h"><h2 id="bh-todos-h" class="bh-h2" data-bh-titulo>Todos os artigos</h2>
      <ol class="bl-grid bh-todos" aria-label="Artigos do blog">{todos}</ol>
      <p class="bh-vazio" data-bh-vazio hidden>Ainda não há artigos neste tópico.</p></section>
  </div>
</div>'''
    return f

def p_post(p):
    def f(L, A):
        ex, rv = p['status'] == 'exemplo', p['status'] == 'revisao'
        aviso = ('<p class="bl-ex" role="note">Exemplo de layout na prévia. Este artigo não existe e não vai para o site publicado.</p>' if ex else
                 ('<p class="bl-ex" role="note">Em revisão: este artigo aparece só no ambiente de teste e ainda não foi aprovado para o site.</p>' if WEB else
                  '<p class="bl-ex" role="note">Em revisão: este artigo aparece só na prévia. Para publicar, troque o status para publicado e preencha a data.</p>') if rv else '')
        q = ' · '.join(x for x in [data_txt(p['data']) if p['data'] else '', f'{p["minutos"]} min de leitura'] if x)
        coms = ''.join(f'<li class="pc-com">{autor_linha(A, c["autor"], data_txt(c["data"]), 36)}<div class="pc-com-tx">{c["html"]}</div></li>' for c in p['comentarios'])
        coms_html = (f'<section class="pc-coms" aria-labelledby="pc-coms-h"><h2 id="pc-coms-h" class="bh-h2">Da equipe HypeApp</h2><ol>{coms}</ol></section>') if coms else ''
        return (f'<article class="post">'
                f'<nav class="post-crumbs" aria-label="Caminho"><a href="{L("/")}">Início</a><span aria-hidden="true">/</span><a href="{L("/blog/")}">Blog</a>'
                f'<span aria-hidden="true">/</span><a href="{L("/blog/", "#" + tema_slug(p["categoria"]))}">{html.escape(p["categoria"])}</a></nav>'
                f'<header class="post-head"><span class="bl-cat">{html.escape(p["categoria"])}</span><h1 class="post-h">{html.escape(p["titulo"])}</h1>'
                f'<p class="lead">{html.escape(p["resumo"])}</p>{aviso}'
                f'{"" if ex else autor_linha(A, p["autor"], q, 44, "post-au")}</header>'
                f'<figure class="post-cover"><img src="{A("assets/blog/" + p["capa"])}" alt="{html.escape(p["alt"])}" width="960" height="600" decoding="async"></figure>'
                f'<div class="prose card post-body">{p["html"].replace('src="@blog/', 'src="' + A('assets/blog/'))}</div>'
                f'{coms_html}'
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
        a = EQUIPE[p['autor']]
        ld['author'] = {'@type': 'Organization' if p['autor'] == 'equipe-hypeapp' else 'Person', 'name': a['nome']}
        out[u] = dict(title=(p['titulo_seo'] or p['titulo']) + (' | Blog HypeApp' if len(p['titulo_seo'] or p['titulo']) <= 45 else ' | HypeApp'), desc=p['resumo'],
                      robots='index, follow' if p['status'] == 'publicado' else 'noindex, follow',
                      img='og/blog/' + p['slug'] + '.jpg', pagina=p['titulo'], ld=ld)  # 1200×630 gerada por make_media.py com a capa e o título
    return out
