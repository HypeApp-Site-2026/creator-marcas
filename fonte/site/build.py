# -*- coding: utf-8 -*-
"""Gera o site do HypeApp a partir das páginas abaixo e da matriz de SEO (seo/data.py).

Uso:
  python3 build.py            -> dist/       (prévia navegável: links para index.html, noindex, faixa de prévia)
  python3 build.py --web      -> dist-web/   (hospedagem real: URLs limpas /criadores/, sem faixa)
"""
import json, os, re, shutil, sys, html

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'seo'))
from data import R, BASE  # noqa: E402

WEB = '--web' in sys.argv
OUT = os.path.join(os.path.dirname(__file__), 'dist-web' if WEB else 'dist')
HERE = os.path.dirname(os.path.abspath(__file__))

# ---------- Configuração ----------
CFG = {
    'ios': 'https://apps.apple.com/br/app/hype-app-influenciadores/id6778357608',
    'android': 'https://play.google.com/store/apps/details?id=br.com.hypeapp.v2',
    'painel': 'https://www.hypeapp.com.br/backoffice/sign-up',   # backoffice das marcas (decisão de 30/10)
    'preview': not WEB,      # faixa "Prévia" + noindex
}
META = {r['url']: r for r in R}
PAINEL_URL = f"<span>{CFG['painel'].replace('https://', '').split('/sign-up')[0]}</span>" if CFG['painel'] else ''

# ---------- Utilidades ----------
def depth_of(url):
    return 0 if url == '/' else url.strip('/').count('/') + 1

def make_link(cur):
    pre = '../' * depth_of(cur)
    def L(path, hash=''):
        if path.startswith('http'):
            return path
        if WEB:
            return path + hash
        if path == '/':
            return pre + 'index.html' + hash
        return pre + path.strip('/') + '/index.html' + hash
    def A(path):
        return ('/' if WEB else pre) + path
    return L, A

PH = re.compile(r'\[([^\[\]<>"\n]{2,90})\]')
def mark_ph(s):
    return PH.sub(lambda m: '<span class="ph">[' + m.group(1) + ']</span>', s)

def ico(d, size=18, sw=2, fill=False):
    if fill:
        return f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="{d}"></path></svg>'
    return f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="{d}"></path></svg>'

I_ARROW = 'M5 12h14M13 6l6 6-6 6'
I_DOWN = 'm6 9 6 6 6-6'
I_PHONE = 'M8 2h8a2 2 0 0 1 2 2v16a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2zM11 18h2'
I_CASE = 'M3 9a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2zM8 7V5a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2'
I_PLUS = 'M12 5v14M5 12h14'
I_PLAY = 'M5 3l14 9-14 9V3z'
I_MENU = 'M4 7h16M4 12h16M4 17h16'
I_X = 'M6 6l12 12M18 6 6 18'
I_SEARCH = 'M11 18a7 7 0 1 0 0-14 7 7 0 0 0 0 14zM20 20l-3.5-3.5'


SOCIAL = [
    ('Instagram', 'https://www.instagram.com/hypeappbrasil/', '0 0 30 24', '<path d="M9.75195 0C5.89295 0 2.75391 3.14195 2.75391 7.00195V17.002C2.75391 20.861 5.89586 24 9.75586 24H19.7559C23.6149 24 26.7539 20.858 26.7539 16.998V6.99805C26.7539 3.13905 23.612 0 19.752 0H9.75195ZM21.7539 4C22.3059 4 22.7539 4.448 22.7539 5C22.7539 5.552 22.3059 6 21.7539 6C21.2019 6 20.7539 5.552 20.7539 5C20.7539 4.448 21.2019 4 21.7539 4ZM14.7539 6C18.0629 6 20.7539 8.691 20.7539 12C20.7539 15.309 18.0629 18 14.7539 18C11.4449 18 8.75391 15.309 8.75391 12C8.75391 8.691 11.4449 6 14.7539 6ZM14.7539 8C13.693 8 12.6756 8.42143 11.9255 9.17157C11.1753 9.92172 10.7539 10.9391 10.7539 12C10.7539 13.0609 11.1753 14.0783 11.9255 14.8284C12.6756 15.5786 13.693 16 14.7539 16C15.8148 16 16.8322 15.5786 17.5823 14.8284C18.3325 14.0783 18.7539 13.0609 18.7539 12C18.7539 10.9391 18.3325 9.92172 17.5823 9.17157C16.8322 8.42143 15.8148 8 14.7539 8Z" fill="currentColor"/>'),
    ('YouTube', 'https://www.youtube.com/@hypeappbrasil', '0 0 30 24', '<path d="M14.9345 0C10.3683 0 4.44179 1.14407 4.44179 1.14407L4.42688 1.16112C2.34722 1.49372 0.753906 3.28075 0.753906 5.45406V18.5438C0.755936 19.5839 1.12791 20.5871 1.80305 21.3755C2.47818 22.1639 3.41225 22.6857 4.43753 22.8474L4.44179 22.8538C4.44179 22.8538 10.3683 24 14.9345 24C19.5006 24 25.4271 22.8538 25.4271 22.8538L25.4293 22.8517C26.4557 22.6903 27.3908 22.168 28.0665 21.3787C28.7421 20.5894 29.1139 19.5849 29.115 18.5459V5.45406C29.1135 4.41575 28.7418 3.41201 28.0666 2.62319C27.3914 1.83438 26.457 1.31219 25.4314 1.15047L25.4271 1.14407C25.4271 1.14407 19.5006 0 14.9345 0ZM11.662 6.97949L20.3885 11.9989L11.662 17.0184V6.97949Z" fill="currentColor"/>'),
    ('LinkedIn', 'https://www.linkedin.com/company/hypeappbrasil/', '0 0 24 24', '<path d="M4.98298 7.1968C6.19138 7.1968 7.17098 6.2172 7.17098 5.0088C7.17098 3.8004 6.19138 2.8208 4.98298 2.8208C3.77458 2.8208 2.79498 3.8004 2.79498 5.0088C2.79498 6.2172 3.77458 7.1968 4.98298 7.1968Z" fill="currentColor"/><path d="M9.2377 8.85518V20.9942H13.0067V14.9912C13.0067 13.4072 13.3047 11.8732 15.2687 11.8732C17.2057 11.8732 17.2297 13.6842 17.2297 15.0912V20.9952H21.0007V14.3382C21.0007 11.0682 20.2967 8.55518 16.4747 8.55518C14.6397 8.55518 13.4097 9.56218 12.9067 10.5152H12.8557V8.85518H9.2377ZM3.0957 8.85518H6.8707V20.9942H3.0957V8.85518Z" fill="currentColor"/>'),
]
I_APPLE = '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M9.07535 14.6985L14.676 4.58153C14.753 4.44221 14.83 4.30471 14.8997 4.1608C14.9629 4.03063 15.0161 3.89956 15.0509 3.75748C15.1242 3.45865 15.1041 3.147 14.9904 2.86192C14.88 2.58106 14.6803 2.34432 14.4221 2.18819C14.1687 2.03478 13.8706 1.97237 13.577 2.01128C13.2836 2.0507 13.0151 2.18911 12.8033 2.40544C12.7025 2.50627 12.62 2.62085 12.5439 2.74276C12.4596 2.87659 12.3835 3.01592 12.3065 3.15525L11.9527 3.79414L11.5979 3.15433C11.5209 3.01592 11.4449 2.87659 11.3605 2.74276C11.2863 2.62116 11.1993 2.50778 11.1011 2.40452C10.8945 2.19057 10.6221 2.05211 10.3275 2.01128C10.0341 1.97259 9.73637 2.03498 9.48325 2.18819C9.22501 2.34432 9.02531 2.58106 8.91494 2.86192C8.80167 3.14678 8.78051 3.45997 8.85444 3.75748C8.88927 3.89956 8.94244 4.03063 9.00477 4.1608C9.07443 4.30471 9.15143 4.44221 9.22843 4.58153L10.3724 6.64764L5.9157 14.6976H2.86146C2.70746 14.6976 2.55347 14.6976 2.40039 14.7067C2.26106 14.715 2.1254 14.7324 1.98974 14.7718C1.70558 14.8543 1.45625 15.0285 1.27659 15.2741C1.09698 15.5213 1.00016 15.819 1 16.1246C0.999836 16.4302 1.09633 16.728 1.27567 16.9754C1.45625 17.2211 1.70466 17.3943 1.98974 17.4777C2.1254 17.5171 2.26106 17.5345 2.40039 17.5428C2.55347 17.552 2.70746 17.552 2.86146 17.552H14.8667C14.9031 17.4718 14.9338 17.3891 14.9583 17.3045C15.3387 16.0065 14.3937 14.6976 13.093 14.6976L9.07535 14.6985ZM3.85418 18.0185L3.1282 19.3935C3.05304 19.5365 2.97695 19.6776 2.90912 19.8252C2.84653 19.9581 2.7974 20.0969 2.76246 20.2395C2.68891 20.5449 2.70936 20.8654 2.82113 21.1589C2.93204 21.4504 3.12728 21.6933 3.37753 21.851C3.62777 22.0087 3.91742 22.0728 4.20342 22.0316C4.49124 21.9912 4.7534 21.8501 4.96056 21.6283C5.05956 21.5228 5.14022 21.4064 5.21538 21.2818C5.29788 21.1443 5.37213 21.0013 5.44729 20.8583L6.50051 18.8637C6.41801 18.7262 5.63245 17.5162 3.85418 18.0185ZM22.7241 15.2631C22.5473 15.0238 22.2962 14.8498 22.01 14.7681C21.8761 14.7309 21.7383 14.7091 21.5994 14.7031C21.4454 14.6939 21.2923 14.6939 21.1383 14.6939H18.0942L14.0701 7.53036C13.5419 8.08452 13.1975 8.78808 13.0838 9.54513C12.9361 10.492 13.1124 11.461 13.5843 12.295L18.4186 20.905C18.4956 21.0425 18.5717 21.18 18.656 21.312C18.733 21.4312 18.8155 21.5439 18.9155 21.6457C19.1272 21.8583 19.3958 21.994 19.69 22.0334C19.9843 22.0728 20.2794 22.0114 20.5352 21.8592C20.7924 21.7054 20.9922 21.4717 21.1044 21.1938C21.219 20.9124 21.2382 20.6053 21.1649 20.3101C21.1286 20.1726 21.0779 20.0392 21.0136 19.9123C20.9449 19.7702 20.867 19.6346 20.79 19.4971L19.6754 17.5116H21.1383C21.2923 17.5116 21.4454 17.5116 21.5994 17.5034C21.7387 17.4951 21.8744 17.4777 22.01 17.4392C22.2966 17.3575 22.5481 17.1831 22.725 16.9433C22.9042 16.7001 23.0005 16.4058 23 16.1037C23.0005 15.8016 22.9042 15.5073 22.725 15.264" fill="currentColor"/></svg>'
I_GPLAY = '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M3.28967 3.93383L12.0297 12.5048L3.35467 21.1548C3.21274 20.97 3.10257 20.7628 3.02867 20.5418C2.99044 20.2916 2.99044 20.0371 3.02867 19.7868V5.06683C3.00267 4.67183 3.09367 4.27683 3.28867 3.93383M15.7947 8.76683L12.9417 11.5928L4.30567 3.09983C4.58567 3.00283 4.88567 2.97583 5.17867 3.02183C5.63867 3.14783 6.07767 3.34183 6.48067 3.59483L14.2967 7.91983C14.8047 8.19283 15.2997 8.47983 15.7947 8.76683ZM12.9427 13.4298L15.7817 16.2178L13.7237 17.3638L7.44467 20.8538C6.92467 21.1408 6.40267 21.4148 5.89467 21.7278C5.67729 21.8632 5.43355 21.9506 5.17971 21.9842C4.92587 22.0178 4.66778 21.9969 4.42267 21.9228L12.9427 13.4298ZM20.3027 12.5048C20.31 12.8545 20.2216 13.1995 20.0471 13.5027C19.8727 13.8058 19.6187 14.0555 19.3127 14.2248L16.9667 15.5268L13.8797 12.5048L16.9797 9.43083C17.7747 9.87383 18.5567 10.3168 19.3377 10.7338C19.6491 10.9079 19.905 11.1666 20.0756 11.48C20.2462 11.7934 20.3256 12.1487 20.3027 12.5048Z" fill="currentColor"/></svg>'

def social_links(cls='social'):
    return f'<ul class="{cls}" aria-label="Redes sociais do HypeApp">' + ''.join(
        f'<li><a href="{u}" target="_blank" rel="noopener me" aria-label="HypeApp no {n}"><svg width="{26 if vb.startswith("0 0 30") else 22}" height="22" viewBox="{vb}" fill="none" aria-hidden="true">{d}</svg></a></li>' for n, u, vb, d in SOCIAL) + '</ul>'

def stores(L, small=False):
    return (f'<a class="store" href="{CFG["ios"]}" target="_blank" rel="noopener">{I_APPLE}<span><small>Baixar na</small>App Store</span></a>'
            f'<a class="store" href="{CFG["android"]}" target="_blank" rel="noopener">{I_GPLAY}<span><small>Disponível no</small>Google Play</span></a>')

def qr_svg():
    import qrcode, qrcode.image.svg
    img = qrcode.make(BASE + '/app', image_factory=qrcode.image.svg.SvgPathImage, box_size=10, border=0)
    s = img.to_string(encoding='unicode')
    s = re.sub(r'<\?xml[^>]*\?>', '', s)
    s = s.replace('<svg ', '<svg role="img" aria-label="QR code para hypeapp.com.br/app" ', 1)
    s = re.sub(r'width="[^"]*mm" height="[^"]*mm" ', '', s)
    return s.replace('fill="#000000"', 'fill="#050505"')
QR = qr_svg()

def faq_html(items):
    out = []
    for q, a in items:
        out.append(f'<details><summary>{q}<span class="plus">{ico(I_PLUS, 14)}</span></summary><p>{a}</p></details>')
    return ''.join(out)

# ---------- Logo e vitrines de telas ----------
def logo(A, h):
    w = round(h * 746.32 / 407.89)
    return f'<img class="logo-img" src="{A("assets/logo-hypeapp.svg")}" alt="HypeApp" width="{w}" height="{h}">'

def tela(A, code):
    return A(f'assets/telas/{code}.webp')

# Cursor tour nas vitrines do painel: onde o cursor clica em cada captura (% da largura, % da altura)
CURSOR_HOT = {
    'bo-C1': (46.4, 67.8), 'bo-C2': (28.6, 52.5), 'bo-C3': (55, 45), 'bo-C4': (49.6, 53.4), 'bo-C5': (30, 55), 'bo-C6': (52.9, 68.3),
    'bo-D1': (29.3, 93.4), 'bo-D2': (30, 61.4), 'bo-D4': (66, 57), 'bo-D6': (65.4, 58.7),
    'bo-E1': (36, 62.6), 'bo-E2': (47.9, 92.9), 'bo-I3': (45.7, 92.9),
    'bo-F1': (79.7, 15), 'bo-G1': (27.1, 57.5), 'bo-G2': (86.9, 53.9),
    'bo-I1': (88.9, 83.3), 'bo-B3': (61.1, 84), 'bo-B5': (45.7, 52.3),
}
CURSOR_SVG = ('<svg viewBox="0 0 24 24" width="26" height="26" aria-hidden="true"><path d="M5 3l14 8.2-6.1 1.4-2.9 5.9z" '
              'fill="#050505" stroke="#fff" stroke-width="1.6" stroke-linejoin="round"/></svg>')

def showcase(A, sid, kind, tag, title, lead, items, flip=False, note='Dados de exemplo.'):
    """kind: 'phone' (app) ou 'web' (painel). items: [(codigo, titulo, descricao)]"""
    btns, imgs = '', ''
    for i, (code, t, d) in enumerate(items):
        on = i == 0
        btns += (f'<li><button type="button" class="sc-item" data-i="{i}" aria-pressed="{"true" if on else "false"}" aria-controls="{sid}-tela">'
                 f'<span class="sc-bar" aria-hidden="true"><i></i></span><b>{t}</b><span>{d}</span></button></li>')
        w, h = (600, 1298) if kind == 'phone' else (1400, 875)
        hp = CURSOR_HOT.get(code) if kind == 'web' else None
        imgs += (f'<img src="{tela(A, code)}" alt="Tela do {"app" if kind == "phone" else "painel"}: {t}" width="{w}" height="{h}" data-i="{i}"'
                 + (f' data-hot="{hp[0]},{hp[1]}"' if hp else '') + ''
                 f'{" class=\"on\"" if on else ""} loading="{"eager" if on else "lazy"}" decoding="async">')
    if kind == 'phone':
        dev = f'<div class="dev-phone"><div class="dev-screen" id="{sid}-tela" aria-live="polite">{imgs}</div></div>'
    else:
        dev = (f'<div class="dev-web"><div class="dev-bar"><i></i><i></i><i></i>{PAINEL_URL}</div>'
               f'<div class="dev-screen" id="{sid}-tela" aria-live="polite">{imgs}'
               + (f'<span class="tour" aria-hidden="true">{CURSOR_SVG}<i></i></span>' if 'data-hot=' in imgs else '') + '</div></div>')
    return f'''<section class="sc sc-{kind}{" flip" if flip else ""}" id="{sid}" data-show aria-labelledby="{sid}-t">
  <div class="sc-head stack" style="gap:14px"><span class="tag{" ink" if kind == "web" else ""}">{tag}</span><h2 class="h2" id="{sid}-t">{title}</h2><p class="body">{lead}</p></div>
  <ul class="sc-list" aria-label="Telas de {tag.lower()}">{btns}</ul>
  <figure class="sc-dev">{dev}<figcaption class="small muted">{note}</figcaption></figure>
</section>'''

# ---------- Cabeçalho e rodapé ----------
def header(cur, L, A):
    nav = [('/criadores/', 'Para creators'), ('/marcas/', 'Para marcas'), ('/perguntas-frequentes/', 'Ajuda')]
    MEGA = {
        '/criadores/': ('Para creators', 'app-D1', [
            ('Como funciona', 'Do convite ao pagamento, passo a passo', L('/criadores/', '#como-funciona')),
            ('Funcionalidades do app', 'Campanhas, entregas, comunidade e carteira', L('/criadores/', '#recursos')),
            ('Baixar o app', 'App Store e Google Play', L('/baixar/')),
            ('Dúvidas de creators', 'Pagamento, nota fiscal e regras', L('/perguntas-frequentes/', '#creators'))]),
        '/marcas/': ('Para marcas e agências', 'monitor', [
            ('Funcionalidades do painel', 'Criar, acompanhar e pagar campanhas', L('/marcas/', '#funcionalidades')),
            ('Formas de trabalhar', 'Self-service ou gerenciada', L('/marcas/', '#modalidades')),
            ('Para agências', 'Várias marcas em um painel', L('/marcas/', '#agencias')),
            ('Falar com nosso time', 'Valores sob consulta', L('/contato/marcas/'))]),
        '/perguntas-frequentes/': ('Ajuda', None, [
            ('Perguntas frequentes', 'Respostas rápidas sobre o app e o painel', L('/perguntas-frequentes/')),
            ('Suporte', 'Abra um chamado de seg. a sex.', L('/suporte/')),
            ('Exclusão de conta', 'Como excluir sua conta e seus dados', L('/exclusao-de-conta/')),
            ('Contato', 'Comercial, parcerias e privacidade', L('/contato/'))]),
    }
    links, panels = '', ''
    for i, (p, t) in enumerate(nav):
        label, img, items = MEGA[p]
        pid = f'mega-{i}'
        cur_attr = ' aria-current="page"' if cur == p else ''
        links += (f'<a href="{L(p)}" class="nav-trigger" data-mega="{pid}" aria-haspopup="true" aria-expanded="false" aria-controls="{pid}"{cur_attr}>'
                  f'{t}{ico(I_DOWN, 14)}</a>')
        lis = ''.join(f'<li><a href="{h}"><b>{n}</b><span>{d}</span></a></li>' for n, d, h in items)
        art = (f'<img class="mega-art mega-monitor" src="{A("assets/menu/monitor-painel.webp")}" alt="" width="480" height="424" loading="lazy">' if img == 'monitor' else
               f'<img class="mega-art" src="{tela(A, img)}" alt="" width="{600 if img.startswith("app") else 1400}" height="{1298 if img.startswith("app") else 875}" loading="lazy">'
               if img else '<span class="mega-art mega-bubble" aria-hidden="true">?</span>')
        panels += (f'<div class="mega{" mega-web" if img and (img.startswith("bo") or img == "monitor") else ""}" id="{pid}" role="region" aria-label="{label}" hidden>'
                   f'<div class="mega-card"><span class="mega-label">{label}</span><ul>{lis}</ul></div>{art}</div>')
    painel = CFG['painel']
    marca_href = painel if painel else L('/entrar/', '#marcas')
    marca_sub = 'Painel das marcas · ' + painel.replace('https://www.', '').split('/sign-up')[0] if painel else 'Painel das marcas'
    menu = f'''
<div class="entrar-menu" id="entrar-menu" role="menu" aria-label="Entrar como" hidden>
  <a role="menuitem" class="entrar-item" href="{L('/entrar/', '#creators')}">
    <span class="entrar-ico">{ico(I_PHONE, 20)}</span>
    <span class="entrar-txt"><b>Sou creator</b><span>Abrir o app ou baixar na loja</span></span>
  </a>
  <a role="menuitem" class="entrar-item" href="{marca_href}">
    <span class="entrar-ico ink">{ico(I_CASE, 20)}</span>
    <span class="entrar-txt"><b>Sou marca ou agência</b><span>{marca_sub}</span></span>
  </a>
  <div class="entrar-sep"></div>
  <a role="menuitem" class="entrar-foot" href="{L('/baixar/')}">Ainda não tem o app? Baixar {ico(I_ARROW, 16)}</a>
</div>'''
    mmenu = f'''
<div class="mmenu" id="mmenu" hidden role="dialog" aria-modal="true" aria-label="Menu">
  <div class="mmenu-top">
    <a class="logo" href="{L('/')}" aria-label="HypeApp, página inicial">{logo(A, 36)}</a>
    <button type="button" class="menu-btn" id="mmenu-close" aria-label="Fechar menu" style="display:inline-flex">{ico(I_X, 20)}</button>
  </div>
  <nav aria-label="Menu do celular">
    <div class="mgroup"><a class="mhead" href="{L('/criadores/')}">Para creators {ico(I_ARROW, 18)}</a>
      <div class="msub"><a href="{L('/criadores/', '#como-funciona')}">Como funciona</a><a href="{L('/criadores/', '#recursos')}">Recursos do app</a><a href="{L('/baixar/')}">Baixar o app</a></div></div>
    <div class="mgroup"><a class="mhead" href="{L('/marcas/')}">Para marcas {ico(I_ARROW, 18)}</a>
      <div class="msub"><a href="{L('/marcas/', '#modalidades')}">Formas de trabalhar</a><a href="{L('/marcas/', '#agencias')}">Para agências</a><a href="{L('/contato/marcas/')}">Falar com nosso time</a></div></div>
    <a class="mlink" href="{L('/perguntas-frequentes/')}">Ajuda {ico('m9 6 6 6-6 6', 18)}</a>
    <a class="mlink" href="{L('/suporte/')}">Suporte {ico('m9 6 6 6-6 6', 18)}</a>
  </nav>
  <div class="mmenu-actions">
    <a class="btn btn-cta" href="{L('/baixar/')}">Baixar o app</a>
    <a class="btn btn-ghost" href="{L('/entrar/')}">Entrar</a>
  </div>
</div>'''
    return f'''<header class="site-header wrap">
  <div class="hdr">
    <a class="logo" href="{L('/')}" aria-label="HypeApp, página inicial">{logo(A, 40)}</a>
    <nav class="nav" aria-label="Principal">{links}</nav>
    <div class="hdr-actions">
      <button type="button" class="btn btn-ghost btn-entrar" id="btn-entrar" aria-expanded="false" aria-controls="entrar-menu">Entrar {ico(I_DOWN, 14)}</button>
      <a class="btn btn-cta hdr-cta" href="{L('/baixar/')}">Baixar o app</a>
      <button type="button" class="menu-btn" id="menu-btn" aria-label="Abrir menu" aria-expanded="false" aria-controls="mmenu">{ico(I_MENU, 20)}</button>
    </div>
  </div>
  {menu}
  {panels}
</header>
<div class="nav-scrim" id="nav-scrim" aria-hidden="true"></div>
{mmenu}'''

def footer(L, A):
    cols = [
        ('Para creators', [('Como funciona', L('/criadores/')), ('Baixar o app', L('/baixar/')), ('Entrar no app', L('/entrar/', '#creators'))]),
        ('Para marcas', [('Para marcas e agências', L('/marcas/')), ('Falar com nosso time', L('/contato/marcas/')), ('Entrar no painel', CFG['painel'] or L('/entrar/', '#marcas'))]),
        ('Ajuda', [('Perguntas frequentes', L('/perguntas-frequentes/')), ('Suporte', L('/suporte/'))]),
        ('Empresa', [('Sobre o HypeApp', L('/sobre/'))] + ([('Blog', L('/blog/'))] if BLOG_ON else []) + [('Contato', L('/contato/'))]),
        ('Legal', [('Privacidade', L('/privacidade/')), ('Encarregado de dados', L('/privacidade/', '#encarregado')), ('Termos de uso', L('/termos/')), ('Cookies', L('/cookies/')), ('Exclusão de conta', L('/exclusao-de-conta/'))]),
    ]
    c = ''.join(f'<nav aria-label="{t}"><span class="ftr-h">{t}</span>' + ''.join(f'<a href="{h}">{n}</a>' for n, h in ls) + '</nav>' for t, ls in cols)
    return f'''<footer class="site-footer wrap">
  <div class="ftr">
    <div class="between" style="align-items:center">
      <div class="stack" style="gap:10px;max-width:420px">
        <a class="logo" href="{L('/')}" aria-label="HypeApp, página inicial">{logo(A, 52)}</a>
        <p class="small muted" style="font-size:15px">Campanhas entre creators e marcas, do convite ao pagamento. Desenvolvido pela Você no Hype.</p>
      </div>
      <div class="row">{stores(L)}</div>
    </div>
    <div class="ftr-cols">{c}</div>
    <div class="ftr-legal">
      <span>© 2026 HypeApp · Você no Hype Marketing e Entretenimento LTDA · CNPJ 43.442.408/0001-26</span>
      {social_links()}
    </div>
  </div>
</footer>'''

# ---------- Peças do mockup do app ----------
def pc(kind):
    if kind == 'campanha':
        return ('<div class="pc pc-camp"><div class="cov"><span class="a">Novo</span><span class="b">Beleza</span>VG</div>'
                '<div class="bt"><span><b>Verão Glow</b><i>Inscrições abertas</i></span><span class="v">R$ 1.200</span></div></div>')
    if kind == 'etapas':
        st = [('Convite aceito', 'done'), ('Roteiro aprovado', 'done'), ('Enviar conteúdo', 'now'), ('Registrar publicação', '')]
        rows = ''.join(f'<span class="pc-step"><span class="m {c}">{"✓" if c == "done" else i + 1}</span>{t}</span>' for i, (t, c) in enumerate(st))
        return f'<div class="pc pc-steps">{rows}</div>'
    if kind == 'proximo':
        return ('<div class="pc pc-next"><span><i>Próximo passo</i><b>Enviar o conteúdo</b></span>'
                '<span style="display:flex;justify-content:space-between;align-items:center"><i>Prazo: 10/11</i><span class="go">Enviar</span></span></div>')
    rows = {
        'grupo1': ('', 'BE', 'Beleza e skincare', 'Grupo oficial', 'Entrar'),
        'live': ('dark', 'AO', 'Live: precificar Reels', 'Quinta, 19h', 'Agenda'),
        'grupo2': ('', 'UG', 'Creators de UGC', 'Grupo aberto', 'Entrar'),
        'saldo': ('dark', 'R$', 'Saldo disponível', 'R$ 3.250', 'Sacar'),
        'pag1': ('', 'SP', 'Skincare Pro', 'Pagamento liberado', '+ R$ 800'),
        'pag2': ('', 'VG', 'Verão Glow', 'A liberar', 'R$ 1.200'),
    }
    c, ini, n, d, v = rows[kind]
    return f'<div class="pc pc-row {c}"><span class="c">{ini}</span><span class="tx"><b>{n}</b><i>{d}</i></span><span class="p">{v}</span></div>'

def motion_criador(third='comunidade'):
    gk = ['saldo', 'pag1', 'pag2'] if third == 'carteira' else ['grupo1', 'live', 'grupo2']
    title3 = 'Carteira' if third == 'carteira' else 'Comunidade'
    # (chave, tipo, x, y, w, h) dentro da tela
    pieces = [('A', 'campanha', 14, 128, 244, 196), ('St', 'etapas', 14, 96, 244, 228), ('Nx', 'proximo', 14, 336, 244, 104),
              ('G1', gk[0], 14, 96, 244, 82), ('G2', gk[1], 14, 190, 244, 82), ('G3', gk[2], 14, 284, 244, 82), ('Nav', 'nav', 12, 510, 248, 58)]
    box = lambda k, kind, x, y, w, h: f'<div class="mc-abs" data-in="{k}" style="left:{x}px;top:{y}px;width:{w}px;height:{h}px">{"" if kind == "nav" else pc(kind)}</div>'
    P = {p[0]: p for p in pieces}
    X0, Y0 = 144, 73
    dets = ''.join(f'<div class="mc-det" data-det="{k}" style="left:{X0 + x}px;top:{Y0 + y}px;width:{w}px;height:{h}px">{"" if kind == "nav" else pc(kind)}</div>' for k, kind, x, y, w, h in pieces)
    lst = lambda ini, n, d, v, top: f'<div class="mc-abs mc-list" style="left:14px;top:{top}px;width:244px;height:72px"><span class="sq">{ini}</span><span class="tx"><b>{n}</b><i>{d}</i></span><span class="v">{v}</span></div>'
    return f'''<div class="mc-frame" data-terceiro="{third}">
  <div class="mc-stage">
    <div class="mc-scene" role="img" aria-label="Demonstração animada do app HypeApp: oportunidades, entregas e {title3.lower()}">
      <span class="mc-label">Demonstração</span>
      <span class="mc-chapter" style="opacity:0">Oportunidades</span>
      <div class="mc-cam">
        <div class="mc-phone"><div class="mc-screen">
          <div class="mc-pane" data-pane="home">
            <span class="mc-abs mc-title" style="left:16px;top:44px">Descobrir</span>
            <span class="mc-abs mc-chips" style="left:16px;top:86px"><span class="on">Todas</span><span>Beleza</span><span>Moda</span></span>
            {box(*P['A'])}
            {lst('SP', 'Skincare Pro', 'Convite · Casa Lume', 'R$ 800', 336)}
            {lst('MO', 'Brisa de Verão', 'Moda · TikTok', 'Permuta', 418)}
          </div>
          <div class="mc-pane" data-pane="camp" style="transform:translateX(272px)">
            <span class="mc-abs" style="left:16px;top:44px;display:flex;align-items:center;gap:10px"><span style="width:36px;height:36px;border-radius:50%;background:#fff;display:flex;align-items:center;justify-content:center">{ico('m15 6-6 6 6 6', 16)}</span><span style="display:flex;flex-direction:column"><b style="font-size:17px;font-weight:600">Skincare Pro</b><span style="font-size:12px">Campanha em andamento</span></span></span>
            {box(*P['St'])}{box(*P['Nx'])}
          </div>
          <div class="mc-pane" data-pane="third" style="transform:translateX(544px)">
            <span class="mc-abs mc-title" style="left:16px;top:44px">{title3}</span>
            {box(*P['G1'])}{box(*P['G2'])}{box(*P['G3'])}
          </div>
          {box(*P['Nav'])}
        </div></div>
        {dets}
      </div>
    </div>
    <button type="button" class="mc-pause" aria-label="Pausar animação">{ico('M7 5h4v14H7zM13 5h4v14h-4z', 14, fill=True)}</button>
  </div>
</div>'''

def motion_stack(L, third='comunidade'):
    camps = [('VG', 'Verão Glow', 'Beleza · Instagram', 'R$ 1.200'), ('SP', 'Skincare Pro', 'Convite · Casa Lume', 'R$ 800'), ('MO', 'Brisa de Verão', 'Moda · TikTok', 'Permuta')]
    d1 = ('<span class="mc-chips first"><span class="on">Todas</span><span>Beleza</span><span>Moda</span></span>' +
          ''.join(f'<span class="mini-row" style="padding:12px;border-radius:22px"><span class="ini ink" style="width:52px;height:52px">{a}</span><span style="display:flex;flex-direction:column;flex:1;min-width:0"><b style="font-size:16px;font-weight:600">{b}</b><span style="font-size:13px">{c}</span></span><b style="font-size:16px;font-weight:600">{d}</b></span>' for a, b, c, d in camps))
    st = [('Convite aceito', 'done'), ('Roteiro aprovado', 'done'), ('Enviar conteúdo', 'now'), ('Registrar publicação', '')]
    d2 = ('<span class="pc-steps first" style="padding:6px 16px">' + ''.join(f'<span class="pc-step" style="font-size:15px"><span class="m {c}" style="width:28px;height:28px">{"✓" if c == "done" else i + 1}</span>{t}</span>' for i, (t, c) in enumerate(st)) + '</span>'
          '<span class="pc-next" style="flex-direction:row;align-items:center"><span><i>Próximo passo</i><b>Enviar o conteúdo</b></span><span class="go" style="height:36px;font-size:13px">Enviar</span></span>')
    if third == 'carteira':
        rows3 = [('dark', 'R$', 'Saldo disponível', 'Pronto para sacar via PIX', 'R$ 3.250'), ('', 'SP', 'Skincare Pro', 'Pagamento liberado', '+ R$ 800'), ('', 'VG', 'Verão Glow', 'A liberar após a publicação', 'R$ 1.200')]
        c3 = ('Carteira', 'Receba pela carteira', 'Veja o que está a liberar e o que já pode sacar, com o extrato de cada campanha.', 'Como funciona o pagamento')
    else:
        rows3 = [('', 'BE', 'Beleza e skincare', '1.240 membros · grupo oficial', 'Entrar'), ('dark', 'AO', 'Live: como precificar Reels', 'Quinta, 19h · agenda', 'Ao vivo'), ('', 'UG', 'Creators de UGC', '860 membros', 'Entrar')]
        c3 = ('Comunidade', 'Conecte-se à comunidade', 'Feed, grupos e lives com outros creators, com regras claras de participação.', 'Ver dúvidas sobre a comunidade')
    d3 = ''.join(f'<span class="pc-row {c}{" first" if i == 0 else ""}" style="padding:14px"><span class="c">{a}</span><span class="tx"><b style="font-size:15px">{b}</b><i style="font-size:13px">{d}</i></span><b style="font-size:15px;font-weight:600">{v}</b></span>' for i, (c, a, b, d, v) in enumerate(rows3))
    data = [('Oportunidades', 'Explore oportunidades', 'Encontre campanhas do seu nicho, veja critérios, valor e prazo, e se inscreva nas que combinam com você.', 'Baixar o app', L('/baixar/'), d1),
            ('Entregas', 'Acompanhe suas entregas', 'Briefing, roteiro, conteúdo, ajustes e publicação, com o próximo passo sempre à vista.', 'Baixar o app', L('/baixar/'), d2),
            (c3[0], c3[1], c3[2], 'Baixar o app', L('/baixar/'), d3)]
    cards = ''
    for i, (tag, t, d, cta, href, demo) in enumerate(data):
        cards += f'''<div class="stk-card" style="z-index:{10 - i}"><div class="stk-in"><article class="stk-art">
  <div class="stk-txt"><span style="display:flex;justify-content:space-between;align-items:center"><span class="tag">{tag}</span><span class="stk-idx">{i + 1:02d} / 03</span></span>
  <h3>{t}</h3><p class="body">{d}</p><a class="btn btn-ink" href="{href}">{cta}</a></div>
  <div class="stk-demo" aria-hidden="true"><span class="lbl">Demonstração</span>{demo}</div>
</article></div></div>'''
    return f'''<section class="stk" id="como-funciona" aria-labelledby="stk-t">
  <div class="stk-head stack" style="gap:10px"><h2 class="h2" id="stk-t">Seu próximo passo no HypeApp</h2><p class="body" style="max-width:560px">Do convite ao pagamento, cada etapa fica no app.</p></div>
  <div class="stk-stage"><div class="stk-deck">{cards}</div></div>
</section>'''

def motion_painel():
    I = {'camp': 'M3 11v2a1 1 0 0 0 1 1h2l5 4V6L6 10H4a1 1 0 0 0-1 1zM15 9a4 4 0 0 1 0 6',
         'cre': 'M16 20v-1a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v1M9 11a4 4 0 1 0 0-8 4 4 0 0 0 0 8M22 20v-1a4 4 0 0 0-3-3.9M16 3.1a4 4 0 0 1 0 7.8',
         'apr': 'M20 6 9 17l-5-5', 'res': 'M4 20V10M10 20V4M16 20v-8M22 20H2', 'fin': 'M3 7h18v12H3zM3 11h18M7 15h3',
         'eq': 'M12 11a4 4 0 1 0 0-8 4 4 0 0 0 0 8M4 21v-1a6 6 0 0 1 6-6h4a6 6 0 0 1 6 6v1'}
    side_items = [('camp', 'Campanhas', None), ('cre', 'Creators', 0), ('apr', 'Aprovações', 1), ('res', 'Resultados', 2), ('fin', 'Financeiro', 3), ('eq', 'Equipe', None)]
    side = ''.join(f'<button type="button" class="bo-nav"{" data-scene=\"%d\"" % s if s is not None else " disabled"} tabindex="-1">{ico(I[k], 18, 1.8)}{n}</button>' for k, n, s in side_items)
    crs = [('SK', 'Skincare', '@bianca.alves', '84,2 mil seguidores · Instagram', ''), ('BE', 'Beleza', '@dudalima', '31,4 mil seguidores · Instagram', 'alt'),
           ('SK', 'Skincare', '@rafacosta', '22,1 mil seguidores · TikTok', ''), ('BE', 'Beleza', '@ninarocha', '58 mil seguidores · Instagram', 'alt')]
    cr = ''.join(f'<div class="bo-cr r{i + 1}"><div class="ph-img {a}"><em>{n}</em>{ini}</div><div class="info"><b>{h}</b><i>{inf}</i></div><span class="add">Adicionar à lista</span></div>' for i, (ini, n, h, inf, a) in enumerate(crs))
    kp = [('Alcance', 'alc', '1,2 mi', 'dark'), ('Visualizações', 'vis', '482.000', ''), ('Engajamento', 'eng', '4,8%', ''), ('Publicações', 'pub', '18', '')]
    kps = ''.join(f'<div class="bo-kpi {c} r{i + 1}"><span style="font-size:14px">{l}</span><b data-kpi="{k}">{v}</b></div>' for i, (l, k, v, c) in enumerate(kp))
    vals = [96, 128, 140, 162, 188, 176, 214, 240]
    bars = ''.join(f'<div>{v}<i class="bar{" hi" if i == 7 else ""}" style="height:{round(v / 240 * 180)}px;animation-delay:{0.3 + i * 0.06:.2f}s"></i></div>' for i, v in enumerate(vals))
    lbls = ''.join(f'<span>S{i + 1}</span>' for i in range(8))
    pays = [('C1', '@bianca.alves', 'Reels + 3 Stories', 'Liberado', True, 'R$ 1.200'), ('C2', '@dudalima', 'Reels', 'Liberado', True, 'R$ 800'),
            ('C3', '@rafacosta', 'TikTok', 'Aguardando publicação', False, 'R$ 950'), ('C4', '@ninarocha', '3 Stories', 'Aguardando aprovação', False, 'R$ 600')]
    py = ''.join(f'<div class="bo-pay r{i + 1}"><span class="av">{a}</span><span class="tx"><b>{h}</b><i>{d}</i></span><span class="t{" on" if on else ""}">{t}</span><span class="v">{v}</span></div>' for i, (a, h, d, t, on, v) in enumerate(pays))
    dots = ''.join(f'<button type="button" class="dot" aria-pressed="{"true" if i == 0 else "false"}">{n}</button>' for i, n in enumerate(['Encontrar creators', 'Aprovar conteúdo', 'Resultados', 'Financeiro']))
    return f'''<div class="bo-wrap">
<div class="bo-frame"><div class="bo-stage" role="img" aria-label="Animação do painel de marcas do HypeApp com dados de exemplo: busca de creators, aprovação de conteúdo, resultados e financeiro">
 <span class="tour tour-bo" aria-hidden="true">{CURSOR_SVG}<i></i></span>
 <div class="bo-win">
  <div class="bo-bar"><i></i><i></i><i></i>{PAINEL_URL.replace("<span>", "<span class=\"bo-url\">")}</div>
  <div class="bo-body">
   <aside class="bo-side"><span class="lg"><span>h</span>hypeapp</span>{side}<span class="bo-ws"><span class="av">CL</span><span style="display:flex;flex-direction:column"><b style="font-size:14px">Casa Lume</b><span style="font-size:12.5px">Workspace</span></span></span></aside>
   <section class="bo-main">
    <div class="bo-scene">
      <div class="bo-top"><span class="bo-h">Encontrar creators</span><span class="bo-pill">Lista: Verão Glow · <span id="bo-count">9 creators</span></span></div>
      <div style="display:flex;gap:8px"><span class="bo-search">{ico(I_SEARCH, 18)}<span id="bo-typed">skincare</span><span class="bo-caret"></span></span><span class="bo-round">{ico('M3 5h18l-7 8v6l-4 2v-8z', 20)}</span></div>
      <div class="bo-chips"><span class="on">Instagram</span><span>TikTok</span><span class="on">Beleza</span><span>10 mil a 100 mil</span></div>
      <div class="bo-grid4">{cr}</div>
    </div>
    <div class="bo-scene" hidden>
      <div class="bo-top"><span class="bo-h">Aprovações</span><div class="bo-seg"><span class="on">Conteúdos</span><span>Roteiros</span></div></div>
      <div style="display:flex;gap:18px">
        <div class="bo-video r1"><div><span>{ico('M8 5v14l11-7z', 24, fill=True)}</span></div></div>
        <div class="bo-panel r2">
          <span class="bo-who"><span class="av">C1</span><span style="display:flex;flex-direction:column"><b style="font-size:18px;font-weight:600">@bianca.alves</b><span style="font-size:14px">Reels · Skincare Pro</span></span><span class="bo-ok show">Aprovado</span></span>
          <div class="bo-kv"><span><span>Roteiro</span><b>Aprovado</b></span><span><span>Versão do conteúdo</span><b>2 de 2</b></span><span><span>Prazo de publicação</span><b>10/11</b></span></div>
          <span style="font-size:15px">Ajuste feito: produto aparece nos primeiros segundos e o cupom está na legenda.</span>
          <div class="bo-acts"><span>Pedir ajuste</span><span class="ink press">Aprovar conteúdo</span></div>
        </div>
      </div>
    </div>
    <div class="bo-scene" hidden>
      <div class="bo-top"><span class="bo-h">Resultados · Verão Glow</span><span class="bo-pill" style="height:40px">Últimos 30 dias</span></div>
      <div class="bo-grid4">{kps}</div>
      <div class="bo-chart r3"><span style="display:flex;justify-content:space-between;font-size:16px;font-weight:600"><span>Alcance por semana</span><span style="font-size:14px;font-weight:500">mil pessoas</span></span><div class="bo-bars">{bars}</div><div class="bo-lbls">{lbls}</div></div>
    </div>
    <div class="bo-scene" hidden>
      <span class="bo-h">Financeiro</span>
      <div style="display:flex;gap:14px">
        <div class="bo-fin dark r1"><span style="font-size:14px">Saldo da campanha</span><b id="bo-saldo">R$ 10.400</b><span style="font-size:14px;padding-top:6px">Reservado para pagamentos de creators</span></div>
        <div class="bo-fin r2"><span style="font-size:14px">Pagamentos liberados</span><b id="bo-pagos">R$ 2.000</b><span style="font-size:14px;padding-top:6px">de 12 creators</span></div>
      </div>
      <div class="bo-pays r3">{py}</div>
    </div>
   </section>
  </div>
 </div>
</div></div>
<div class="bo-ctrl"><button type="button" class="pp" aria-label="Pausar animação">{ico('M7 5h4v14H7zM13 5h4v14h-4z', 16, fill=True)}</button>{dots}<span class="note">Dados de exemplo</span></div>
</div>'''

# ---------- Páginas ----------
def homography_css(w, h, quad):
    """matrix3d que leva um retângulo w×h (origem no canto superior esquerdo) ao quadrilátero
    quad = [(x0,y0) sup. esq., (x1,y1) sup. dir., (x2,y2) inf. dir., (x3,y3) inf. esq.], em px da ilustração 1536×1024."""
    src = [(0, 0), (w, 0), (w, h), (0, h)]
    M, b = [], []
    for (x, y), (u, v) in zip(src, quad):
        M.append([x, y, 1, 0, 0, 0, -u * x, -u * y]); b.append(u)
        M.append([0, 0, 0, x, y, 1, -v * x, -v * y]); b.append(v)
    n = 8  # eliminação de Gauss
    A_ = [row + [bb] for row, bb in zip(M, b)]
    for c in range(n):
        piv = max(range(c, n), key=lambda r: abs(A_[r][c])); A_[c], A_[piv] = A_[piv], A_[c]
        for r in range(n):
            if r != c:
                f = A_[r][c] / A_[c][c]
                A_[r] = [a - f * cc for a, cc in zip(A_[r], A_[c])]
    a, b_, c_, d, e, f, g, hh = [A_[i][n] / A_[i][i] for i in range(n)]
    m = [a, d, 0, g, b_, e, 0, hh, 0, 0, 1, 0, c_, f, 0, 1]
    return 'matrix3d(' + ','.join(f'{x:.8g}' for x in m) + ')'

# Cantos das telas na ilustração (medidos no hero-base.webp, 1536×1024)
HERO_MON = [(328.2, 190.9), (1180.7, 73.8), (1151.8, 736.0), (279.5, 739.5)]
HERO_PH = [(1018.3, 433.7), (1250.2, 413.7), (1237.3, 927.5), (994.0, 920.2)]
# Contorno do celular por cima do monitor (para o celular continuar na frente)
HERO_PH_CLIP = [(1300, 380), (1220, 403), (1180, 406), (1160, 408), (1100, 414), (1061, 417), (1041, 419), (1027, 425), (1014, 440),
                (1008, 455), (1005, 470), (1004, 500), (1003, 515), (1001, 545), (999, 590), (997, 635), (995, 680), (993, 725), (990, 1000), (1300, 1000)]
HERO_MON_TELAS = ['bo-C2', 'bo-E1', 'bo-C1']
HERO_PH_TELAS = ['app-D1', 'app-E4', 'app-G2']

def hero_scene(A):
    """Ilustração animada da hero. Arquivos: assets/hero/hero-base.webp e hero-textos.webp; estilos no fim do site.css.
    Ciclo de 15,5 s: a ilustração com os textos animados e, depois, três telas reais no monitor e no celular."""
    mon = ''.join(f'<img src="{tela(A, c)}" alt="" width="1400" height="875" loading="lazy" decoding="async">' for c in HERO_MON_TELAS)
    ph = ''.join(f'<img src="{tela(A, c)}" alt="" width="600" height="1298" loading="lazy" decoding="async">' for c in HERO_PH_TELAS)
    clip = 'polygon(' + ','.join(f'{x}px {y}px' for x, y in HERO_PH_CLIP) + ')'
    return f'''<div class="hero-art">
<div class="hh" role="img" aria-label="HypeApp: painel de campanhas no computador para marcas e app no celular para creators" data-hh>
  <img src="{A('assets/hero/hero-base.webp')}" width="1536" height="1024" alt="" fetchpriority="high" decoding="async">
  <div class="hh-scr" aria-hidden="true"><div class="hh-stage">
    <div class="hh-mon" style="transform:{homography_css(1120, 760, HERO_MON)}">{mon}</div>
    <img class="hh-front" src="{A('assets/hero/hero-base.webp')}" alt="" width="1536" height="1024" style="clip-path:{clip}">
    <div class="hh-ph" style="transform:{homography_css(600, 1298, HERO_PH)}">{ph}<i class="hh-notch"></i></div>
  </div></div>
  <div aria-hidden="true">
    <span class="hh-t hh-big hh-logo"></span>
    <span class="hh-t hh-rise hh-nav-inicio"></span>
    <span class="hh-t hh-rise hh-nav-campanhas"></span>
    <span class="hh-t hh-rise hh-nav-criadores"></span>
    <span class="hh-t hh-rise hh-nav-financeiro"></span>
    <span class="hh-t hh-type hh-busca"></span>
    <span class="hh-t hh-pop hh-avatar"></span>
    <span class="hh-t hh-big hh-titulo"></span>
    <span class="hh-t hh-rise hh-subtitulo"></span>
    <span class="hh-t hh-rise hh-aba-todas"></span>
    <span class="hh-t hh-rise hh-aba-andamento"></span>
    <span class="hh-t hh-rise hh-aba-disponiveis"></span>
    <span class="hh-t hh-rise hh-aba-concluidas"></span>
    <span class="hh-t hh-pop hh-r1-letra"></span>
    <span class="hh-t hh-rise hh-r1-nome"></span>
    <span class="hh-t hh-rise hh-r1-chip1"></span>
    <span class="hh-t hh-rise hh-r1-chip2"></span>
    <span class="hh-t hh-pop hh-r1-status"></span>
    <span class="hh-t hh-pop hh-r2-letra"></span>
    <span class="hh-t hh-rise hh-r2-nome"></span>
    <span class="hh-t hh-rise hh-r2-chip1"></span>
    <span class="hh-t hh-rise hh-r2-chip2"></span>
    <span class="hh-t hh-pop hh-r2-status"></span>
    <span class="hh-t hh-pop hh-r3-letra"></span>
    <span class="hh-t hh-rise hh-r3-nome"></span>
    <span class="hh-t hh-rise hh-r3-chip1"></span>
    <span class="hh-t hh-rise hh-r3-chip2"></span>
    <span class="hh-t hh-pop hh-r3-status"></span>
    <span class="hh-t hh-rise hh-cel-hora"></span>
    <span class="hh-t hh-pop hh-cel-avatar"></span>
    <span class="hh-t hh-big hh-cel-ola"></span>
    <span class="hh-t hh-rise hh-cel-sub"></span>
    <span class="hh-t hh-rise hh-cel-destaque"></span>
    <span class="hh-t hh-rise hh-cel-destaque-l1"></span>
    <span class="hh-t hh-rise hh-cel-destaque-l2"></span>
    <span class="hh-t hh-rise hh-cel-proximo"></span>
    <span class="hh-t hh-rise hh-cel-perfil"></span>
    <span class="hh-t hh-rise hh-cel-perfil-l1"></span>
    <span class="hh-t hh-rise hh-cel-perfil-l2"></span>
    <span class="hh-t hh-rise hh-cel-tab-inicio"></span>
    <span class="hh-t hh-rise hh-cel-tab-campanhas"></span>
    <span class="hh-t hh-rise hh-cel-tab-comunidade"></span>
    <span class="hh-t hh-rise hh-cel-tab-perfil"></span>
    <span class="hh-t hh-big hh-card-roteiro"></span>
    <span class="hh-t hh-big hh-card-comunidade"></span>
    <span class="hh-t hh-pop hh-card-l"></span>
    <span class="hh-t hh-pop hh-card-b"></span>
    <span class="hh-t hh-pop hh-card-s"></span>
    <span class="hh-t hh-pop hh-card-99"></span>
  </div>
</div>
</div>'''

COMO_FUNCIONA_C = [
    ('01 · Seu perfil', 'Mostre quem você é', 'Crie sua conta e conecte suas redes.', 'Ilustração: creator segurando o celular, com o cartão de perfil ao lado'),
    ('02 · Oportunidades', 'Encontre sua próxima conexão', 'Explore campanhas e envie sua inscrição.', 'Ilustração: celular com a lista de campanhas e o botão Quero participar'),
    ('03 · Entregas', 'Sua ideia ganha forma', 'Envie conteúdo e acompanhe as aprovações.', 'Ilustração: dedo tocando o botão de envio, com o selo de aprovação'),
    ('04 · Carteira', 'Acompanhe seu saldo', 'Solicite o saque quando o valor for liberado.', 'Ilustração: celular com a carteira, saldo oculto e o botão Solicitar saque'),
]

COMO_FUNCIONA_M = [
    ('01 · Comercial', 'Vamos falar sobre sua marca', 'Conte seus objetivos e conheça as condições de acesso.', 'Ilustração: profissional com headset atendendo pelo computador'),
    ('02 · Campanha', 'Sua campanha começa aqui', 'Defina briefing, remuneração, critérios e fases.', 'Ilustração: monitor com a tela Nova campanha do painel'),
    ('03 · Aprovações', 'Escolha creators. Aprove entregas.', 'Receba inscrições e revise roteiros e conteúdos.', 'Ilustração: notebook com a tela Aprovações do painel'),
    ('04 · Resultados', 'Acompanhe cada resultado', 'Veja publicações, métricas e pagamentos no painel.', 'Ilustração: tablet com a tela Resultados do painel'),
]

def como_funciona(A, pid, tab, label, items, media, hidden=False):
    """Carrossel do "Como funciona". media='video' usa cenaN.mp4 (make_comofunciona.py);
    media='img' usa marcaN.webp com aproximação sutil da imagem inteira (sem camadas, nada interno se mexe).
    Títulos e textos ficam no HTML. Só o card ativo anima; nada avança sozinho."""
    cards = ''
    for i, (tg, t, d, alt) in enumerate(items):
        n = i + 1
        if media == 'video':
            m = (f'<video muted playsinline loop preload="{"metadata" if i == 0 else "none"}" width="720" height="720" '
                 f'poster="{A(f"assets/como-funciona/cena{n}.webp")}" aria-label="{alt}"><source src="{A(f"assets/como-funciona/cena{n}.mp4")}" type="video/mp4"></video>')
        else:
            m = f'<img class="cf-anim cf-anim-{n}" src="{A(f"assets/como-funciona/marca{n}.webp")}" alt="{alt}" width="720" height="720" loading="lazy" decoding="async">'
        cards += (f'<li class="cf-card{" is-active" if i == 0 else ""}" data-i="{i}" style="--d:{i * 110}ms">'
                  f'<div class="cf-top"><span class="cf-tag">{tg}</span><h3 class="cf-t">{t}</h3><p class="cf-d">{d}</p></div>'
                  f'<div class="cf-media">{m}</div></li>')
    dots = ''.join(f'<button type="button" class="cf-dot" data-i="{i}" aria-label="Passo {i + 1}: {tg.split(" · ")[1]}"{" aria-current=\"step\"" if i == 0 else ""}></button>' for i, (tg, *_r) in enumerate(items))
    pause_i = ico('M7 5h4v14H7zM13 5h4v14h-4z', 16, fill=True)
    return f'''<div id="{pid}" role="tabpanel" aria-labelledby="{tab}" class="cf" data-cf{" hidden" if hidden else ""}>
    <ol class="cf-track" aria-label="{label}">{cards}</ol>
    <div class="cf-foot"><div class="cf-dots">{dots}</div><span class="cf-hint">Arraste para explorar</span>
      <button type="button" class="cf-pause" data-cf-pause aria-pressed="false">{pause_i}<span>Pausar animação</span></button></div>
  </div>'''

def _round_clip(pts, box, r=40, steps=6):
    """clip-path: polygon() com cantos arredondados para um quadrilátero (px do desenho 760×760),
    em % da caixa do bloco. Os cantos viram curvas suaves de raio ~r."""
    x0, y0, w, h = box
    out = []
    n = len(pts)
    for i in range(n):
        P, A_, B = pts[i], pts[i - 1], pts[(i + 1) % n]
        def toward(Q):
            dx, dy = Q[0] - P[0], Q[1] - P[1]; L_ = (dx * dx + dy * dy) ** 0.5; k = min(r, L_ / 2) / L_
            return (P[0] + dx * k, P[1] + dy * k)
        s, e = toward(A_), toward(B)
        for j in range(steps + 1):
            u = j / steps
            x = (1 - u) ** 2 * s[0] + 2 * (1 - u) * u * P[0] + u * u * e[0]
            y = (1 - u) ** 2 * s[1] + 2 * (1 - u) * u * P[1] + u * u * e[1]
            out.append(f'{(x - x0) / w * 100:.2f}% {(y - y0) / h * 100:.2f}%')
    return 'polygon(' + ','.join(out) + ')'

# Mosaico da seção "Gestão da carreira" (desenho de 760×760; tudo em % na tela)
GC_BLOCKS = {
    'phone': [(0, 0), (374, 0), (374, 470), (0, 505)],
    'entrega': [(0, 517), (374, 482), (374, 760), (0, 760)],
    'receb': [(386, 0), (760, 0), (760, 350), (386, 402)],
    'char': [(386, 414), (760, 362), (760, 760), (386, 760)],
}
GC_BOX = {'phone': (0, 0, 374, 505), 'entrega': (0, 482, 374, 278), 'receb': (386, 0, 374, 402), 'char': (386, 348, 374, 412)}

def gestao_carreira(L, A):
    def pos(k):
        x, y, w, h = GC_BOX[k]
        return (f'left:{x / 7.6:.3f}%;top:{y / 7.6:.3f}%;width:{w / 7.6:.3f}%;height:{h / 7.6:.3f}%;'
                f'--clip:{_round_clip(GC_BLOCKS[k], GC_BOX[k])}')
    cal = ico('M7 3v3M17 3v3M4 8h16M5 5h14a1 1 0 0 1 1 1v13a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V6a1 1 0 0 1 1-1zM8 12h2M12 12h2M16 12h0M8 16h2M12 16h2', 30)
    wallet = ico('M4 7a2 2 0 0 1 2-2h11v4M4 7v10a2 2 0 0 0 2 2h13a1 1 0 0 0 1-1v-8a1 1 0 0 0-1-1H6a2 2 0 0 1-2-2zM16 14h.01', 34)
    return f'''<section class="gc" aria-labelledby="gc-t">
  <div class="gc-copy">
    <span class="gc-eyebrow">Gestão da carreira</span>
    <h2 id="gc-t" class="gc-h">Sua carreira de creator, <span>mais organizada.</span></h2>
    <p class="gc-p">Acompanhe oportunidades, organize suas entregas e tenha clareza sobre seus recebimentos.</p>
    <ul class="gc-tags" aria-label="O que o app organiza"><li>Parcerias</li><li>Entregas</li><li>Recebimentos</li></ul>
    <div class="gc-ctas"><a class="btn btn-cta btn-lg" href="{L('/baixar/')}">Baixar o app</a><a class="gc-link" href="{L('/criadores/', '#recursos')}">Conhecer funcionalidades {ico(I_ARROW, 20)}</a></div>
  </div>
  <figure class="gc-fig">
    <div class="mz" data-mz aria-hidden="true">
      <div class="mz-b mz-phone" style="{pos('phone')}"><img class="mz-fill" src="{A('assets/carreira/celular-inicio.webp')}" alt="" width="902" height="1218" loading="lazy" decoding="async"></div>
      <div class="mz-b mz-receb" style="{pos('receb')}"><div class="mz-in">
        <div class="mz-rh"><b>Recebimentos</b>{wallet}</div>
        <div class="mz-row"><i class="mz-dot"></i><span>Em campanha</span><i class="mz-bar"><i style="width:76%"></i></i><i class="mz-dash"></i></div>
        <div class="mz-row"><i class="mz-dot"></i><span>A liberar</span><i class="mz-bar"><i style="width:58%"></i></i><i class="mz-dash"></i></div>
      </div></div>
      <div class="mz-b mz-entrega" style="{pos('entrega')}"><div class="mz-in">
        <span class="mz-cal">{cal}</span><b class="mz-et">Próxima entrega</b><span class="mz-es">Envio de roteiro</span><span class="mz-pill"><i></i>Em andamento</span>
      </div></div>
      <div class="mz-b mz-char" style="{pos('char')}"><img class="mz-fill" src="{A('assets/carreira/creator-celular.webp')}" alt="" width="993" height="1094" loading="lazy" decoding="async"></div>
    </div>
    <figcaption class="gc-cap">Interface e dados ilustrativos.</figcaption>
  </figure>
</section>'''

def p_home(L, A):
    steps_c = [('Crie sua conta no app', 'Baixe o HypeApp, crie seu perfil e conecte Instagram, TikTok ou YouTube.'),
               ('Inscreva-se pelo mural', 'Encontre no mural as campanhas do seu nicho e se inscreva, ou responda aos convites das marcas.'),
               ('Envie roteiro e conteúdo', 'Siga o briefing, envie para aprovação e registre a publicação.'),
               ('Receba pela carteira', 'Acompanhe o saldo e solicite o saque quando o valor for liberado.')]
    steps_m = [('Fale com o comercial', 'Conte objetivo, prazo e forma de trabalho. O comercial envia a proposta e libera o acesso ao painel.'),
               ('Monte o mural da campanha', 'Publique no painel o briefing, a remuneração, os critérios e as fases.'),
               ('Receba inscrições e aprove', 'Creators se inscrevem pelo mural. Você seleciona, convida e aprova roteiros e conteúdos.'),
               ('Acompanhe os resultados', 'Publicações registradas, métricas e pagamentos em um só lugar.')]
    li = lambda s: ''.join(f'<li><span class="step-n">{i + 1}</span><span class="t">{t}</span><span class="d">{d}</span></li>' for i, (t, d) in enumerate(s))
    faq = [('O cadastro garante participação em campanhas?', 'Não. Cada campanha tem critérios próprios e a marca ou a curadoria seleciona quem participa.'),
           ('Quanto custa para creators?', 'Nada. O HypeApp é gratuito para creators: não há mensalidade nem taxa sobre o valor que você recebe das campanhas.'),
           ('Como as marcas contratam?', 'Pelo painel, em campanhas self-service, ou com a operação da Você no Hype. Os valores são sob consulta com o comercial.'),
           ('Já tenho conta no HypeApp. Preciso me cadastrar de novo?', 'Não. Atualize o app pela loja e entre com o mesmo e-mail e a mesma senha que você já usava.')]
    chips = lambda xs: ''.join(f'<span class="chip">{x}</span>' for x in xs)
    return f'''
<section class="hero-home" aria-labelledby="hero-t">
  <div class="stack hero-copy">
    <span class="notice">App para iPhone e Android · <a href="{L('/baixar/')}">Baixar o app</a></span>
    <h1 id="hero-t" class="display hero-t1"><span>O app de quem cria conteúdo.</span> <span>O painel de quem contrata.</span></h1>
    <p class="lead">O app de gestão de carreira para creators e a plataforma de gestão de campanhas para marcas.</p>
    <div class="row hero-ctas">
      <a class="btn btn-cta btn-lg" href="{L('/baixar/')}">Baixar o app {ico(I_ARROW)}</a>
      <a class="btn btn-grey btn-lg" href="{L('/marcas/')}">Sou marca ou agência</a>
    </div>
  </div>
  {hero_scene(A)}
</section>

<section class="stack-lg cf-sec" aria-labelledby="como-t" data-tabs>
  <div class="cf-head">
    <div class="stack" style="gap:6px"><h2 id="como-t" class="h2 cf-h">Como funciona</h2><p class="cf-sub">Seu próximo passo começa aqui.</p></div>
    <div class="row cf-ctrl">
      <div class="seg" role="tablist" aria-label="Escolha o público">
        <button type="button" role="tab" id="tab-c" aria-selected="true" aria-controls="painel-c">Para creators</button>
        <button type="button" role="tab" id="tab-m" aria-selected="false" aria-controls="painel-m" tabindex="-1">Para marcas</button>
      </div>
      <div class="cf-arrows"><button type="button" class="cf-arrow" data-cf-prev aria-label="Passo anterior">{ico('M19 12H5M11 6l-6 6 6 6', 20)}</button><button type="button" class="cf-arrow" data-cf-next aria-label="Próximo passo">{ico(I_ARROW, 20)}</button></div>
    </div>
  </div>
  {como_funciona(A, 'painel-c', 'tab-c', 'Passos para creators', COMO_FUNCIONA_C, 'video')}
  {como_funciona(A, 'painel-m', 'tab-m', 'Passos para marcas', COMO_FUNCIONA_M, 'img', hidden=True)}
</section>

{gestao_carreira(L, A)}

<section class="faq-block" aria-labelledby="faq-t">
  <div class="stack"><h2 id="faq-t" class="h2">Perguntas frequentes</h2><a class="link-strong" href="{L('/perguntas-frequentes/')}">Ver todas as perguntas</a></div>
  <div class="faq">{faq_html(faq)}</div>
</section>

{_blog.blog_section(L, A, POSTS, ico)}

<section class="band-dark between" aria-labelledby="ajuda-t" style="align-items:center">
  <div class="stack" style="gap:8px;flex:1 1 320px"><h2 id="ajuda-t" class="h3" style="font-size:32px">Precisa de ajuda?</h2><p class="body" style="font-size:16px">Busque nas perguntas frequentes ou fale com o suporte.</p></div>
  <form class="search" role="search" data-search-to="{L('/perguntas-frequentes/')}" style="flex:1 1 420px">
    <label for="busca-home" class="sr-only">Buscar nas perguntas frequentes</label>
    <input id="busca-home" class="input" type="search" placeholder="Ex.: como recebo o pagamento">
    <button class="btn btn-cta" type="submit">Buscar</button>
  </form>
</section>'''

CANDIDATURA = [
    ('app-D1', 'Encontre a campanha', 'Em Descobrir, filtre o mural por nicho e formato e veja as campanhas em destaque.', 'Descobrir'),
    ('app-E1', 'Leia o briefing', 'Confira o que a marca pede, a remuneração, as entregas, os prazos e os critérios antes de decidir.', 'Quero participar'),
    ('app-E2', 'Escolha o perfil e envie', 'Selecione com quais redes quer participar e, quando a campanha pedir, informe sua proposta de valor.', 'Enviar inscrição'),
    ('app-D3', 'Acompanhe a análise', 'Na aba Minhas inscrições você vê quando sua inscrição está em análise.', 'Inscrição em análise'),
    ('app-E3', 'Receba a resposta', 'Se for pré-selecionado, a marca envia o convite com as condições. Você aceita ou recusa pelo app.', 'Aceitar convite'),
]

def process_draw(L, A):
    """Process draw horizontal: a seção fica fixa enquanto a rolagem avança; a linha se desenha entre as etapas
    e, embaixo, aparecem a tela e o texto da etapa ativa. Sem JavaScript, mostra a primeira etapa."""
    n = len(CANDIDATURA)
    nodes = ''.join(
        f'<li class="pd-n{" on cur" if i == 0 else ""}" data-i="{i}"><button type="button" class="pd-dot" data-i="{i}" aria-label="Etapa {i + 1} de {n}: {t}"'
        f'{" aria-current=\"step\"" if i == 0 else ""}>{i + 1}</button><span class="pd-lbl">{t}</span></li>'
        for i, (code, t, d, chip) in enumerate(CANDIDATURA))
    texts = ''.join(
        f'<div class="pd-card{" on" if i == 0 else ""}" data-i="{i}"><span class="pd-k">Etapa {i + 1} de {n}</span><h3 class="pd-t">{t}</h3>'
        f'<p class="pd-d">{d}</p><span class="pd-chip">{chip}</span></div>'
        for i, (code, t, d, chip) in enumerate(CANDIDATURA))
    phones = ''.join(f'<img src="{tela(A, code)}" alt="Tela do app: {t}" width="600" height="1298" data-i="{i}"{" class=\"on\"" if i == 0 else ""} loading="lazy" decoding="async">'
                     for i, (code, t, *_r) in enumerate(CANDIDATURA))
    return f'''<section class="pd" id="candidatura" aria-labelledby="pd-h" data-pd>
  <div class="pd-pin"><div class="pd-box">
    <div class="pd-head">
      <span class="pd-eyebrow">Do mural à campanha</span>
      <h2 id="pd-h" class="pd-h">Como se candidatar a uma campanha</h2>
      <p class="pd-p">Cinco passos, todos pelo app. Cada campanha tem critérios próprios, e a seleção é feita pela marca ou pela curadoria.</p>
    </div>
    <div class="pd-time"><span class="pd-rail" aria-hidden="true"><i></i></span><ol class="pd-nodes" aria-label="Etapas da candidatura">{nodes}</ol></div>
    <div class="pd-stage">
      <div class="pd-texts" aria-live="polite">{texts}
        <p class="pd-end">Selecionado? Daí em diante, roteiro, conteúdo, publicação e pagamento seguem pelo app. <a href="#recursos">Ver as funcionalidades</a></p></div>
      <figure class="pd-phone"><div class="dev-phone"><div class="dev-screen">{phones}</div></div><figcaption>Dados de exemplo.</figcaption></figure>
    </div>
  </div></div>
</section>'''

def p_criadores(L, A):
    camps = [('beleza', 'Paga', 'VG', 'Verão Glow', 'Beleza · Instagram', 'R$ 1.200', ''),
             ('moda', 'Permuta', 'MO', 'Brisa de Verão', 'Moda · TikTok', 'Produto + R$ 300', 'alt'),
             ('gastronomia', 'Recebido', 'GA', 'Café Brasa', 'Gastronomia · Instagram', 'Produto', ''),
             ('fitness', 'Paga', 'FT', 'Run Club SP', 'Fitness · YouTube', 'R$ 2.500', 'alt')]
    cards = ''.join(f'<article class="camp-card" data-nicho="{n}"><div class="camp-cover {a}"><span class="tag">{tp}</span>{ini}</div><div class="camp-body"><b style="font-size:19px;font-weight:600">{nm}</b><span class="small muted">{ni}</span><span class="v">{v}</span></div></article>' for n, tp, ini, nm, ni, v, a in camps)
    filt = ''.join(f'<button type="button" data-v="{v}" aria-pressed="{"true" if v == "todas" else "false"}">{t}</button>' for v, t in [('todas', 'Todas'), ('beleza', 'Beleza'), ('moda', 'Moda'), ('gastronomia', 'Gastronomia'), ('fitness', 'Fitness')])
    rec = [('Perfil e redes', 'Conecte suas redes e mostre seus dados profissionais e valores por formato.'),
           ('Mural e convites', 'Filtre o mural por nicho, inscreva-se e responda aos convites das marcas.'),
           ('Entregas e aprovações', 'Briefing, roteiro, conteúdo e ajustes com prazo em cada etapa.'),
           ('Carteira', 'Saldo em campanha, a liberar e disponível para saque via PIX.')]
    recs = ''.join(f'<div class="feat"><span class="h4">{t}</span><span style="font-size:15px">{d}</span></div>' for t, d in rec)
    faq = [('Quem pode participar?', 'Qualquer pessoa com 18 anos ou mais, ou emancipada, sem mínimo de seguidores. Cada campanha tem critérios próprios.'),
           ('O cadastro garante campanhas?', 'Não. Cada campanha tem critérios próprios e a seleção é feita pela marca ou pela curadoria.'),
           ('Como recebo o pagamento?', 'O valor aparece na carteira do app e pode ser sacado quando for liberado.'),
           ('Preciso emitir nota fiscal?', 'Depende da campanha e do seu cadastro como pessoa física ou jurídica. O app informa o que é exigido antes do pagamento.'),
           ('Quanto custa para creators?', 'Nada. O HypeApp é gratuito para creators: não há mensalidade nem taxa sobre o valor que você recebe das campanhas.'),
           ('Recebidos e permuta: o produto fica comigo?', 'Depende da campanha. O mural de cada campanha informa se o produto é seu ou se precisa ser devolvido.'),
           ('A marca pode usar meu conteúdo depois?', 'Depende do contrato da campanha, firmado entre você e a marca. Confira as condições de uso de imagem antes de aceitar o convite.')]
    return f'''
<section class="split" aria-labelledby="hero-c">
  <div class="stack" style="gap:24px;flex-basis:540px">
    <span class="tag">Para creators</span>
    <h1 id="hero-c" class="display">O app completo para quem cria conteúdo.</h1>
    <p class="lead">Encontre no mural as campanhas do seu nicho, inscreva-se, entregue pelo app e acompanhe seus pagamentos na carteira.</p>
    <div class="row"><a class="btn btn-cta btn-lg" href="{L('/baixar/')}">Baixar o app</a><a class="btn btn-ghost btn-lg" href="{L('/entrar/', '#creators')}">Já tenho conta</a></div>
    <p class="small" style="max-width:540px">Grátis para iPhone e Android. Crie sua conta pelo app. Para maiores de 18 anos, sem mínimo de seguidores.</p>
  </div>
  <div style="flex-basis:520px">{motion_criador('comunidade')}</div>
</section>

{motion_stack(L, 'comunidade')}

{process_draw(L, A)}

<div class="sc-intro stack" id="recursos" style="gap:10px"><h2 class="h2">Funcionalidades do app</h2><p class="body" style="max-width:620px">Tudo o que uma campanha pede, do cadastro ao saque. Toque em cada item para ver a tela.</p></div>
{showcase(A, 'sc-cadastro', 'phone', 'Cadastro', 'Seu perfil pronto em poucos passos', 'Cinco etapas com barra de progresso. No fim, as marcas já veem suas redes e seus valores.', [
  ('app-B3', 'Conecte suas redes', 'Instagram, TikTok e YouTube. Quem conecta todas recebe mais convites.'),
  ('app-B4', 'Defina seus valores', 'Quanto você cobra por Reels, Stories e post, com valor sugerido.'),
  ('app-B7', 'Perfil concluído', 'Pronto para entrar nas campanhas.')])}
{showcase(A, 'sc-campanhas', 'phone', 'Campanhas', 'Campanhas do seu nicho em um só lugar', 'Descubra campanhas abertas, responda convites e acompanhe o próximo passo de cada uma.', [
  ('app-D1', 'Descobrir', 'Busca, filtro por nicho e campanhas em destaque.'),
  ('app-D5', 'Convites', 'Convites das marcas, com prazo para responder.'),
  ('app-D2', 'Minhas campanhas', 'Ativas, inscrições e finalizadas, com o próximo passo à vista.')], flip=True)}
{showcase(A, 'sc-execucao', 'phone', 'Entregas', 'Do briefing à publicação', 'Veja as condições antes de entrar, proponha seu valor e entregue cada etapa pelo app.', [
  ('app-E1', 'Detalhe da campanha', 'Ganho, duração, entregas, benefícios e regras.'),
  ('app-E2', 'Inscrição', 'Escolha as redes e proponha seu valor para cada uma.'),
  ('app-E5', 'Briefing', 'Sobre a campanha, produtos da marca e fases com prazo.'),
  ('app-E8', 'Envio do roteiro', 'Escreva ou anexe o roteiro e envie para aprovação.'),
  ('app-E6', 'Chat com a marca', 'Tire dúvidas sem sair da campanha.')])}
{showcase(A, 'sc-comunidade', 'phone', 'Comunidade', 'Uma comunidade de quem cria conteúdo', 'Feed, lives e grupos com outros creators, com regras claras de convivência.', [
  ('app-F1', 'Para você', 'Publicações, dicas e bastidores de outros creators.'),
  ('app-F2', 'Lives', 'Ao vivo, em breve e gravadas, com chat.'),
  ('app-F3', 'Grupos', 'Grupos por nicho, com outros creators.')], flip=True)}
{showcase(A, 'sc-carteira', 'phone', 'Carteira', 'Seu dinheiro com regras claras', 'Acompanhe o que está em campanha, a liberar e disponível, e peça o saque via PIX.', [
  ('app-G2', 'Carteira', 'Saldo disponível, valores a liberar e extrato.'),
  ('app-G4', 'Solicitar saque', 'Valor e chave PIX, com as regras do saque na tela.'),
  ('app-G5', 'Avaliações', 'A nota e os comentários das marcas sobre seu trabalho.')])}
{showcase(A, 'sc-rotina', 'phone', 'Organização', 'Prazos e avisos sem planilha', 'Calendário com os prazos de cada campanha e notificações por assunto.', [
  ('app-H1', 'Calendário', 'Prazos de envio e publicação por dia.'),
  ('app-H3', 'Notificações', 'Filtros por campanhas, comunidade e carteira.')], flip=True)}

<section class="band-dark between" aria-labelledby="baixar-c" style="align-items:center">
  <div class="stack" style="flex:1 1 380px">
    <h2 id="baixar-c" class="h2">Baixe o HypeApp</h2>
    <p class="body">Disponível para iPhone e Android. Já tem conta? Entre com o mesmo e-mail.</p>
    <div class="row">{stores(L)}</div>
  </div>
  <div class="qr">{QR}</div>
</section>

<section class="faq-block" aria-labelledby="faq-c">
  <div class="stack"><h2 id="faq-c" class="h2">Dúvidas de creators</h2><a class="link-strong" href="{L('/perguntas-frequentes/', '#creators')}">Ver todas as dúvidas</a></div>
  <div class="faq">{faq_html(faq)}</div>
</section>'''

def p_marcas(L, A):
    steps = [('Mural da campanha', 'Objetivo, público, formatos, prazos e remuneração, publicados no painel.'),
             ('Inscrições e convites', 'Creators se inscrevem pelo mural. Você também busca por nicho e rede e envia convites.'),
             ('Aprovações', 'Roteiros e conteúdos revisados antes de ir ao ar.'),
             ('Entregas e resultados', 'Publicações registradas e métricas da campanha no painel.')]
    li = ''.join(f'<li><span class="step-n">{i + 1}</span><span class="t">{t}</span><span class="d">{d}</span></li>' for i, (t, d) in enumerate(steps))
    faq = [('Qual a diferença entre self-service e gerenciada?', 'No self-service sua equipe opera tudo no painel. Na gerenciada, a Você no Hype cuida da estratégia, da curadoria e da operação.'),
           ('Quanto custa uma campanha?', 'Os valores são sob consulta e dependem do escopo, do volume e da forma de trabalho.'),
           ('Quais métricas eu acompanho?', 'As métricas vêm direto das redes sociais dos creators, conectadas ao app.'),
           ('E se o creator não entregar?', 'O valor reservado para aquela participação volta ao saldo da campanha.'),
           ('Agências podem gerir várias marcas?', 'Sim. Cada marca tem seu espaço no painel, e a equipe da agência alterna entre elas.')]
    return f'''
<section class="hero-center" aria-labelledby="hero-m">
  <div class="stack">
    <span class="tag ink">Para marcas e agências</span>
    <h1 id="hero-m" class="display" style="font-size:clamp(38px,5.8vw,64px)">Campanhas com creators do jeito que sua equipe preferir.</h1>
    <p class="lead">Monte o mural da campanha no painel, receba as inscrições dos creators, aprove roteiros e conteúdos e acompanhe as métricas. Você opera pelo painel ou deixa a operação com a Você no Hype.</p>
    <div class="row" style="justify-content:center"><a class="btn btn-cta" href="{L('/contato/marcas/')}">Falar com nosso time</a><a class="btn btn-soft" href="#modalidades">Ver as duas formas de trabalhar</a></div>
    <span class="small">Valores sob consulta, conforme escopo e volume.</span>
  </div>
  {motion_painel()}
</section>

<div class="sc-intro stack" id="funcionalidades" style="gap:10px"><h2 class="h2">Funcionalidades do painel</h2><p class="body" style="max-width:620px">Da criação da campanha ao pagamento dos creators. Clique em cada item para ver a tela.</p></div>
{showcase(A, 'sc-painel', 'web', 'Painel', 'Tudo o que pede atenção, logo na entrada', 'Pendências do dia, métricas do workspace e o resumo de cada campanha.', [
  ('bo-C1', 'Dashboard', 'Tarefas e aprovações pendentes, alcance e engajamento.'),
  ('bo-C2', 'Campanhas', 'Todas as campanhas em cartões, com filtros por situação.')])}
{showcase(A, 'sc-criar', 'web', 'Nova campanha', 'Crie uma campanha em quatro passos', 'Um assistente guia o briefing, os creators, o pagamento e as fases, com prévia ao vivo de como o creator vai ver.', [
  ('bo-C3', '1. Campanha', 'Briefing, materiais e prévia ao vivo no app.'),
  ('bo-C4', '2. Creators', 'Quantos creators e com quais critérios.'),
  ('bo-C5', '3. Pagamento', 'Formato de remuneração e valores.'),
  ('bo-C6', '4. Fases', 'Entregas, datas e regras de cada fase.')], flip=True)}
{showcase(A, 'sc-acompanhar', 'web', 'Acompanhamento', 'Cada etapa da campanha à vista', 'Progresso, quadro por etapa, contratos e resultados de cada campanha publicada.', [
  ('bo-D1', 'Visão geral', 'Progresso, etapas e o que precisa da sua ação.'),
  ('bo-D2', 'Gerenciamento', 'Quadro por etapa, com chat e revisão de conteúdo.'),
  ('bo-D4', 'Contratos', 'Envio e acompanhamento das assinaturas.'),
  ('bo-D6', 'Métricas e conteúdos', 'Alcance, desempenho e conteúdos publicados.')])}
{showcase(A, 'sc-criadores', 'web', 'Creators', 'Encontre e convide os creators certos', 'Catálogo com filtros, perfil público com métricas por rede e uma página de convite para o creator responder.', [
  ('bo-E1', 'Catálogo de creators', 'Filtros por rede, nicho, estado e seguidores.'),
  ('bo-E2', 'Perfil do creator', 'Métricas por rede e botão para convidar.'),
  ('bo-I3', 'Convite da campanha', 'A página que o creator recebe para aceitar ou recusar.')], flip=True)}
{showcase(A, 'sc-financeiro', 'web', 'Lives e financeiro', 'Lives e pagamentos no mesmo painel', 'Agende transmissões e acompanhe o saldo, as reservas e o extrato de cada campanha.', [
  ('bo-F1', 'Lives', 'Agendar, transmitir e ver as gravações.'),
  ('bo-G1', 'Financeiro', 'Saldo, reservas, extrato e consumo por campanha.'),
  ('bo-G2', 'Reservas de pagamento', 'Valor reservado para cada participação até a liberação.')])}

<section id="modalidades" class="stack-lg" aria-labelledby="mod-t">
  <h2 id="mod-t" class="h2">Duas formas de trabalhar</h2>
  <div class="grid-300">
    <div class="mode"><span class="tag soft">Self-service</span><span class="h3">Sua equipe opera a campanha no painel.</span>
      <ul><li>Monta o mural da campanha, com briefing e fases</li><li>Seleciona as inscrições e convida creators</li><li>Aprova roteiros e conteúdos</li><li>Acompanha entregas e métricas</li></ul></div>
    <div class="mode dark"><span class="tag">Gerenciada</span><span class="h3">A Você no Hype opera a campanha por você.</span>
      <ul><li>Estratégia e curadoria de creators</li><li>Negociação e contratos</li><li>Acompanhamento das entregas</li><li>Relatório de resultados</li></ul></div>
  </div>
  <div class="card-mid between" style="align-items:center">
    <div class="stack" style="gap:4px;flex:1 1 360px"><span class="h4">Quanto custa?</span><span style="font-size:16px">O valor depende do escopo, do volume e da forma de trabalho. O comercial monta a proposta depois de entender sua campanha.</span></div>
    <a class="btn btn-cta" href="{L('/contato/marcas/')}">Falar com nosso time</a>
  </div>
</section>

<section class="stack-lg" aria-labelledby="proc-t">
  <h2 id="proc-t" class="h2">Do briefing ao resultado</h2>
  <ol class="steps">{li}</ol>
</section>

{showcase(A, 'agencias', 'web', 'Para agências', 'Várias marcas, um painel', 'Agências gerenciam as campanhas de cada cliente em espaços separados, com equipe, aprovações e relatórios por marca.', [
  ('bo-I1', 'Equipe e permissões', 'Marca, empresa, equipe e quem pode fazer o quê.'),
  ('bo-B3', 'Uma marca por espaço', 'Nome, nicho e descrição de cada cliente.'),
  ('bo-B5', 'Primeiros passos', 'Atalhos para criar a primeira campanha e convidar a equipe.')], flip=True)}

<section class="faq-block" aria-labelledby="faq-m">
  <div class="stack"><h2 id="faq-m" class="h2">Dúvidas de marcas</h2><a class="link-strong" href="{L('/perguntas-frequentes/', '#marcas')}">Ver todas as dúvidas de marcas</a></div>
  <div class="faq">{faq_html(faq)}</div>
</section>

<section class="band-dark between" aria-labelledby="com-t" style="align-items:center">
  <h2 id="com-t" class="h2" style="flex:1 1 420px">Marque uma demonstração e veja como fica a sua gestão de marketing.</h2>
  <a class="btn btn-cta btn-xl" href="{L('/contato/marcas/')}">Falar com nosso time {ico(I_ARROW, 22)}</a>
</section>'''

def p_baixar(L, A):
    return f'''
<section class="band-white split" aria-labelledby="baixar-t" style="padding:clamp(28px,5vw,64px)">
  <div class="stack" style="gap:24px;flex-basis:480px">
    <h1 id="baixar-t" class="display" style="font-size:clamp(40px,5.8vw,64px)">Baixe o HypeApp</h1>
    <p class="lead">Campanhas, entregas e carteira no seu celular. Grátis para iPhone e Android.</p>
    <div class="row">{stores(L)}</div>
    <p class="small">Crie sua conta pelo app. Para maiores de 18 anos, sem mínimo de seguidores.</p>
    <dl class="req"><div><dt>iPhone</dt><dd>iOS 15.1 ou superior</dd></div><div><dt>Android</dt><dd>Veja a compatibilidade na Google Play</dd></div></dl>
  </div>
  <div class="stack" style="flex:0 1 360px;align-items:center;gap:16px;background:var(--ground);border-radius:32px;padding:32px;text-align:center">
    <div class="qr" style="width:220px;height:220px">{QR}</div>
    <span style="font-size:17px;font-weight:600">Está no computador?</span>
    <span style="font-size:15px">Aponte a câmera do celular para o código. Ele abre a loja certa para o seu aparelho.</span>
  </div>
</section>

<section class="band-dark between" aria-labelledby="conta-t" style="align-items:center;padding:40px 48px">
  <div class="stack" style="gap:6px;flex:1 1 420px"><h2 id="conta-t" style="font-size:25px;letter-spacing:-0.03em">Já tem conta no HypeApp?</h2>
    <p class="body" style="font-size:16px">Atualize o app pela loja e entre com o mesmo e-mail e a mesma senha.</p></div>
  <a class="btn btn-cta" href="{L('/entrar/', '#creators')}">Como entrar</a>
</section>

<section aria-label="Ajuda com o app" class="grid-280">
  <a class="help-card" href="{L('/perguntas-frequentes/', '#conta')}"><b>Baixei o app e não consigo entrar</b><span style="font-size:15px">O que fazer e quando falar com o suporte</span></a>
  <a class="help-card" href="{L('/suporte/')}"><b>O app não abre ou está lento</b><span style="font-size:15px">Abra um chamado com o modelo do aparelho</span></a>
  <a class="help-card" href="{L('/sobre/', '#canais')}"><b>Canais oficiais do HypeApp</b><span style="font-size:15px">Como reconhecer o app e os contatos verdadeiros</span></a>
</section>'''

FAQ_GROUPS = [
    ('creators', 'Para creators', [
        ('Quem pode participar?', 'Qualquer pessoa com 18 anos ou mais, ou emancipada, sem mínimo de seguidores. Cada campanha tem critérios próprios.'),
        ('Como eu começo?', 'Baixe o HypeApp na App Store ou no Google Play, crie sua conta e conecte suas redes. Não há mínimo de seguidores.'),
        ('O cadastro garante participação em campanhas?', 'Não. Cada campanha tem critérios próprios e a marca ou a curadoria seleciona quem participa.'),
        ('Quanto custa para creators?', 'Nada. O HypeApp é gratuito para creators: não há mensalidade nem taxa sobre o valor que você recebe das campanhas.'),
        ('Como recebo o pagamento?', 'O valor aparece na carteira do app e pode ser sacado via PIX quando for liberado.'),
        ('Preciso emitir nota fiscal?', 'Depende da campanha e do seu cadastro como pessoa física ou jurídica. O app informa o que é exigido antes do pagamento.'),
        ('Recebidos e permuta: o produto fica comigo?', 'Depende da campanha. O mural de cada campanha informa se o produto é seu ou se precisa ser devolvido.'),
        ('A marca pode usar meu conteúdo depois?', 'Depende do contrato da campanha, firmado entre você e a marca. Confira as condições de uso de imagem antes de aceitar o convite.'),
        ('Como funciona a comunidade?', 'Feed, grupos e lives com outros creators dentro do app, com regras de participação.'),
    ]),
    ('marcas', 'Para marcas e agências', [
        ('Como marcas e agências começam?', 'Pelo formulário Falar com nosso time. O comercial entende a campanha, envia uma proposta e libera o acesso ao painel.'),
        ('Como os creators chegam à minha campanha?', 'Você monta o mural da campanha no painel e os creators se inscrevem por ele. Também dá para buscar creators e enviar convites.'),
        ('Quanto custa uma campanha?', 'Os valores são sob consulta e dependem do escopo, do volume e da forma de trabalho.'),
        ('Qual a diferença entre self-service e gerenciada?', 'No self-service sua equipe opera tudo no painel. Na gerenciada, a Você no Hype cuida da estratégia, da curadoria e da operação.'),
        ('Quais métricas eu acompanho?', 'As métricas vêm direto das redes sociais dos creators, conectadas ao app.'),
        ('E se o creator não entregar?', 'O valor reservado para aquela participação volta ao saldo da campanha.'),
        ('Agências podem gerir várias marcas?', 'Sim. Cada marca tem seu espaço no painel.'),
    ]),
    ('conta', 'Conta, acesso e segurança', [
        ('Baixei o app e não consigo entrar. O que faço?', 'Confira se o app está atualizado na loja e entre com o e-mail e a senha do cadastro. Se esqueceu a senha, use Esqueci a senha na tela de entrada. Se o erro continuar, abra um chamado no suporte.'),
        ('Já tenho conta no HypeApp. Preciso me cadastrar de novo?', 'Não. Atualize o app pela loja e entre com o mesmo e-mail e a mesma senha que você já usava.'),
        ('Como excluo minha conta?', 'Pelo app ou pela página de exclusão de conta, que explica o que é apagado e o que fica guardado por obrigação legal.'),
        ('Como reconheço os canais oficiais?', 'O HypeApp é desenvolvido pela Você no Hype. Os links oficiais das lojas e das redes estão na página Sobre. O HypeApp nunca pede senha ou código por mensagem.'),
    ]),
]

def p_faq(L, A):
    groups = ''.join(f'<section class="stack" id="{gid}" data-faq-group aria-labelledby="g-{gid}"><h2 class="h3" id="g-{gid}">{gt}</h2><div class="faq" style="flex:none">{faq_html(items)}</div></section>' for gid, gt, items in FAQ_GROUPS)
    return f'''
<section class="page-hero" aria-labelledby="faq-h">
  <h1 id="faq-h" class="display" style="font-size:clamp(38px,5.4vw,60px)">Perguntas frequentes</h1>
  <p class="lead">Respostas rápidas sobre o app, campanhas, pagamentos, valores para marcas e segurança.</p>
  <form class="search" role="search" style="max-width:640px">
    <label for="faq-busca" class="sr-only">Buscar nas perguntas</label>
    <input id="faq-busca" class="input" type="search" placeholder="Ex.: nota fiscal, saque, agência">
    <button class="btn btn-ink" type="submit">Buscar</button>
  </form>
  <p class="small muted" id="faq-contagem" aria-live="polite"></p>
  <div class="row"><a class="chip" href="#creators" style="text-decoration:none">Creators</a><a class="chip" href="#marcas" style="text-decoration:none">Marcas e agências</a><a class="chip" href="#conta" style="text-decoration:none">Conta e segurança</a></div>
</section>
<div class="stack-lg" style="gap:48px">
  {groups}
  <div class="empty stack" id="faq-vazio" hidden style="align-items:center"><span class="h4">Nenhuma resposta para essa busca.</span><span class="small">Tente outra palavra ou fale com o suporte.</span><a class="btn btn-ink" href="{L('/suporte/')}">Abrir chamado</a></div>
</div>
<section class="band-dark between" aria-labelledby="sup-t" style="align-items:center">
  <div class="stack" style="gap:6px;flex:1 1 360px"><h2 id="sup-t" class="h3">Não encontrou o que procura?</h2><p class="body" style="font-size:16px">O suporte atende quem já usa o app. Marcas falam com o comercial.</p></div>
  <div class="row"><a class="btn btn-cta" href="{L('/suporte/')}">Falar com o suporte</a><a class="btn btn-soft" href="{L('/contato/marcas/')}">Falar com nosso time</a></div>
</section>'''

def p_sobre(L, A):
    return f'''
<section class="page-hero" aria-labelledby="sobre-h">
  <span class="tag ink">Sobre</span>
  <h1 id="sobre-h" class="display" style="font-size:clamp(38px,5.4vw,60px)">Sobre o HypeApp</h1>
  <p class="lead">O HypeApp é a plataforma da Você no Hype que conecta creators e marcas em campanhas de marketing de influência, do convite ao pagamento.</p>
</section>
<section class="grid-300" aria-label="O que é o HypeApp">
  <div class="card stack"><span class="h4">Para creators</span><p class="small" style="font-size:15px">Um app para iPhone e Android com campanhas, convites, entregas, comunidade e carteira.</p><a class="link-strong" href="{L('/criadores/')}">Para creators</a></div>
  <div class="card stack"><span class="h4">Para marcas e agências</span><p class="small" style="font-size:15px">Um painel na web para encontrar creators, aprovar conteúdos e acompanhar resultados.</p><a class="link-strong" href="{L('/marcas/')}">Para marcas</a></div>
  <div class="card stack" style="background:var(--ink);color:var(--purple-ink)"><span class="h4">Quem opera</span><p class="small" style="font-size:15px">Desenvolvido e operado pela Você no Hype Marketing e Entretenimento LTDA, CNPJ 43.442.408/0001-26. Av. Cardeal Motta, 1057, City América, São Paulo/SP, CEP 02452-001.</p></div>
</section>
<section class="band-white split" id="canais" aria-labelledby="canais-t">
  <div class="stack"><h2 id="canais-t" class="h2">Canais oficiais</h2><p class="body">Use só estes endereços. O HypeApp nunca pede senha, código de verificação ou chave PIX por mensagem.</p></div>
  <dl class="req" style="grid-template-columns:repeat(auto-fit,minmax(min(100%,240px),1fr))">
    <div><dt>Site</dt><dd>www.hypeapp.com.br</dd></div>
    <div><dt>App para iPhone</dt><dd><a href="{CFG['ios']}" target="_blank" rel="noopener">App Store</a></dd></div>
    <div><dt>App para Android</dt><dd><a href="{CFG['android']}" target="_blank" rel="noopener">Google Play</a></dd></div>
    <div><dt>Redes sociais</dt><dd>{social_links("social social-inline")}</dd></div>
    <div><dt>Suporte</dt><dd><a href="{L('/suporte/')}">Formulário de suporte</a></dd></div>
    <div><dt>Comercial</dt><dd><a href="{L('/contato/marcas/')}">Falar com nosso time</a></dd></div>
  </dl>
</section>'''

def p_contato(L, A):
    cards = [('Sou marca ou agência', 'Quero fazer uma campanha ou conhecer o painel.', 'Falar com nosso time', L('/contato/marcas/'), 'btn-cta'),
             ('Já uso o app', 'Dúvida, erro, pagamento, conta ou denúncia.', 'Abrir chamado no suporte', L('/suporte/'), 'btn-ink'),
             ('Parcerias e imprensa', 'Propostas de parceria, eventos e pedidos de imprensa.', 'Ver o contato', '#parcerias', 'btn-grey'),
             ('Meus dados pessoais', 'Acesso, correção ou exclusão de dados, e o encarregado.', 'Ver a política de privacidade', L('/privacidade/', '#encarregado'), 'btn-grey')]
    cs = ''.join(f'<div class="card stack" style="gap:12px"><span class="h4">{t}</span><p class="small" style="font-size:15px;flex:1">{d}</p><a class="btn {c}" href="{h}" style="align-self:flex-start">{b}</a></div>' for t, d, b, h, c in cards)
    return f'''
<section class="page-hero" aria-labelledby="ct-h">
  <h1 id="ct-h" class="display" style="font-size:clamp(38px,5.4vw,60px)">Fale com o HypeApp</h1>
  <p class="lead">Escolha o assunto para falar com a equipe certa.</p>
</section>
<section class="grid-280" aria-label="Assuntos">{cs}</section>
<section class="card-mid" id="parcerias" aria-labelledby="parc-t"><h2 id="parc-t" class="h4">Parcerias e imprensa</h2><p class="body" style="margin-top:8px">Escreva para contato@vocenohype.com.br com o assunto e o prazo do pedido.</p></section>'''

def field(id_, label, kind='text', req=True, hint='', opt=False, extra='', ph=''):
    lab = label + (' <span class="opt">(opcional)</span>' if not req else '')
    attrs = f' required' if req else ''
    if kind == 'textarea':
        ctl = f'<textarea class="input" id="{id_}" name="{id_}"{attrs}{extra} placeholder="{ph}"></textarea>'
    else:
        ctl = f'<input class="input" id="{id_}" name="{id_}" type="{kind}"{attrs}{extra} placeholder="{ph}">'
    h = f'<p class="hint" id="{id_}-h">{hint}</p>' if hint else ''
    return f'<div class="field"><label for="{id_}">{lab}</label>{ctl}{h}<p class="err" hidden></p></div>'

def choices(name, legend, opts, req=True):
    o = ''.join(f'<label class="choice"><input type="radio" name="{name}" value="{v}"{" required" if req else ""}><span>{t}</span></label>' for v, t in opts)
    return f'<fieldset class="field"><legend>{legend}</legend><div class="choices">{o}</div><p class="err" hidden></p></fieldset>'

def select(id_, label, opts, req=True):
    o = '<option value="">Selecione</option>' + ''.join(f'<option value="{v}">{t}</option>' for v, t in opts)
    return f'<div class="field"><label for="{id_}">{label}</label><select class="input" id="{id_}" name="{id_}"{" required" if req else ""}>{o}</select><p class="err" hidden></p></div>'

def privacy_check(L, id_):
    return f'<div class="field"><label class="check"><input type="checkbox" id="{id_}" name="{id_}" required><span>Li a <a href="{L("/privacidade/")}">política de privacidade</a> e concordo com o uso destes dados para responder ao meu contato.</span></label><p class="err" hidden></p></div>'

FORM_LIVE = ' data-live' if WEB else ''
HONEYPOT = '<p class="hp" hidden><label>Não preencha este campo <input name="bot-field" tabindex="-1" autocomplete="off"></label></p>'

def preview_note():
    return '<p class="form-note" role="note">Prévia: o envio é simulado e nada é gravado. Em produção, o pedido vira um lead no CRM Comercial da plataforma Você no Hype antes da confirmação.</p>' if CFG['preview'] else ''

def multi(name, legend, opts, req=True, hint=''):
    """Grupo de múltipla escolha (checkbox). Com req, exige pelo menos uma opção."""
    o = ''.join(f'<label class="choice"><input type="checkbox" name="{name}" value="{v}"{" data-group required" if req else " data-group"}><span>{t}</span></label>' for v, t in opts)
    h = f'<p class="hint">{hint}</p>' if hint else ''
    return f'<fieldset class="field"><legend>{legend} <span class="opt">(marque quantas quiser)</span></legend><div class="choices">{o}</div>{h}<p class="err" hidden></p></fieldset>'

def etapa(n, titulo, corpo):
    return f'<fieldset class="form-step"><legend class="form-step-h"><span>{n}</span>{titulo}</legend><div class="form-step-b">{corpo}</div></fieldset>'

# Faixas de verba mensal (sugestão de 30/10, ajustar com o comercial). "alta" entra na fila prioritária.
VERBAS = [('ate-5k', 'Até R$ 5 mil'), ('5-20k', 'R$ 5 mil a R$ 20 mil'), ('20-50k', 'R$ 20 mil a R$ 50 mil'), ('50k-mais', 'Acima de R$ 50 mil'), ('nao-sei', 'Ainda não sei')]

# Versão dos arquivos de estilo e script (muda a cada alteração: força o navegador a baixar de novo)
import hashlib as _hl
VER = {n: _hl.md5(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets', n), 'rb').read()).hexdigest()[:8] for n in ('site.css', 'site.js')}

def p_contato_marcas(L, A):
    s1 = ('<div class="cols-2">' + field('empresa', 'Nome da empresa', extra=' autocomplete="organization" maxlength="200"')
          + field('site', 'Site ou Instagram da marca', extra=' maxlength="300"', ph='www.marca.com.br ou @marca', hint='Ajuda a conhecer a marca antes da conversa.') + '</div>'
          + '<div class="cols-2">' + select('segmento', 'Segmento', [('moda', 'Moda'), ('beleza', 'Beleza'), ('alimentos', 'Alimentos'), ('tecnologia', 'Tecnologia'), ('servicos', 'Serviços'), ('outro', 'Outro')])
          + field('cidade', 'Cidade e estado', extra=' autocomplete="address-level2" maxlength="120"', ph='São Paulo, SP') + '</div>')
    s2 = ('<div class="cols-2">' + field('nome', 'Nome completo', extra=' autocomplete="name" maxlength="200"')
          + field('cargo', 'Cargo ou função', extra=' autocomplete="organization-title" maxlength="120"', ph='Marketing, sócio, agência…') + '</div>'
          + '<div class="cols-2">' + field('email', 'E-mail corporativo', 'email', extra=' autocomplete="email" maxlength="200"', ph='nome@empresa.com.br')
          + field('whatsapp', 'WhatsApp com DDD', 'tel', extra=' autocomplete="tel" data-kind="tel" inputmode="tel" maxlength="60"', ph='(11) 90000-0000') + '</div>')
    s3 = (choices('experiencia', 'Já trabalha com influenciadores?', [('nunca', 'Nunca'), ('ocasional', 'Ocasionalmente'), ('frequente', 'Com frequência')])
          + choices('campanhas_mes', 'Quantas campanhas pretende fazer por mês?', [('1-2', '1 a 2'), ('3-10', '3 a 10'), ('10-mais', 'Mais de 10')])
          + select('verba', 'Verba mensal aproximada para influenciadores', VERBAS)
          + multi('redes', 'Que redes importam', [('instagram', 'Instagram'), ('tiktok', 'TikTok'), ('youtube', 'YouTube'), ('kwai', 'Kwai')]))
    s4 = (choices('objetivo', 'Qual o principal objetivo?', [('lancamento', 'Lançar produto'), ('alcance', 'Ganhar alcance'), ('vendas', 'Gerar vendas'), ('recorrencia', 'Recorrência'), ('outro', 'Outro')])
          + multi('interesses', 'O que mais interessa no painel', [('criadores', 'Encontrar creators'), ('aprovacoes', 'Aprovar roteiros e conteúdos'), ('pagamentos', 'Pagamentos'), ('lives', 'Lives'), ('metricas', 'Métricas')])
          + choices('gestao_hoje', 'Como gerencia isso hoje?', [('planilha', 'Planilha'), ('agencia', 'Agência'), ('plataforma', 'Outra plataforma'), ('nada', 'Ainda não gerencio')]))
    s5 = (choices('usuarios', 'Quantas pessoas da equipe usariam o painel?', [('1', '1'), ('2-5', '2 a 5'), ('6-mais', '6 ou mais')])
          + choices('agencia', 'É uma agência que atende várias marcas?', [('sim', 'Sim'), ('nao', 'Não')])
          + '<p class="form-note" data-show-when="agencia=sim" hidden>Agências usam um espaço separado para cada marca no painel, e isso muda o plano. Vamos considerar na proposta.</p>'
          + choices('inicio', 'Para quando precisa começar?', [('agora', 'Agora'), ('30-dias', 'Em até 30 dias'), ('pesquisando', 'Só pesquisando')])
          + field('mensagem', 'Quer contar algo mais?', 'textarea', req=False, extra=' maxlength="3000"', ph='Produto, público, datas importantes ou o que mais ajudar'))
    consent = ('<div class="field"><label class="check"><input type="checkbox" id="aceite" name="aceite" required><span>Autorizo a Você no Hype a usar estes dados para responder a este pedido '
               f'e entrar em contato por e-mail e WhatsApp sobre o HypeApp, conforme a <a href="{L("/privacidade/")}">política de privacidade</a>. '
               'Posso pedir a exclusão a qualquer momento em contato@vocenohype.com.br.</span></label><p class="err" hidden></p></div>')
    return f'''
<section class="split" style="align-items:flex-start" aria-labelledby="cm-h">
  <div class="stack form-side" style="gap:20px;flex:1 1 360px">
    <span class="tag ink">Para marcas e agências</span>
    <h1 id="cm-h" class="display" style="font-size:clamp(38px,5vw,56px)">Fale com nosso time</h1>
    <p class="lead">Conte um pouco sobre a sua empresa e como vocês trabalham com influenciadores. Nosso time retorna com uma proposta. Leva cerca de 3 minutos.</p>
    <ul class="body" style="padding-left:20px;margin:0;display:flex;flex-direction:column;gap:6px"><li>Valores sob consulta, conforme escopo e volume</li><li>Painel para operar sozinho ou campanha gerenciada pela Você no Hype</li><li>Retornamos em até 2 dias úteis</li></ul>
    <p class="small muted">É creator? <a href="{L('/baixar/')}">Baixe o app</a>. Já usa o HypeApp? <a href="{L('/suporte/')}">Fale com o suporte</a>.</p>
  </div>
  <form class="card form form-steps" style="flex:1 1 560px" data-form name="comercial" method="POST" action="{'/api/lead' if WEB else L('/contato/enviado/')}" data-next="{L('/contato/enviado/')}"{FORM_LIVE} novalidate>
    <input type="hidden" name="form-name" value="comercial">
    {HONEYPOT}
    {etapa(1, 'Quem é a empresa', s1)}
    {etapa(2, 'Quem está falando', s2)}
    {etapa(3, 'Como a empresa usa influenciadores hoje', s3)}
    {etapa(4, 'O que a empresa quer do painel', s4)}
    {etapa(5, 'Operacional', s5)}
    {consent}
    <p class="err form-erros" role="alert" hidden></p>
    {preview_note()}
    <button class="btn btn-cta btn-lg" type="submit" style="align-self:flex-start">Enviar para nosso time</button>
  </form>
</section>'''

def p_enviado(L, A):
    return f'''
<section class="band-white stack" style="align-items:flex-start;gap:20px;max-width:820px" aria-labelledby="ok-h">
  <span class="tag">Recebido</span>
  <h1 id="ok-h" class="display" style="font-size:clamp(36px,5vw,56px)">Recebemos sua mensagem</h1>
  <p class="lead">Obrigado! Nosso time retorna em até 2 dias úteis, pelo e-mail ou WhatsApp informados.</p>
  <div class="row"><a class="btn btn-ink" href="{L('/marcas/')}">Voltar para Para marcas</a><a class="btn btn-grey" href="{L('/perguntas-frequentes/', '#marcas')}">Ver dúvidas de marcas</a></div>
</section>'''

SUP_ASSUNTOS = [('conta', 'Conta e acesso'), ('redes', 'Redes sociais'), ('campanha', 'Campanha ou entrega'), ('pagamento', 'Pagamento ou saque'),
                ('erro', 'Erro no app'), ('denuncia', 'Denúncia'), ('exclusao', 'Excluir minha conta'), ('outro', 'Outro')]

def p_suporte(L, A):
    cond = lambda when, inner: f'<div class="stack" style="gap:22px" data-show-when="assunto={when}" hidden>{inner}</div>'
    return f'''
<section class="split" style="align-items:flex-start" aria-labelledby="sp-h">
  <div class="stack" style="gap:20px;flex:1 1 380px">
    <span class="tag ink">Suporte</span>
    <h1 id="sp-h" class="display" style="font-size:clamp(38px,5vw,56px)">Como podemos ajudar?</h1>
    <p class="lead">Atendimento para quem já usa o app ou o painel. Segunda a sexta, das 10h às 18h, com primeira resposta em até 2 dias úteis. Também pelo e-mail contato@vocenohype.com.br ou pelo telefone (11) 3834-5221.</p>
    <div class="stack" style="gap:8px">
      <span class="small" style="font-weight:600">Antes de abrir um chamado</span>
      <a class="help-card" href="{L('/perguntas-frequentes/', '#conta')}"><b>Baixei o app e não consigo entrar</b></a>
      <a class="help-card" href="{L('/perguntas-frequentes/', '#creators')}"><b>Quando o pagamento é liberado</b></a>
      <a class="help-card" href="{L('/perguntas-frequentes/', '#creators')}"><b>Preciso emitir nota fiscal?</b></a>
    </div>
    <p class="small muted">Pedidos sobre seus dados pessoais seguem pela <a href="{L('/privacidade/', '#encarregado')}">política de privacidade</a>. Marcas novas falam com o <a href="{L('/contato/marcas/')}">comercial</a>.</p>
  </div>
  <form class="card form" style="flex:1 1 520px" data-form name="suporte" method="POST" action="{'/api/contato' if WEB else L('/suporte/enviado/')}" data-next="{L('/suporte/enviado/')}"{FORM_LIVE} novalidate>
    <input type="hidden" name="form-name" value="suporte">
    {HONEYPOT}
    {choices('uso', 'Você usa', [('app', 'O app (creator)'), ('painel', 'O painel (marca ou agência)')])}
    {select('assunto', 'Assunto', SUP_ASSUNTOS)}
    {cond('conta|exclusao', field('email_conta', 'E-mail da conta', 'email', ph='nome@email.com'))}
    {cond('redes', '<div class="cols-2">' + select('rede', 'Rede', [('instagram', 'Instagram'), ('tiktok', 'TikTok'), ('youtube', 'YouTube')]) + field('arroba', 'Seu @ nessa rede', ph='@seuperfil') + '</div>' + field('erro_rede', 'Mensagem de erro', req=False))}
    {cond('campanha', '<div class="cols-2">' + field('campanha_nome', 'Nome da campanha') + select('etapa', 'Etapa', [('convite', 'Convite'), ('roteiro', 'Roteiro'), ('conteudo', 'Conteúdo'), ('publicacao', 'Publicação')]) + '</div>')}
    {cond('pagamento', '<div class="cols-2">' + field('data_saque', 'Data da solicitação', 'date') + field('valor', 'Valor', extra=' inputmode="decimal"', ph='R$ 0,00') + '</div><p class="form-note">Nunca informe sua chave PIX ou dados bancários neste formulário.</p>')}
    {cond('erro', '<div class="cols-2">' + field('aparelho', 'Aparelho e sistema', ph='Ex.: iPhone 13, iOS 18') + field('versao', 'Versão do app', req=False, ph='Ex.: 2.0.1') + '</div>' + field('passos', 'O que você fez até o erro aparecer', 'textarea'))}
    {cond('denuncia', field('alvo', 'Link ou @ denunciado'))}
    {cond('exclusao', '<p class="form-note">Antes de excluir, veja o que acontece com campanhas, saldo e dados na página <a href="' + L('/exclusao-de-conta/') + '">Exclusão de conta</a>.</p>')}
    <div class="cols-2">{field('nome', 'Nome', extra=' autocomplete="name"')}{field('email', 'E-mail para resposta', 'email', extra=' autocomplete="email"', ph='nome@email.com')}</div>
    {field('descricao', 'Descreva o que aconteceu', 'textarea')}
    {privacy_check(L, 'aceite')}
    <p class="err form-erros" role="alert" hidden></p>
    {preview_note()}
    <button class="btn btn-ink btn-lg" type="submit" style="align-self:flex-start">Abrir chamado</button>
  </form>
</section>'''

def p_sup_enviado(L, A):
    return f'''
<section class="band-white stack" style="align-items:flex-start;gap:20px;max-width:820px" aria-labelledby="ok-h">
  <span class="tag ink">Chamado aberto</span>
  <h1 id="ok-h" class="display" style="font-size:clamp(36px,5vw,56px)">Seu chamado foi aberto</h1>
  <p class="lead">A primeira resposta chega em até 2 dias úteis, de segunda a sexta, das 10h às 18h.</p>
  <p class="small">A confirmação automática não é a resposta da equipe. Se precisar complementar, responda ao e-mail do chamado.</p>
  <div class="row"><a class="btn btn-ink" href="{L('/')}">Voltar ao início</a><a class="btn btn-grey" href="{L('/perguntas-frequentes/')}">Perguntas frequentes</a></div>
</section>'''

def p_entrar(L, A):
    painel = CFG['painel']
    pbtn = (f'<a class="btn btn-ink" href="{painel}">Entrar no painel</a>' if painel else
            '<span class="btn btn-ink" aria-disabled="true">Entrar no painel</span><p class="small">[Endereço do painel a confirmar. Proposta: painel.hypeapp.com.br]</p>')
    return f'''
<section class="page-hero" aria-labelledby="en-h"><h1 id="en-h" class="display" style="font-size:clamp(38px,5.4vw,60px)">Entrar</h1><p class="lead">Escolha como você usa o HypeApp.</p></section>
<section class="grid-300" aria-label="Formas de entrar">
  <div class="card stack" id="creators" style="gap:14px"><span class="entrar-ico" style="width:52px;height:52px">{ico(I_PHONE, 22)}</span><h2 class="h3">Sou creator</h2>
    <p class="small" style="font-size:15px">O HypeApp para creators funciona no celular. Abra o app e entre com seu e-mail. Se ainda não tem, baixe na loja.</p>
    <div class="row">{stores(L)}</div><p class="small muted">Para maiores de 18 anos, sem mínimo de seguidores.</p></div>
  <div class="card stack" id="marcas" style="gap:14px"><span class="entrar-ico ink" style="width:52px;height:52px">{ico(I_CASE, 22)}</span><h2 class="h3">Sou marca ou agência</h2>
    <p class="small" style="font-size:15px">O painel das marcas funciona no navegador. O acesso é liberado pelo comercial depois do primeiro contato.</p>
    <div class="stack" style="gap:8px;align-items:flex-start">{pbtn}</div>
    <a class="link-strong" href="{L('/contato/marcas/')}">Ainda não tem acesso? Falar com nosso time</a></div>
</section>
<section class="card-mid between" style="align-items:center" aria-label="Problemas para entrar"><span class="h4">Problemas para entrar?</span><a class="btn btn-grey" href="{L('/suporte/')}">Falar com o suporte</a></section>'''

def p_app(L, A):
    return f'''
<section class="band-white split" data-app-redirect data-ios="{CFG['ios']}" data-android="{CFG['android']}" aria-labelledby="app-h">
  <div class="stack" style="gap:20px"><h1 id="app-h" class="display" style="font-size:clamp(36px,5vw,56px)">Baixe o HypeApp</h1>
    <p class="lead" id="app-msg" aria-live="polite">Escolha a loja do seu aparelho.</p><div class="row">{stores(L)}</div></div>
  <div class="qr" style="width:220px;height:220px;flex:0 0 auto">{QR}</div>
</section>'''

LEGAL = {
    '/privacidade/': ('Política de privacidade', 'Como o HypeApp trata os dados pessoais de quem usa o site, o app e o painel.', [
        ('controlador', 'Quem é o controlador', 'Você no Hype Marketing e Entretenimento LTDA, CNPJ [CNPJ], [endereço]. [Texto aprovado pelo jurídico.]'),
        ('dados', 'Quais dados tratamos', '[Dados do site (formulários e cookies necessários), do app e do painel, conforme a minuta jurídica, seção 4.]'),
        ('finalidades', 'Para que usamos', '[Finalidades e bases legais aprovadas.]'),
        ('compartilhamento', 'Com quem compartilhamos', '[Marcas participantes, fornecedores de tecnologia e pagamentos, conforme a minuta.]'),
        ('retencao', 'Por quanto tempo guardamos', '[Prazos de retenção aprovados.]'),
        ('direitos', 'Seus direitos', 'Você pode pedir confirmação, acesso, correção, anonimização, portabilidade e exclusão dos seus dados. [Canal e prazo aprovados.]'),
        ('encarregado', 'Encarregado de dados', 'Encarregado: [nome ou empresa]. Contato: contato@vocenohype.com.br. [Texto público da designação, conforme a Resolução CD/ANPD 18/2024.]'),
        ('atualizacoes', 'Atualizações desta política', 'Versão [número], de [data].')]),
    '/termos/': ('Termos de uso', 'Regras para usar o site, o app e o painel do HypeApp.', [
        ('aceite', 'Aceite', '[Texto aprovado pelo jurídico, minuta seção 2.]'),
        ('idade', 'Quem pode usar', '[Idade mínima e regras aprovadas.]'),
        ('conta', 'Conta e segurança', '[Responsabilidades da pessoa usuária.]'),
        ('campanhas', 'Campanhas e pagamentos', '[Regras de participação, aprovação e pagamento.]'),
        ('fiscal', 'Obrigações fiscais', '[Cláusula fiscal, minuta seção 6.]'),
        ('alteracoes', 'Alterações', 'Versão [número], de [data].')]),
    '/cookies/': ('Política de cookies', 'Quais tecnologias o site usa e para quê.', [
        ('necessarios', 'Cookies necessários', 'O site não usa cookies de publicidade nem de rastreamento. Usa apenas o necessário para funcionar.'),
        ('medicao', 'Medição de visitas', 'Usamos o Cloudflare Web Analytics para contar visitas de forma agregada. Ele não usa cookies e não identifica quem visita.'),
        ('opcionais', 'Cookies opcionais', 'Se alguma ferramenta de publicidade ou de análise com cookies for adicionada, o site vai pedir sua escolha antes de carregá-la.')]),
    '/exclusao-de-conta/': ('Exclusão de conta', 'Como pedir a exclusão da sua conta do HypeApp e dos dados associados.', [
        ('app', 'Pelo app', '[Caminho no app a confirmar, por exemplo: Perfil, Configurações, Excluir conta.]'),
        ('site', 'Pelo site', 'Abra um chamado no suporte com o assunto Excluir minha conta, usando o e-mail da conta.'),
        ('o-que-acontece', 'O que é apagado', '[Dados apagados, prazo e o que fica guardado por obrigação legal, como registros fiscais de pagamentos.]'),
        ('saldo', 'Saldo e campanhas em andamento', '[Regra aprovada para saldo a liberar e entregas abertas.]')]),
}

def p_legal(url):
    def f(L, A):
        t, d, secs = LEGAL[url]
        toc = ''.join(f'<a href="#{sid}">{st}</a>' for sid, st, _ in secs)
        body = ''.join(f'<h2 id="{sid}">{st}</h2><p>{tx}</p>' for sid, st, tx in secs)
        extra = ''
        if url == '/exclusao-de-conta/':
            extra = f'<p><a class="btn btn-ink" href="{L("/suporte/")}">Abrir pedido de exclusão</a></p>'
        return f'''
<section class="page-hero" aria-labelledby="lg-h"><h1 id="lg-h" class="display" style="font-size:clamp(36px,5vw,56px)">{t}</h1><p class="lead">{d}</p>
  {'<p class="small muted">Rascunho para revisão. O texto final depende da aprovação do jurídico.</p>' if not WEB else ''}</section>
<div class="doc-layout"><nav class="toc" aria-label="Nesta página">{toc}</nav><article class="prose card">{body}{extra}</article></div>'''
    return f

def p_legal_hub(L, A):
    docs = [('Política de privacidade', 'Como tratamos dados pessoais no site, no app e no painel, e os seus direitos.', L('/privacidade/')),
            ('Termos de uso', 'Regras para usar o site, o app e o painel do HypeApp.', L('/termos/')),
            ('Política de cookies', 'Quais tecnologias o site usa e como mudar suas preferências.', L('/cookies/')),
            ('Encarregado de dados', 'Quem responde por dados pessoais e como falar com ele.', L('/privacidade/', '#encarregado')),
            ('Exclusão de conta', 'Como excluir sua conta e o que acontece com os seus dados.', L('/exclusao-de-conta/'))]
    cards = ''.join(f'<a class="help-card" href="{u}"><b>{t}</b><span class="small muted">{s}</span></a>' for t, s, u in docs)
    return f'''
<section class="page-hero" aria-labelledby="lgh-h"><h1 id="lgh-h" class="display" style="font-size:clamp(36px,5vw,56px)">Documentos legais</h1>
  <p class="lead">Privacidade, termos e seus direitos sobre dados no HypeApp. Dúvidas: contato@vocenohype.com.br.</p></section>
<div class="legal-hub">{cards}</div>'''

def p_404(L, A):
    return f'''
<section class="band-white stack" style="align-items:flex-start;gap:20px" aria-labelledby="nf-h">
  <span class="tag soft">Erro 404</span>
  <h1 id="nf-h" class="display" style="font-size:clamp(36px,5vw,56px)">Página não encontrada</h1>
  <p class="lead">O endereço pode ter mudado ou ter sido digitado errado.</p>
  <div class="row"><a class="btn btn-ink" href="{L('/')}">Ir para o início</a><a class="btn btn-grey" href="{L('/perguntas-frequentes/')}">Perguntas frequentes</a></div>
</section>'''


LEGAL_FILES = {
    '/privacidade/': ('privacidade.html', 'Política de Privacidade', 'Quais dados pessoais o HypeApp coleta, como usa, com quem compartilha e como você exerce seus direitos.',
        ['O controlador aparece como "HypeApp", sem razão social e CNPJ. Os termos citam Você no Hype Marketing e Entretenimento LTDA, CNPJ 43.442.408/0001-26.',
         'O encarregado aparece só pelo e-mail. A Resolução CD/ANPD 18/2024 pede que a identidade do encarregado também seja pública.',
         'Duas referências internas estão trocadas: o resumo manda ver a seção 8 para exclusão (é a 9) e a tabela manda ver a seção 5 para rastreamento (é a 6).',
         'A política fala do app. Falta cobrir o site (formulários do comercial e do suporte, cookies) e o painel das marcas.']),
    '/termos/': ('termos.html', 'Termos de Uso', 'Termos e condições gerais de uso do aplicativo HypeApp.',
        ['Texto de 27/04/2022, anterior ao relançamento. As cláusulas 2, 9.4 e 9.6 dizem que o HypeApp só intermedeia e não participa de transações financeiras, mas o app novo tem carteira, saque e pagamentos.',
         'Não cita recursos novos: Hype Points, comunidade, lives, avaliações e o painel das marcas.',
         'Erro de digitação na cláusula 2 ("Hyppe App") e menção a um "catálogo (hypeapp.com.br)" que não existe no site novo.',
         'O telefone e o horário da cláusula 15 também foram para a página de suporte; confirmar se continuam valendo.']),
    '/exclusao-de-conta/': ('exclusao.html', 'Exclusão de conta e dados', 'Como excluir sua conta no HypeApp e o que acontece com os seus dados.',
        ['Texto da página oficial de exclusão (api-v2.hypeapp.com.br/api/legal/solicitar-exclusao-dados), sem a linha técnica sobre a chamada da API.',
         'Se as lojas apontam para o endereço antigo, mantenha os dois no ar ou redirecione o antigo para cá.']),
}

def p_legal_file(url):
    def f(L, A):
        fn, t, d, notes = LEGAL_FILES[url]
        body = open(os.path.join(HERE, 'content', fn), encoding='utf-8').read()
        body = body.replace('{{PRIVACIDADE}}', L('/privacidade/')).replace('{{EXCLUSAO}}', L('/exclusao-de-conta/'))
        toc = ''.join('<a href="#%s">%s</a>' % (i, re.sub('<[^>]+>', '', x)) for i, x in re.findall(r'<h2 id="([^"]+)">(.*?)</h2>', body))
        rev = ''
        if CFG['preview'] and notes:
            rev = ('<aside class="legal-review" aria-label="Pontos para o jurídico"><b>Só na prévia · pontos para o jurídico revisar</b><ul>'
                   + ''.join('<li>%s</li>' % n for n in notes) + '</ul></aside>')
        return ('<section class="page-hero" aria-labelledby="lg-h"><h1 id="lg-h" class="display" style="font-size:clamp(36px,5vw,56px)">%s</h1><p class="lead">%s</p></section>\n%s\n'
                '<div class="doc-layout"><nav class="toc" aria-label="Nesta página">%s</nav><article class="prose card legal">%s</article></div>') % (t, d, rev, toc, body)
    return f

# ---------- Blog (content/blog/*.md, ver blog_build.py) ----------
import blog_build as _blog
POSTS = _blog.load_posts(HERE, WEB)
BLOG_ON = bool(POSTS)   # sem artigo, /blog/ não existe e os links para ele somem
POST_META = _blog.post_meta(POSTS, BASE)

PAGES = [
    ('/', p_home, 'wide'), ('/criadores/', p_criadores, 'wide'), ('/marcas/', p_marcas, 'wide'),
    ('/baixar/', p_baixar, 'tight'), ('/perguntas-frequentes/', p_faq, 'mid'), ('/sobre/', p_sobre, 'mid'),
    ('/contato/', p_contato, 'mid'), ('/contato/marcas/', p_contato_marcas, 'mid'), ('/contato/enviado/', p_enviado, 'mid'),
    ('/suporte/', p_suporte, 'mid'), ('/suporte/enviado/', p_sup_enviado, 'mid'), ('/entrar/', p_entrar, 'mid'),
    ('/app', p_app, 'mid'),
    ('/privacidade/', p_legal_file('/privacidade/'), 'mid'), ('/termos/', p_legal_file('/termos/'), 'mid'),
    ('/cookies/', p_legal('/cookies/'), 'mid'), ('/exclusao-de-conta/', p_legal_file('/exclusao-de-conta/'), 'mid'),
    ('/legal/', p_legal_hub, 'mid'),
    ('/404', p_404, 'mid'),
]
if BLOG_ON:
    PAGES += [('/blog/', _blog.p_blog(POSTS), 'wide')] + [('/blog/' + _p['slug'] + '/', _blog.p_post(_p), 'mid') for _p in POSTS]

FALLBACK = {
    '/entrar/': ('Entrar no HypeApp', 'Creators entram pelo app. Marcas e agências entram pelo painel.'),
    '/app': ('Baixar o HypeApp', 'Leva à loja certa para o seu celular.'),
    '/404': ('Página não encontrada | HypeApp', 'O endereço pode ter mudado.'),
}

def crumbs(url):
    names = {r['url']: r['pagina'] for r in R}
    names.update({u: v['pagina'] for u, v in POST_META.items()}); names['/blog/'] = 'Blog'
    parts, acc = [], '/'
    items = [{'@type': 'ListItem', 'position': 1, 'name': 'Início', 'item': BASE + '/'}]
    for seg in url.strip('/').split('/'):
        acc += seg + '/'
        items.append({'@type': 'ListItem', 'position': len(items) + 1, 'name': names.get(acc, seg), 'item': BASE + acc})
    return {'@context': 'https://schema.org', '@type': 'BreadcrumbList', 'itemListElement': items}

ORG = {'@context': 'https://schema.org', '@type': 'Organization', 'name': 'HypeApp', 'url': BASE + '/',
       'parentOrganization': {'@type': 'Organization', 'name': 'Você no Hype Marketing e Entretenimento LTDA'},
       'logo': BASE + '/assets/logo-hypeapp.svg',
       'sameAs': [u for _, u, _, _ in SOCIAL] + [CFG['ios'], CFG['android']]}

def build_page(url, fn, kind):
    L, A = make_link(url)
    m = META.get(url) or POST_META.get(url)
    title, desc = (m['title'], m['desc']) if m else FALLBACK[url]
    robots = 'noindex, nofollow' if CFG['preview'] else (m['robots'] if m else 'noindex, follow')
    canon = BASE + url if url != '/404' else ''
    main = fn(L, A)
    cls = 'wrap' + (' tight' if kind == 'tight' else '')
    body = header(url, L, A) + f'\n<main class="{cls}" id="conteudo">{main}</main>\n' + footer(L, A)
    body = mark_ph(body)
    for p, _ in [('/criadores/', 0), ('/marcas/', 0), ('/perguntas-frequentes/', 0)]:
        pass
    jl = [ORG] if url == '/' else ([crumbs(url)] if url not in ('/404', '/app') else [])
    if url in POST_META:
        jl.append(POST_META[url]['ld'])
    ld = ''.join(f'<script type="application/ld+json">{json.dumps(j, ensure_ascii=False)}</script>' for j in jl)
    bar = (f'<div class="preview-bar"><strong>Prévia do site</strong> · conteúdo em revisão. Textos entre colchetes aguardam aprovação. Envios de formulário são simulados. <a href="{A("iphone/index.html")}">Ver no iPhone</a></div>' if CFG['preview'] else '')
    head = f'''<title>{html.escape(title)}</title>
<meta name="claude:viewport-fit-sides" content="cover">
<meta name="description" content="{html.escape(desc)}">
<meta name="robots" content="{robots}">
{f'<link rel="canonical" href="{canon}">' if canon else ''}
<meta property="og:type" content="website">
<meta property="og:site_name" content="HypeApp">
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{html.escape(desc)}">
{f'<meta property="og:url" content="{canon}">' if canon else ''}
<meta property="og:image" content="{BASE}/{(m or {}).get('img', 'og/padrao.jpg')}">
<meta property="og:locale" content="pt_BR">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#EFEFEF">
<link rel="preload" href="{A('assets/fonts/inter-latin-wght-normal.woff2')}" as="font" type="font/woff2" crossorigin>
<link rel="icon" href="{A('favicon.ico')}" sizes="32x32">
<link rel="icon" href="{A('favicon.svg')}" type="image/svg+xml">
<link rel="apple-touch-icon" href="{A('apple-touch-icon.png')}">
<link rel="manifest" href="{A('site.webmanifest')}">
<link rel="stylesheet" href="{A('assets/site.css')}?v={VER['site.css']}">
{ld}'''
    if url == '/app' and WEB:
        pass
    inner = f'<a class="sr-only" href="#conteudo">Pular para o conteúdo</a>\n{bar}\n{body}\n<script src="{A("assets/site.js")}?v={VER['site.js']}" defer></script>'
    is_root = url == '/'
    if is_root and not WEB:
        # A página principal da prévia é publicada sem esqueleto (a publicação acrescenta doctype, head e body).
        return head + '\n' + inner
    return f'<!doctype html>\n<html lang="pt-BR">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n{head}\n</head>\n<body>\n{inner}\n</body>\n</html>\n'

# ---------- Netlify: redirecionamentos e cabeçalhos (só na versão --web) ----------
# 301 = definitivo · 302 = temporário (rota suspensa ou que ainda vai existir).
REDIRECTS = '''# Domínio canônico (também marcar www.hypeapp.com.br como domínio principal no Netlify)
https://hypeapp.com.br/*        https://www.hypeapp.com.br/:splat   301!
http://hypeapp.com.br/*         https://www.hypeapp.com.br/:splat   301!

# Link curto para as lojas (a página escolhe a loja pelo aparelho)
/app                /app/index.html            200

# Rotas suspensas pela ordem de 26/10 (temporário: podem voltar)
/interesse/criadores/*  /baixar/               302
/interesse/marcas/*     /contato/marcas/       302
/interesse/*            /                      302
/pre-cadastro/*         /                      302

# Rotas do sitemap completo que ainda não estão no ar (temporário)
/ajuda/*            /perguntas-frequentes/     302
/como-funciona/     /criadores/#como-funciona  302
/funcionalidades/   /marcas/#funcionalidades   302
/contato/parcerias/ /contato/                  302
/direitos-sobre-dados/*  /privacidade/#direitos  302
/mapa-do-site/      /                          302

# Nomes alternativos que as pessoas digitam
/criador/*          /criadores/                301
/creators/*         /criadores/                301
/marca/*            /marcas/                   301
/agencias/*         /marcas/#agencias          301
/download/*         /baixar/                   301
/login/*            /entrar/                   301
/faq/*              /perguntas-frequentes/     301
/politica-de-privacidade/*  /privacidade/      301
/termos-de-uso/*    /termos/                   301
/excluir-conta/*    /exclusao-de-conta/        301

# Endereços do site antigo (omnes-tech/hype-site): política e termos acima; demais páginas
/murais-campanhas/*  /criadores/              301
/influenciadores/*   /criadores/              301
'''

HEADERS = '''/*
  X-Content-Type-Options: nosniff
  X-Frame-Options: DENY
  Referrer-Policy: strict-origin-when-cross-origin
  Permissions-Policy: camera=(), microphone=(), geolocation=(), interest-cohort=()
  Content-Security-Policy: default-src 'self'; img-src 'self' data:; style-src 'self' 'unsafe-inline'; script-src 'self' https://static.cloudflareinsights.com; font-src 'self'; connect-src 'self' https://cloudflareinsights.com; form-action 'self'; frame-ancestors 'none'; base-uri 'self'; object-src 'none'

/assets/fonts/*
  Cache-Control: public, max-age=31536000, immutable

/assets/telas/*
  Cache-Control: public, max-age=604800

/og/*
  Cache-Control: public, max-age=86400
'''

def out_path(url):
    if url == '/':
        return 'index.html'
    if url == '/404':
        return '404.html'
    return url.strip('/') + '/index.html'

def main():
    if os.path.exists(OUT):
        shutil.rmtree(OUT)
    os.makedirs(os.path.join(OUT, 'assets'))
    for f in ('site.css', 'site.js', 'logo-hypeapp.svg'):
        shutil.copy(os.path.join(HERE, 'assets', f), os.path.join(OUT, 'assets', f))
    shutil.copytree(os.path.join(HERE, 'assets', 'fonts'), os.path.join(OUT, 'assets', 'fonts'))
    shutil.copytree(os.path.join(HERE, 'assets', 'hero'), os.path.join(OUT, 'assets', 'hero'))
    shutil.copytree(os.path.join(HERE, 'assets', 'como-funciona'), os.path.join(OUT, 'assets', 'como-funciona'))
    shutil.copytree(os.path.join(HERE, 'assets', 'carreira'), os.path.join(OUT, 'assets', 'carreira'))
    shutil.copytree(os.path.join(HERE, 'assets', 'menu'), os.path.join(OUT, 'assets', 'menu'))
    os.makedirs(os.path.join(OUT, 'assets', 'blog'))
    for _p in POSTS:
        shutil.copy(os.path.join(HERE, 'assets', 'blog', _p['capa']), os.path.join(OUT, 'assets', 'blog', _p['capa']))
    # Ícones, manifest e imagens sociais ficam na raiz do site (gerados por make_media.py)
    for f in os.listdir(os.path.join(HERE, 'static')):
        src = os.path.join(HERE, 'static', f)
        (shutil.copytree if os.path.isdir(src) else shutil.copy)(src, os.path.join(OUT, f))
    os.makedirs(os.path.join(OUT, 'assets', 'telas'))
    used = set()
    for url, fn, kind in PAGES:
        if url == '/404' and not WEB:
            # Na prévia o 404 fica em /404/index.html para os links relativos funcionarem
            path = '404/index.html'
            L_url = '/404/'
        else:
            path = out_path(url)
        p = os.path.join(OUT, path)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        page = build_page(url if not (url == '/404' and not WEB) else '/404', fn, kind)
        open(p, 'w', encoding='utf-8').write(page)
        used.update(re.findall(r'assets/telas/([\w-]+\.webp)', page))
    for f in sorted(used):  # só as telas usadas nas páginas
        shutil.copy(os.path.join(HERE, 'assets', 'telas', f), os.path.join(OUT, 'assets', 'telas', f))
    if WEB:
        seo = os.path.join(HERE, '..', 'seo', 'out')
        for f in ('robots.txt', 'sitemap.xml', 'llms.txt'):
            shutil.copy(os.path.join(seo, f), os.path.join(OUT, f))
        if BLOG_ON:  # o blog entra no sitemap só com artigo publicado
            sm = os.path.join(OUT, 'sitemap.xml'); x = open(sm, encoding='utf-8').read()
            urls = ['/blog/'] + ['/blog/' + _p['slug'] + '/' for _p in POSTS]
            x = x.replace('</urlset>', ''.join(f'  <url><loc>{BASE}{u}</loc></url>\n' for u in urls) + '</urlset>')
            open(sm, 'w', encoding='utf-8').write(x)
        open(os.path.join(OUT, '_redirects'), 'w').write(REDIRECTS)
        open(os.path.join(OUT, '_headers'), 'w').write(HEADERS)
    if not WEB:  # simulador de iPhone (só na prévia)
        names = {r['url']: r['pagina'] for r in R}; names.update({u: v['pagina'] for u, v in POST_META.items()})
        names.update({'/': 'Início', '/404': 'Página 404', '/app': 'Link para as lojas', '/blog/': 'Blog'})
        lista = []
        for url, _fn, _k in PAGES:
            src = '../index.html' if url == '/' else '../' + url.strip('/') + '/index.html'
            lista.append({'name': names.get(url, url), 'src': src})
        sim = open(os.path.join(HERE, 'tools', 'iphone.html'), encoding='utf-8').read().replace('{{PAGES_JSON}}', json.dumps(lista, ensure_ascii=False))
        os.makedirs(os.path.join(OUT, 'iphone'), exist_ok=True)
        open(os.path.join(OUT, 'iphone', 'index.html'), 'w', encoding='utf-8').write(sim)
    print('ok', OUT, len(PAGES), 'páginas')
    if WEB:  # checagem de lançamento: nada entre colchetes pode ir ao ar
        ph = {}
        for root, _, files in os.walk(OUT):
            for fn in files:
                if fn.endswith('.html'):
                    for t in re.findall(r'<span class="ph">(\[[^<]*\])</span>', open(os.path.join(root, fn), encoding='utf-8').read()):
                        ph.setdefault(t, set()).add(os.path.relpath(os.path.join(root, fn), OUT))
        if ph:
            print(f'ATENÇÃO: {len(ph)} textos entre colchetes ainda no site. Não publicar em produção antes de resolver:')
            for t, fs in sorted(ph.items()):
                print(f'  {t}  ({len(fs)} página{"s" if len(fs) > 1 else ""})')

if __name__ == '__main__':
    main()
