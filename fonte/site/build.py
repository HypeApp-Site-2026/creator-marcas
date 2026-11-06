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
    'painel': 'https://backoffice-v2.hypeapp.com.br/sign-in',   # backoffice das marcas (Lucas, 06/11: direto no endereço do painel; /backoffice do www redireciona para lá)
    'preview': not WEB,      # faixa "Prévia" + noindex
    # Google Tag Manager: ID do contêiner (GTM-XXXXXXX). Vazio = nenhum script de análise e nenhum aviso de cookies.
    # O GTM só é carregado depois que a pessoa aceita os cookies de medição (Consent Mode v2, modo básico).
    'gtm': os.environ.get('HH_GTM', 'GTM-KKF9JKK9'),   # contêiner "www.hypeapp.com.br" (04/11); GA4 G-3WD7HYT50C fica dentro do GTM
}
CFG['ga4'] = os.environ.get('HH_GA4', 'G-3WD7HYT50C')   # tag do Google (gtag.js) direto no site (06/11); só carrega com o aceite de medição
if CFG['ga4'] and not re.fullmatch(r'G-[A-Z0-9]{6,12}', CFG['ga4']):
    raise SystemExit('CFG ga4 inválido: use o formato G-XXXXXXX')
CFG['ios_pt'] = os.environ.get('HH_IOS_PT', '')   # token do provedor no App Store Connect (links de campanha da App Store); vazio = sem
if CFG['ios_pt'] and not re.fullmatch(r'[0-9]{4,12}', CFG['ios_pt']):
    raise SystemExit('CFG ios_pt inválido')
CFG['clarity'] = os.environ.get('HH_CLARITY', 'z8cuz3l4nn')   # Microsoft Clarity (04/11); só carrega com o aceite de medição
if CFG['clarity'] and not re.fullmatch(r'[a-z0-9]{6,16}', CFG['clarity']):
    raise SystemExit('CFG clarity inválido')
if CFG['gtm'] and not re.fullmatch(r'GTM-[A-Z0-9]{4,12}', CFG['gtm']):
    raise SystemExit('CFG gtm inválido: use o formato GTM-XXXXXXX')
ANALYTICS = WEB and bool(CFG['gtm'] or CFG['ga4'])
META = {r['url']: r for r in R}
PAINEL_URL = f"<span>{CFG['painel'].replace('https://', '').split('/sign-')[0]}</span>" if CFG['painel'] else ''

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

def rev(s):
    """Textos que estavam em rascunho. Aprovados em 04/11 (textos de produto, políticas e regras): saem sem marcação.
    Para marcar um texto novo como rascunho, use rascunho(s)."""
    return s

def rascunho(s):
    """Texto em rascunho (aguarda o ok de quem cuida do tema): marcado em amarelo só na prévia."""
    return s if WEB else f'<span class="rv" title="Rascunho: aguarda revisão">{s}</span>'

PIX_TXT = ('O valor entra como "A liberar" e fica disponível 30 dias depois do encerramento da campanha. A partir daí você saca via PIX, '
           'sem taxa e sem valor máximo; o mínimo é R$ 1,00. O saque é processado em até 2 horas úteis, e a chave PIX precisa estar no seu nome, com o mesmo CPF da conta.')
CURADORIA_TXT = rev('Os creators se inscrevem pelo mural da campanha. No self-service, a marca escolhe quem participa e pode filtrar por rede, nicho, estado, '
                    'gênero, seguidores, engajamento e proximidade. Na campanha gerenciada, quem seleciona e indica os nomes é a curadoria da Você no Hype.')
METRICAS_TXT = rev('Por campanha: alcance, visualizações, engajamento médio, interações (incluindo salvamentos), cliques e conteúdos no ar, com a divisão por rede '
                   'e os creators com mais visualizações. Por publicação: alcance, curtidas e comentários.')
AGENCIAS_TXT = rev('Sim. Cada marca tem configurações próprias (marca, empresa e equipe), e a pessoa alterna entre as marcas pelo seletor no topo do menu. A equipe é convidada por marca.')
COMUNIDADE_TXT = rev('Feed, grupos e lives com outros creators dentro do app. A comunidade tem tolerância zero a conteúdo censurável e comportamento abusivo: '
                     'qualquer publicação, comentário ou mensagem pode ser denunciada pelo próprio app, e você também pode bloquear outro usuário.')

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
    # telas do painel de novembro/2026 (pacote hypeapp-backoffice-marcas)
    'bo-n01': (45.1, 79.9), 'bo-n02': (33.9, 51), 'bo-n03a': (32.1, 35.9), 'bo-n03b': (30.7, 88),
    'bo-n04': (58.2, 46.8), 'bo-n05': (67.6, 94), 'bo-n06': (57, 50.8), 'bo-n07': (20.9, 58.3),
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
        w, h = (600, 1298) if kind == 'phone' else (1600, 771)
        hp = CURSOR_HOT.get(code) if kind == 'web' else None
        imgs += (f'<img src="{tela(A, code)}" alt="Tela do {"app" if kind == "phone" else "painel"}: {t}" width="{w}" height="{h}" data-i="{i}"'
                 + (f' data-hot="{hp[0]},{hp[1]}"' if hp else '') + ''
                 f'{" class=\"on\"" if on else ""} loading="{"eager" if on else "lazy"}"{" fetchpriority=\"high\"" if on and sid == "painel" else ""} decoding="async">')
    if kind == 'phone':
        dev = f'<div class="dev-phone"><div class="dev-screen" id="{sid}-tela" aria-live="polite">{imgs}</div></div>'
    else:
        dev = (f'<div class="dev-web"><div class="dev-bar"><i></i><i></i><i></i></div>'
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
            ('Comunidade', 'Grupos, feed e lives com outros creators', L('/criadores/', '#comunidade')),
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
        art = (f'<img class="mega-art mega-monitor" src="{A("assets/menu/monitor-painel.webp")}" alt="Monitor com o painel das marcas do HypeApp" width="480" height="424" loading="lazy">' if img == 'monitor' else
               f'<img class="mega-art" src="{tela(A, img)}" alt="{TELA_ALT.get(img, "Tela do HypeApp")}" width="{600 if img.startswith("app") else 1400}" height="{1298 if img.startswith("app") else 875}" loading="lazy">'
               if img else '<span class="mega-art mega-bubble" aria-hidden="true">?</span>')
        panels += (f'<div class="mega{" mega-web" if img and (img.startswith("bo") or img == "monitor") else ""}" id="{pid}" role="region" aria-label="{label}" hidden>'
                   f'<div class="mega-card"><span class="mega-label">{label}</span><ul>{lis}</ul></div>{art}</div>')
    painel = CFG['painel']
    marca_href = painel if painel else L('/entrar/', '#marcas')
    marca_sub = 'Painel das marcas · ' + painel.replace('https://', '').replace('www.', '').split('/sign-')[0] if painel else 'Painel das marcas'
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
      <div class="msub"><a href="{L('/criadores/', '#como-funciona')}">Como funciona</a><a href="{L('/criadores/', '#comunidade')}">Comunidade</a><a href="{L('/baixar/')}">Baixar o app</a></div></div>
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
    return f'''<header class="site-header wrap{' hdr-over' if cur == '/' else ''}">
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
        ('Legal', [('Documentos legais', L('/legal/')), ('Privacidade', L('/privacidade/')), ('Encarregado de dados', L('/privacidade/', '#encarregado')), ('Termos de uso', L('/termos/')), ('Cookies', L('/cookies/')), ('Regras da comunidade', L('/regras-da-comunidade/')), ('Exclusão de conta', L('/exclusao-de-conta/'))] + ([('Preferências de cookies', '#preferencias-cookies')] if ANALYTICS else [])),
    ]
    c = ''.join(f'<nav aria-label="{t}"><span class="ftr-h">{t}</span>' + ''.join(f'<a href="{h}"{_blog.SO_TESTE if n == "Blog" and "/blog/" in SO_TESTE else ""}>{n}</a>' for n, h in ls) + '</nav>' for t, ls in cols)
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
                f'<span style="display:flex;justify-content:space-between;align-items:center"><i>Prazo: {_ht.D(6)}</i><span class="go">Enviar</span></span></div>')
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

def motion_painel(A):
    I = {'camp': 'M3 11v2a1 1 0 0 0 1 1h2l5 4V6L6 10H4a1 1 0 0 0-1 1zM15 9a4 4 0 0 1 0 6',
         'cre': 'M16 20v-1a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v1M9 11a4 4 0 1 0 0-8 4 4 0 0 0 0 8M22 20v-1a4 4 0 0 0-3-3.9M16 3.1a4 4 0 0 1 0 7.8',
         'apr': 'M20 6 9 17l-5-5', 'res': 'M4 20V10M10 20V4M16 20v-8M22 20H2', 'fin': 'M3 7h18v12H3zM3 11h18M7 15h3',
         'eq': 'M12 11a4 4 0 1 0 0-8 4 4 0 0 0 0 8M4 21v-1a6 6 0 0 1 6-6h4a6 6 0 0 1 6 6v1',
         'ini': 'M4 4h7v7H4zM13 4h7v7h-7zM4 13h7v7H4zM13 13h7v7h-7z', 'live': 'M3 7h12v10H3zM15 10l6-3v10l-6-3'}
    # Menu do painel de novembro/2026: seções Workspace, Gestão de campanhas e Financeiro (sem Holds e sem Administração)
    side_items = [('Workspace', [('ini', 'Início', 2, '')]),
                  ('Gestão de campanhas', [('camp', 'Campanhas', 1, '1'), ('cre', 'Criadores', 0, ''), ('live', 'Lives', None, '')]),
                  ('Financeiro', [('fin', 'Financeiro', 3, '')])]
    side = ''.join(f'<span class="bo-sec">{sec}</span>' + ''.join(
        f'<button type="button" class="bo-nav"{" data-scene=\"%d\"" % s if s is not None else " disabled"} tabindex="-1">{ico(I[k], 16, 1.8)}{n}{f"<em>{badge}</em>" if badge else ""}</button>'
        for k, n, s, badge in its) for sec, its in side_items)
    crs = [('BA', 'Skincare', '@bianca.alves', 'Instagram|84,2 mil|4,1% eng.', ''), ('DL', 'Beleza', '@dudalima', 'Instagram|31,4 mil|3,6% eng.', 'alt'),
           ('RC', 'Skincare', '@rafacosta', 'TikTok|22,1 mil|6,8% eng.', ''), ('NR', 'Beleza', '@ninarocha', 'Instagram|58 mil|2,9% eng.', 'alt')]
    cr = ''.join(f'<div class="bo-cr r{i + 1}"><div class="hd"><span class="av {a}">{ini}</span><span class="nm"><b>{h}</b><i>1 rede social</i></span></div>'
                 f'<span class="tg">{n}</span><div class="net"><span><b>{inf.split("|")[0]}</b><i>{h}</i></span><span class="nu"><b>{inf.split("|")[1]}</b><i>{inf.split("|")[2]}</i></span></div>'
                 f'<div class="ac"><span class="vp">Ver perfil</span><span class="add">Convidar</span><span class="fav">{ico("M12 20s-7-4.4-7-10a4 4 0 0 1 7-2.6A4 4 0 0 1 19 10c0 5.6-7 10-7 10z", 14, 1.8)}</span></div></div>'
                 for i, (ini, n, h, inf, a) in enumerate(crs))
    kp = [('Alcance estimado', 'alc', '1,2 mi', 'dark'), ('Influenciadores ativos', 'vis', '12', ''), ('Engajamento médio', 'eng', '4,8%', ''), ('Conteúdos publicados', 'pub', '18', '')]
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
  <div class="bo-bar"><i></i><i></i><i></i></div>
  <div class="bo-body">
   <aside class="bo-side"><img class="lg" src="{A('assets/logo-hypeapp-branco.svg')}" alt="" width="92" height="50"><span class="bo-wsel"><span class="av">CL</span><span class="tx"><b>Casa Lume</b><i>Membro</i></span>{ico(I_DOWN, 14)}</span>{side}<span class="bo-ws"><span class="av">AS</span><span class="tx"><b>Ana Souza</b><i>Membro</i></span>{ico('M15 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4M10 17l5-5-5-5M15 12H3', 14, 1.8)}</span></aside>
   <section class="bo-main">
    <div class="bo-scene">
      <div class="bo-top"><span class="bo-h">Criadores</span><span class="bo-pill">Convidados para Verão Glow · <span id="bo-count">9 creators</span></span></div>
      <div style="display:flex;gap:8px"><span class="bo-search">{ico(I_SEARCH, 18)}<span id="bo-typed">skincare</span><span class="bo-caret"></span></span><span class="bo-round">{ico('M3 5h18l-7 8v6l-4 2v-8z', 20)}</span></div>
      <div class="bo-chips"><span class="on">Instagram</span><span>TikTok</span><span class="on">Beleza</span><span>10 mil a 100 mil</span></div>
      <div class="bo-grid4">{cr}</div>
    </div>
    <div class="bo-scene" hidden>
      <div class="bo-top"><span class="bo-h">Gerenciamento · Verão Glow</span><div class="bo-seg"><span class="on">Conteúdos</span><span>Roteiros</span></div></div>
      <div style="display:flex;gap:18px">
        <div class="bo-video r1"><div><span>{ico('M8 5v14l11-7z', 24, fill=True)}</span></div></div>
        <div class="bo-panel r2">
          <span class="bo-who"><span class="av">C1</span><span style="display:flex;flex-direction:column"><b style="font-size:18px;font-weight:600">@bianca.alves</b><span style="font-size:14px">Reels · Skincare Pro</span></span><span class="bo-ok show">Aprovado</span></span>
          <div class="bo-kv"><span><span>Roteiro</span><b>Aprovado</b></span><span><span>Versão do conteúdo</span><b>2 de 2</b></span><span><span>Prazo de publicação</span><b>{_ht.D(6)}</b></span></div>
          <span style="font-size:15px">Ajuste feito: produto aparece nos primeiros segundos e o cupom está na legenda.</span>
          <div class="bo-acts"><span>Pedir ajuste</span><span class="ink press">Aprovar conteúdo</span></div>
        </div>
      </div>
    </div>
    <div class="bo-scene" hidden>
      <div class="bo-top"><span class="bo-h">Métricas no workspace</span><span class="bo-pill" style="height:40px">Campanhas</span></div>
      <div class="bo-grid4">{kps}</div>
      <div class="bo-chart r3"><span style="display:flex;justify-content:space-between;font-size:16px;font-weight:600"><span>Alcance por semana</span><span style="font-size:14px;font-weight:500">mil pessoas</span></span><div class="bo-bars">{bars}</div><div class="bo-lbls">{lbls}</div></div>
    </div>
    <div class="bo-scene" hidden>
      <span class="bo-h">Financeiro</span>
      <div style="display:flex;gap:14px">
        <div class="bo-fin dark r1"><span style="font-size:14px">Saldo disponível</span><b id="bo-saldo">R$ 10.400</b><span style="font-size:14px;padding-top:6px">Reservado para pagamentos de creators</span></div>
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
# Texto alternativo das telas usadas fora das vitrines (hero e menu)
TELA_ALT = {
    'bo-C1': 'Tela do painel das marcas: dashboard com pendências e métricas',
    'bo-C2': 'Tela do painel das marcas: lista de campanhas',
    'bo-E1': 'Tela do painel das marcas: catálogo de creators',
    'bo-n01': 'Tela do painel das marcas: início com tarefas e aprovações por campanha e métricas do workspace',
    'bo-n02': 'Tela do painel das marcas: lista de campanhas com progresso de publicação',
    'bo-n04': 'Tela do painel das marcas: catálogo de creators com as redes de cada um',
    'app-D1': 'Tela do app para creators: descobrir campanhas',
    'app-E4': 'Tela do app para creators: campanha em andamento com ganho, data de publicação e entregas',
    'app-G2': 'Tela do app para creators: carteira com saldo',
    'app-F1': 'Tela do app para creators: feed da comunidade com a dica de outra creator sobre gravar com luz natural',
    'app-F2': 'Tela do app para creators: lives da comunidade, uma ao vivo e outra em breve',
    'app-F3c': 'Tela do app para creators: grupos da comunidade, como Creators de Beleza',
}
# ---------- Hero da home com rolagem (04/11) ----------
# Palco fixo de ~300svh: APLICATIVO (iPhone) passa para PLATAFORMA (MacBook, com a tampa abrindo) num movimento só.
# Todo o texto sai daqui, no HTML. O site.js só move e revela (transform e opacity); sem JavaScript ou com
# prefers-reduced-motion, as cenas ficam empilhadas e legíveis. As máscaras por palavra e por letra já saem do build.
HX_TELAS = {
    'app': ('assets/hero/tela-app.webp', 'Tela do app HypeApp no iPhone: Campanhas, na aba Ativas, com as campanhas de exemplo Verão Glow e Run Club SP, o próximo passo e o prazo de cada uma'),
    'painel': ('assets/hero/tela-painel.webp', 'Tela do painel HypeApp no MacBook: Campanhas, com as abas Todas, Ativas, Rascunhos e Finalizadas e cartões de exemplo com o progresso de publicação, o alcance e as pendências'),
}

def _img_wh(rel):
    from PIL import Image as _Im
    with _Im.open(os.path.join(HERE, rel)) as im:
        return im.size

def hx_palavras(txt, i0=0):
    """Cada palavra numa máscara (overflow hidden). O texto continua igual: os espaços ficam entre as máscaras."""
    out = [f'<span class="hx-m"><span class="hx-w" style="--i:{i0 + k}">{w}</span></span>' for k, w in enumerate(txt.split(' '))]
    return ' '.join(out), i0 + len(out)

def hx_gigante(word):
    """Palavra decorativa (aria-hidden), letra a letra. --k = largura em em (Inter 600, -0,05em) para caber na tela."""
    k = {'APLICATIVO': 5.46, 'PLATAFORMA': 6.31}[word]
    letras = ''.join(f'<span class="hx-ch"><span style="--i:{i}">{c}</span></span>' for i, c in enumerate(word))
    return f'<span class="hx-word" aria-hidden="true" style="--k:{k}">{letras}</span>'

def hx_lista(itens, label):
    li = ''.join(f'<li style="--i:{i}"><span class="hx-li">{t}</span></li>' for i, t in enumerate(itens))
    return f'<ul class="hx-list" aria-label="{label}">{li}</ul>'

import hero_telas as _ht
import carteira_viva as _cv

# Teclado do MacBook Pro 13" (Touch Bar) em layout ABNT/US de 6 linhas, cada linha somando 14,5 unidades de tecla.
_MB_LINHAS = [
    [('esc', 1.5), ('_tb', 12), ('_id', 1)],
    [(c, 1) for c in '`1234567890-='] + [('delete', 1.5)],
    [('tab', 1.5)] + [(c, 1) for c in 'QWERTYUIOP[]'] + [('\\', 1)],
    [('caps lock', 1.8)] + [(c, 1) for c in "ASDFGHJKL;'"] + [('return', 1.7)],
    [('shift', 2.3)] + [(c, 1) for c in 'ZXCVBNM,./'] + [('shift', 2.2)],
    [('fn', 1), ('control', 1), ('option', 1), ('command', 1.25), ('', 5), ('command', 1.25), ('option', 1), ('_setas', 3)],
]

def mb_teclado():
    """Teclado desenhado tecla a tecla (decorativo, aria-hidden no pai)."""
    linhas = []
    for li in _MB_LINHAS:
        teclas = []
        for t, w in li:
            if t == '_tb':
                teclas.append(f'<i class="mb-tb" style="flex:{w}"><b></b><b></b><b></b><b></b></i>')
            elif t == '_id':
                teclas.append(f'<i class="mb-k mb-tid" style="flex:{w}"></i>')
            elif t == '_setas':
                teclas.append(f'<i class="mb-arr" style="flex:{w}"><i class="mb-k"></i><i class="mb-ud"><i class="mb-k"></i><i class="mb-k"></i></i><i class="mb-k"></i></i>')
            else:
                cls = 'mb-k mb-km' if len(t) > 1 else 'mb-k'
                teclas.append(f'<i class="{cls}" style="flex:{w}">{html.escape(t)}</i>')
        linhas.append('<i class="mb-row">' + ''.join(teclas) + '</i>')
    return '<div class="mb-kb">' + ''.join(linhas) + '</div>'

def hero_scroll(L, A):
    """Sem tela de abertura: a página já abre na cena APLICATIVO. O H1 é um só, com uma frase em cada cena
    (linha 1 sobre o celular, linha 2 sobre o notebook); as duas ficam no mesmo elemento para o texto do H1 não mudar."""
    seta = ico('m6 9 6 6 6-6', 18)
    h1a, n = hx_palavras('O app de quem cria conteúdo.')
    h1b, n = hx_palavras('O painel de quem contrata.')
    capa, _ = hx_palavras('Sua carreira de creator, mais organizada.')
    capb, _ = hx_palavras('Sua campanha, do início ao resultado.')
    (sa, alt_a), (sb, alt_b) = HX_TELAS['app'], HX_TELAS['painel']
    wa, ha = _img_wh(sa)
    wb, hb = _img_wh(sb)
    ip_btns = ''.join(f'<span class="ip-btn ip-{k}"></span>' for k in ('act', 'vu', 'vd', 'pw'))
    return f'''<section class="hx" aria-labelledby="hero-t" data-hx>
  <div class="hx-pin">
    <h1 id="hero-t" class="hx-h1"><span class="hx-l hx-l1">{h1a}</span> <span class="hx-l hx-l2">{h1b}</span></h1>
    <div class="hx-sc hx-app" data-sc="0">
      {hx_gigante('APLICATIVO')}
      <figure class="hx-dev hx-iphone"><div class="ip" data-dev><div class="ip-body"><span class="ip-btns" aria-hidden="true">{ip_btns}</span>
        <div class="ip-bez"><div class="ip-scr"><img src="{A(sa)}" alt="{alt_a}" width="{wa}" height="{ha}" fetchpriority="high" decoding="async">{_ht.tela_app(A)}<span class="ip-di" aria-hidden="true"></span><span class="hx-glare" aria-hidden="true"></span></div></div>
      </div></div></figure>
      <div class="hx-copy">
        <h2 class="hx-cap">{capa}</h2>
        {hx_lista(['Campanhas com marcas', 'Entregas e aprovações', 'Recebimentos no app'], 'O que o app organiza')}
      </div>
    </div>
    <div class="hx-sc hx-plat" data-sc="1">
      {hx_gigante('PLATAFORMA')}
      <figure class="hx-dev hx-mac"><div class="mb" data-dev>
        <div class="mb-lid" data-lid><span class="mb-back" aria-hidden="true"></span><div class="mb-bez"><span class="mb-cam" aria-hidden="true"></span>
          <div class="mb-scr"><img src="{A(sb)}" srcset="{A(sb.replace('.webp', '-800.webp'))} 800w, {A(sb)} 1600w" sizes="(max-width: 760px) 280px, 660px" alt="{alt_b}" width="{wb}" height="{hb}" loading="lazy" decoding="async">{_ht.tela_painel(A, A('assets/logo-hypeapp-branco.svg'))}<span class="mb-off" aria-hidden="true" data-off></span><span class="mb-sweep" aria-hidden="true" data-sweep></span><span class="hx-glare" aria-hidden="true"></span></div>
          <span class="mb-name" aria-hidden="true">MacBook Pro</span></div></div>
        <div class="mb-base" aria-hidden="true"><i class="mb-shadow"></i><div class="mb-deck"><i class="mb-spk mb-spk-l"></i>{mb_teclado()}<i class="mb-spk mb-spk-r"></i><i class="mb-pad"></i></div><i class="mb-lip"><i></i></i></div>
      </div></figure>
      <div class="hx-copy">
        <h2 class="hx-cap">{capb}</h2>
        {hx_lista(['Seleção de creators', 'Conteúdos e aprovações', 'Resultados em um só painel'], 'O que o painel reúne')}
      </div>
    </div>
    <span class="hx-cue hx-cue1" aria-hidden="true">Role para explorar {seta}</span>
    <span class="hx-cue hx-cue2" aria-hidden="true">Continue explorando {seta}</span>
  </div>
</section>'''

COMO_FUNCIONA_C = [
    ('01 · Seu perfil', 'Mostre quem você é', 'Crie sua conta e conecte suas redes.', 'Ilustração: creator segurando o celular, com o cartão de perfil ao lado'),
    ('02 · Oportunidades', 'Encontre sua próxima conexão', 'Explore campanhas e envie sua inscrição.', 'Ilustração: celular com a lista de campanhas e o botão Quero participar'),
    ('03 · Entregas', 'Sua ideia ganha forma', 'Envie conteúdo e acompanhe as aprovações.', 'Ilustração: dedo tocando o botão de envio, com o selo de aprovação'),
    ('04 · Carteira', 'Acompanhe seu saldo', 'Solicite o saque quando o valor for liberado.', 'Ilustração: celular com a carteira, saldo oculto e o botão Solicitar saque'),
]

COMO_FUNCIONA_M = [
    ('01 · Comercial', 'Vamos falar sobre sua marca', 'Conte seus objetivos e conheça as condições de acesso.', 'Ilustração: profissional sorrindo com headset, atendendo pelo notebook'),
    ('02 · Campanha', 'Sua campanha começa aqui', 'Defina briefing, remuneração, critérios e fases.', 'Monitor com a campanha Lançamento Verão aberta no painel: visão geral e etapas'),
    ('03 · Aprovações', 'Escolha creators. Aprove entregas.', 'Receba inscrições e revise roteiros e conteúdos.', 'Notebook com o painel: Precisa da sua ação, com inscrições novas para triar'),
    ('04 · Resultados', 'Acompanhe cada resultado', 'Veja publicações, métricas e pagamentos no painel.', 'Monitor com o Início do painel: campanhas, tarefas e aprovações e métricas do workspace'),
]

def como_funciona(A, pid, tab, label, items, media, hidden=False, img_prefix='marca'):
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
            base = f'assets/como-funciona/{img_prefix}{n}'
            m = (f'<img class="cf-anim cf-anim-{n}" src="{A(base + ".webp")}" srcset="{A(base + "-640.webp")} 640w, {A(base + ".webp")} 960w" '
                 f'sizes="(max-width: 760px) 300px, 345px" alt="{alt}" width="720" height="720" loading="lazy" decoding="async">')
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
      <div class="mz-b mz-phone" style="{pos('phone')}"><img class="mz-fill" src="{A('assets/carreira/celular-proximo-passo.webp')}" alt="Celular com a tela Início do HypeApp: campanhas em destaque e o próximo passo, Enviar roteiro" width="900" height="1169" loading="lazy" decoding="async"></div>
      <div class="mz-b mz-receb" style="{pos('receb')}"><div class="mz-in">
        <div class="mz-rh"><b>Recebimentos</b>{wallet}</div>
        <div class="mz-row"><i class="mz-dot"></i><span>Em campanha</span><i class="mz-bar"><i style="width:76%"></i></i><i class="mz-dash"></i></div>
        <div class="mz-row"><i class="mz-dot"></i><span>A liberar</span><i class="mz-bar"><i style="width:58%"></i></i><i class="mz-dash"></i></div>
      </div></div>
      <div class="mz-b mz-entrega" style="{pos('entrega')}"><div class="mz-in">
        <span class="mz-cal">{cal}</span><b class="mz-et">Próxima entrega</b><span class="mz-es">Envio de roteiro</span><span class="mz-pill"><i></i>Em andamento</span>
      </div></div>
      <div class="mz-b mz-char" style="{pos('char')}"><img class="mz-fill" src="{A('assets/carreira/creator-hijab.webp')}" alt="Ilustração: creator sentada, sorrindo enquanto usa o HypeApp no celular" width="1000" height="1000" loading="lazy" decoding="async"></div>
    </div>
    <figcaption class="gc-cap">Interface e dados ilustrativos.</figcaption>
  </figure>
</section>'''

def tiktok_shop(L, A, url):
    """Selo de agência parceira do TikTok Shop (logo oficial, sem alteração, sempre sobre fundo branco).
    Aparece em todas as páginas, logo acima do rodapé (decisão de 04/11)."""
    onde = 'rodape'
    t, d = ('Agência parceira do TikTok Shop', 'A Você no Hype, que desenvolve o HypeApp, é agência parceira do TikTok Shop. Se a sua marca vende ou quer vender no TikTok Shop, fale com nosso time.')
    cta = '' if url.startswith('/contato/marcas/') else f'<a class="btn btn-ink" href="{L("/contato/marcas/")}">Falar com nosso time</a>'
    return (f'<div class="wrap tts-band"><section class="tts" aria-labelledby="tts-{onde}"><img src="{A("assets/parceiros/tiktok-shop-partner.webp")}" alt="TikTok Shop Partner" width="280" height="79" loading="lazy" decoding="async">'
            f'<div class="stack" style="gap:6px;flex:1 1 320px"><h2 id="tts-{onde}" class="h4">{t}</h2><p style="margin:0;font-size:16px">{d}</p></div>{cta}</section></div>')

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
{hero_scroll(L, A)}
<div class="wrap home-body">

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
  {como_funciona(A, 'painel-c', 'tab-c', 'Passos para creators', COMO_FUNCIONA_C, 'img', img_prefix='creator')}
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
</section>
</div>'''

CANDIDATURA = [
    ('app-D1', 'Encontre a campanha', 'Em Descobrir, filtre o mural por nicho e formato e veja as campanhas em destaque.', 'Descobrir'),
    ('app-E1', 'Leia o briefing', 'Confira o que a marca pede, a remuneração, as entregas, os prazos e os critérios antes de decidir.', 'Quero participar'),
    ('app-E2', 'Escolha o perfil e envie', 'Selecione com quais redes quer participar e, quando a campanha pedir, informe sua proposta de valor.', 'Enviar inscrição'),
    ('app-D3', 'Acompanhe a análise', 'Na aba Minhas inscrições você vê quando sua inscrição está em análise.', 'Inscrição em análise'),
    ('app-E3', 'Receba a resposta', 'Se for pré-selecionado, a marca envia o convite com as condições. Você aceita ou recusa pelo app.', 'Aceitar convite'),
]

# Jornada do creator em carrossel (04/11, versão 4 do quadro de propostas): substitui "Seu próximo passo" e "Como se candidatar".
# Só telas e textos do que o app faz hoje (levantamento de funcionalidades, app 2.0.28).
JORNADA = [
    ('app-B4', 'Monte seu perfil', 'Cadastro em 5 passos: telefone, seus valores por formato, dados e nichos, e endereço. Depois, conecte Instagram, TikTok e YouTube.'),
    ('app-D1', 'Encontre campanhas', 'No mural, busque e filtre por nicho. As campanhas em destaque aparecem primeiro.'),
    ('app-E1', 'Veja tudo antes de entrar', 'Ganho, duração, entregas, regras e arquivos da marca, na página da campanha.'),
    ('app-E2', 'Inscreva-se', 'Escolha com quais perfis quer participar e, quando a campanha pedir, proponha o seu valor.'),
    ('app-D3', 'Acompanhe a análise', 'Em Minhas inscrições: inscrição enviada, análise da marca e resultado. A seleção é da marca ou da curadoria da Você no Hype.'),
    ('app-E3', 'Aceite e comece', 'Selecionado ou convidado, você vê as condições e o prazo e aceita pelo app. O contrato chega por e-mail.'),
    ('app-E8', 'Envie roteiro e conteúdo', 'Cada entrega passa pela aprovação da marca. O próximo passo e o prazo ficam sempre à vista.'),
    ('app-G2', 'Receba na carteira', 'Depois da publicação, o valor entra como "A liberar" e fica disponível 30 dias após o encerramento, para saque via PIX.'),
]
JORNADA_ANTES = 5   # passos 1 a 5: antes do sim; 6 a 8: depois

# "Cresça além de uma campanha" (04/11): igual ao modelo B do canvas (título central e telas em leque),
# girando como o carrossel de telas, sem texto por tela.
CRESCA = [
    ('app-G1', 'Perfil com redes, nichos e campanhas concluídas'),
    ('app-G5', 'Avaliações recebidas das marcas'),
    ('app-F1', 'Feed da comunidade com dicas de outros creators'),
    ('app-G6', 'Atualizar os valores por formato de conteúdo'),
    ('app-F2', 'Lives da comunidade'),
    ('app-F5', 'Grupo da comunidade'),
]

def cresca_carrossel(A):
    n = len(CRESCA)
    slides = ''.join(
        f'<button type="button" class="jc-it" data-i="{i}" data-d="{i if i <= n // 2 else i - n}" aria-label="Tela {i + 1} de {n}: {html.escape(t)}" tabindex="-1">'
        f'<img src="{tela(A, c)}" alt="" width="600" height="1298" loading="lazy" decoding="async"></button>'
        for i, (c, t) in enumerate(CRESCA))
    dots = ''.join(f'<button type="button" class="jc-dot" data-i="{i}" aria-label="Ir para a tela {i + 1}"></button>' for i in range(n))
    return f'''<section id="crescer" class="jc jc-b" aria-labelledby="cs-h" data-jc>
  <div class="jcb-head">
    <h2 id="cs-h" class="jcb-h">Cresça além de uma campanha</h2>
    <p class="jcb-sub">Perfil que vira vitrine, avaliações das marcas e uma comunidade de creators.</p>
  </div>
  <div class="jc-stage" role="region" aria-roledescription="carrossel" aria-label="Telas do app para crescer como creator" tabindex="0">{slides}</div>
  <div class="jc-ctrl">
    <button type="button" class="jc-arr" data-prev aria-label="Tela anterior">{ico('m15 6-6 6 6 6', 22)}</button>
    <div class="jc-dots">{dots}</div>
    <button type="button" class="jc-arr jc-arr-n" data-next aria-label="Próxima tela">{ico('m9 6 6 6-6 6', 22)}</button>
    <button type="button" class="jc-pp" data-pp aria-label="Pausar a rotação">Pausar</button>
  </div>
</section>'''

def jornada_carrossel(L, A):
    """Carrossel 3D das telas do app: gira sozinho com a seção na tela; título e explicação embaixo.
    Sem JavaScript (ou com movimento reduzido), mostra a primeira tela e a lista com os 8 passos."""
    n = len(JORNADA)
    slides = ''.join(
        f'<button type="button" class="jc-it" data-i="{i}" data-d="{i if i <= n // 2 else i - n}" aria-label="Passo {i + 1} de {n}: {html.escape(t)}" tabindex="-1">'
        f'<img src="{tela(A, c)}" alt="" width="600" height="1298" loading="lazy" decoding="async"></button>'
        for i, (c, t, d) in enumerate(JORNADA))
    passos = ''.join(f'<li class="jc-tx{" on" if i == 0 else ""}" data-i="{i}"><span class="jc-n">{i + 1:02d} / {n:02d}</span>'
                     f'<h3 class="jc-t">{html.escape(t)}</h3><p class="jc-d">{html.escape(d)}</p></li>'
                     for i, (c, t, d) in enumerate(JORNADA))
    dots = ''.join(f'<button type="button" class="jc-dot" data-i="{i}" aria-label="Ir para o passo {i + 1}"></button>' for i in range(n))
    seta = lambda d: ico(d, 22)
    return f'''<section class="jc" id="como-funciona" aria-labelledby="jc-h" data-jc>
  <span id="candidatura" class="jc-anc" aria-hidden="true"></span>
  <div class="jc-box">
    <div class="jc-head">
      <span class="pd-eyebrow">Do cadastro ao saque</span>
      <h2 id="jc-h" class="pd-h">Seu próximo passo no HypeApp</h2>
      <div class="jc-fases" role="group" aria-label="Fases"><button type="button" data-ir="0" aria-pressed="true">Antes do sim<span class="jc-fn"> · 1 a {JORNADA_ANTES}</span></button><button type="button" data-ir="{JORNADA_ANTES}" aria-pressed="false">Depois do sim<span class="jc-fn"> · {JORNADA_ANTES + 1} a {n}</span></button></div>
    </div>
    <div class="jc-stage" role="region" aria-roledescription="carrossel" aria-label="Telas do app, passo a passo" tabindex="0">{slides}</div>
    <div class="jc-ctrl">
      <button type="button" class="jc-arr" data-prev aria-label="Passo anterior">{seta('m15 6-6 6 6 6')}</button>
      <div class="jc-dots">{dots}</div>
      <button type="button" class="jc-arr jc-arr-n" data-next aria-label="Próximo passo">{seta('m9 6 6 6-6 6')}</button>
      <button type="button" class="jc-pp" data-pp aria-label="Pausar a rotação">Pausar</button>
    </div>
    <ol class="jc-txs" aria-live="polite">{passos}</ol>
    <p class="jc-note">Telas do app com dados de exemplo.</p>
  </div>
</section>'''

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
    """Página de creators em blocos (bento), versão C do quadro de propostas (04/11).
    Segue as dúvidas de quem decide se o HypeApp ajuda na carreira, misturando animação, ilustração, tela do app e selo.
    Só fatos confirmados (app 2.0.28 e decisões do Lucas); nada de números de usuários ou campanhas."""
    ck = ico('M20 6 9 17l-5-5', 20, 2.4)
    vid = lambda n, alt, cls='': (f'<video class="bt-vid {cls}" muted playsinline loop preload="none" width="720" height="720" data-vis-play '
                                  f'poster="{A(f"assets/como-funciona/cena{n}.webp")}" aria-label="{alt}"><source src="{A(f"assets/como-funciona/cena{n}.mp4")}" type="video/mp4"></video>')
    ilu = lambda f, alt, cls='': f'<img class="bt-img {cls}" src="{A(f)}" alt="{alt}" width="960" height="600" loading="lazy" decoding="async">'
    shot = lambda c: f'<img class="bt-shot" src="{tela(A, c)}" alt="{TELA_ALT.get(c, "Tela do app HypeApp")}" width="600" height="{720 if c == 'app-F3c' else 1298}" loading="lazy" decoding="async">'
    # blog: o primeiro artigo; em revisão só aparece no ambiente de teste
    post = POSTS[0] if POSTS else None
    blog = ''
    if post:
        so = _blog.SO_TESTE if _blog.so_teste(post) else ''
        blog = (f'<a class="bt bt-roxo bt-blog" href="{L("/blog/" + post["slug"] + "/")}"{so}>{ilu("assets/blog/" + post["capa"], "")}'
                f'<span class="bt-pad"><span class="bt-k">Do blog</span><b class="bt-t3">{html.escape(post["titulo"])}</b><span class="bt-lk">Ler o artigo</span></span></a>')
    faq = [('É pago para creators?', 'Não. O HypeApp é gratuito para creators: não há mensalidade nem taxa sobre o valor que você recebe das campanhas.'),
           ('Preciso de quantos seguidores?', 'Nenhum mínimo para criar a conta. Cada campanha tem critérios próprios, e o app mostra se o seu perfil atende antes de você se inscrever.'),
           ('Como e quando recebo?', PIX_TXT),
           ('Quem escolhe quem participa?', 'No self-service, a própria marca. Na campanha gerenciada, a curadoria da Você no Hype.'),
           ('Posso recusar uma campanha ou um convite?', 'Sim. Você só se inscreve nas campanhas que quiser e pode recusar convites; a marca é avisada.'),
           ('O cadastro garante campanhas?', 'Não. Cada campanha tem critérios próprios e a seleção é feita pela marca ou pela curadoria.'),
           ('Preciso emitir nota fiscal?', 'Depende da campanha e do seu cadastro como pessoa física ou jurídica. O app informa o que é exigido antes do pagamento.'),
           ('A marca pode usar meu conteúdo depois?', 'Depende do contrato da campanha, firmado entre você e a marca. Confira as condições de uso de imagem antes de aceitar.'),
           ('Como funciona a comunidade?', COMUNIDADE_TXT)]
    return f'''
<section class="bt-g bt-hero" aria-labelledby="hero-c">
  <div class="bt bt-roxo bt-h1">
    <span class="bt-pill">Para creators</span>
    <div class="stack" style="gap:20px">
      <h1 id="hero-c" class="bt-d">Sua carreira de creator, mais organizada.</h1>
      <p class="bt-lead">Campanhas com marcas, entregas, pagamento e uma comunidade de creators num app só.</p>
      <div class="row"><a class="btn btn-ink btn-lg" href="{L('/baixar/')}">Baixar o app</a><a class="btn btn-soft btn-lg" href="{L('/entrar/', '#creators')}">Já tenho conta</a></div>
    </div>
  </div>
  <div class="bt bt-hv bt-hfoto"><img class="bt-img" src="{A('assets/ilustracoes/hero-creator.webp')}" alt="Ilustração: creator sorrindo com o celular na mão e cartões de perfil e aprovação ao lado" width="934" height="1685" fetchpriority="high" decoding="async"></div>
  <div class="bt bt-hs bt-hfoto"><img class="bt-img" src="{A('assets/ilustracoes/hero-celular.webp')}" alt="Celular com a tela Campanhas do HypeApp aberta em Descobrir" width="1000" height="1000" decoding="async"></div>
  <ul class="bt bt-preto bt-selos" aria-label="Em resumo"><li>{ck}Grátis para creators</li><li>{ck}Sem mínimo de seguidores</li><li>{ck}Saque via PIX</li><li>{ck}Comunidade de creators</li><li class="bt-sub">iPhone e Android</li></ul>
</section>

<section id="para-quem" aria-labelledby="pq-h">
  <h2 id="pq-h" class="bt-h2">Isso é pra mim?</h2>
  <div class="bt-g bt-3">
    <div class="bt bt-card">{ilu('assets/ilustracoes/pq-comecando.webp', 'Ilustração: creator sorrindo com o celular e um cartão de perfil aprovado')}<div class="bt-pad"><b class="bt-t3">Está começando</b><span class="bt-p">Não existe mínimo de seguidores. Cada campanha diz os critérios dela, e o app mostra se o seu perfil atende antes de você se inscrever.</span></div></div>
    <div class="bt bt-card">{ilu('assets/ilustracoes/pq-publis.webp', 'Ilustração: mãos no celular com a campanha e briefing, roteiro e entrega marcados')}<div class="bt-pad"><b class="bt-t3">Já faz publis</b><span class="bt-p">Tire as propostas do direct. Briefing, prazos, aprovações e pagamento ficam registrados em cada campanha.</span></div></div>
    <div class="bt bt-card">{ilu('assets/ilustracoes/pq-ugc.webp', 'Ilustração: mãos posicionando um produto diante do celular no tripé, gravando')}<div class="bt-pad"><b class="bt-t3">Trabalha com UGC</b><span class="bt-p">Marque no cadastro que faz UGC e defina o seu valor para conteúdo que a marca usa nos canais dela.</span></div></div>
  </div>
</section>

<section id="como-funciona" aria-labelledby="cf-h2">
  <span id="candidatura" class="jc-anc" aria-hidden="true"></span><span id="recursos" class="jc-anc" aria-hidden="true"></span>
  <h2 id="cf-h2" class="bt-h2">Como funciona</h2>
  <div class="bt-g bt-cf">
    <div class="bt bt-branco bt-cfp">{ilu('assets/ilustracoes/cf-perfil.webp', 'Ilustração: creator sorrindo e apontando para a tela Meu perfil no celular', 'bt-sq')}<span class="bt-n">01</span><b class="bt-t2">Monte seu perfil</b><span class="bt-p">Cadastro em 5 passos, com os seus valores por formato. Depois, conecte Instagram, TikTok e YouTube.</span></div>
    <div class="bt bt-branco bt-cfp">{ilu('assets/ilustracoes/cf-campanhas.webp', 'Celular com a tela Campanhas e os botões Quero participar, sobre fundo escuro', 'bt-sq')}<span class="bt-n">02</span><b class="bt-t2">Escolha campanhas</b><span class="bt-p">Inscreva-se no mural ou aceite convites. Ganho, entregas e prazo estão escritos antes.</span></div>
    <div class="bt bt-preto bt-cf3">{ilu('assets/ilustracoes/cf-entrega.webp', 'Ilustração: creator sentado tocando em Enviar conteúdo no celular, com um selo de aprovação', 'bt-grow')}<span class="bt-n bt-n-l">03</span><b class="bt-t2">Entregue pelo app</b><span class="bt-p">Roteiro, conteúdo e publicação. A marca aprova ou pede ajuste, e o próximo passo e o prazo ficam sempre à vista.</span></div>
    <div class="bt bt-lima bt-cf4"><span class="bt-n">04</span><b class="bt-t2">Receba na carteira</b><span class="bt-p">O valor entra como "A liberar" e, depois, fica disponível para saque via PIX.</span></div>
    <div class="bt bt-media bt-cf5">{ilu('assets/ilustracoes/cf-carteira.webp', 'Celular com a Carteira: saldo oculto, Em campanha, A liberar e o botão Solicitar saque')}</div>
  </div>
</section>

<section id="dinheiro" aria-labelledby="din-h">
  <h2 id="din-h" class="bt-h2">Seu dinheiro, com regras claras</h2>
  <div class="bt-g bt-din">
    <div class="bt bt-preto bt-d1"><b class="bt-t2">Do post ao PIX</b><ol class="bt-pix"><li><b>1 · Publicou</b>A publicação é identificada.</li><li><b>2 · A liberar</b>O valor aparece na carteira.</li><li><b>3 · Disponível</b>30 dias após o encerramento da campanha.</li><li><b class="bt-lime">4 · PIX</b>Processado em até 2 horas úteis.</li></ol></div>
    <div class="bt bt-d2 bt-cwt">{_cv.carteira_viva()}</div>
    <div class="bt bt-lima bt-d3"><b class="bt-big">Sem taxa</b><span class="bt-p">no saque, a partir de R$ 1,00, com a chave PIX no seu nome e no mesmo CPF da conta.</span></div>
    <div class="bt bt-branco bt-d4"><b class="bt-t3">Como as campanhas pagam</b><ul class="bt-formas"><li><b>Valor fixo</b>o mesmo para cada creator</li><li><b>O seu preço</b>os valores do seu perfil</li><li><b>Proposta</b>você propõe; a marca aceita ou negocia</li><li><b>Permuta</b>produtos, com envio acompanhado no app</li></ul></div>
    <div class="bt bt-media bt-d5">{ilu('assets/ilustracoes/din-permuta.webp', 'Ilustração: caixa aberta com um produto, como numa permuta')}</div>
  </div>
</section>

<section id="comunidade" class="cv" aria-labelledby="com-h">
  <div class="cv-in">
    <div class="cv-copy">
      <span class="cv-pill">Comunidade</span>
      <h2 id="com-h" class="cv-h">A conversa que faltava na sua rotina.</h2>
      <p class="cv-p">Pergunte, responda e aprenda com outros creators, nos grupos, nos posts e nas lives do app.</p>
    </div>
    <div class="cv-fone" data-cvf role="img" aria-label="Celular navegando pela comunidade do HypeApp: feed, post com comentários, grupos, um grupo de creators e uma live">
      <span class="cv-sb cv-sb1" aria-hidden="true"></span><span class="cv-sb cv-sb2" aria-hidden="true"></span><span class="cv-sb cv-sb3" aria-hidden="true"></span>
      <div class="cv-tela" aria-hidden="true">
        <i class="cv-ilha"></i>
        <img class="cv-s on" data-s="feed" src="{tela(A, 'app-F1')}" alt="" width="600" height="1298" loading="lazy" decoding="async">
        <img class="cv-s" data-s="post" src="{tela(A, 'app-F4')}" alt="" width="600" height="1298" loading="lazy" decoding="async">
        <img class="cv-s" data-s="grupos" src="{tela(A, 'app-F3s')}" alt="" width="600" height="1298" loading="lazy" decoding="async">
        <img class="cv-s" data-s="grupo" src="{tela(A, 'app-F5')}" alt="" width="600" height="1298" loading="lazy" decoding="async">
        <img class="cv-s" data-s="lives" src="{tela(A, 'app-F2')}" alt="" width="600" height="1298" loading="lazy" decoding="async">
        <img class="cv-s" data-s="live" src="{tela(A, 'app-F6')}" alt="" width="600" height="1298" loading="lazy" decoding="async">
        <i class="cv-tap" data-cvtap></i>
      </div>
    </div>
    <div class="cv-chatw">
      <div class="cv-chat" data-cvchat role="img" aria-label="Exemplo de conversa no grupo de uma campanha: um creator pergunta sobre envio de produto, outros respondem e compartilham uma dica de gravação">
        <div class="cv-ch" aria-hidden="true"><span class="cv-gi">{ico('M16 19v-1a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v1M9 10a3 3 0 1 0 0-6 3 3 0 0 0 0 6zM22 19v-1a4 4 0 0 0-3-3.9M16 4.1a3 3 0 0 1 0 5.8', 20)}</span><span><b>Verão Glow</b><small>Grupo da campanha</small></span></div>
        <ol class="cv-msgs" aria-hidden="true">
          <li class="cv-m" data-m="0"><img src="{A('assets/comunidade/av-caio.webp')}" alt="" width="96" height="96"><div><b>Caio Ferraz</b><p>Alguém já fez campanha com envio de produto? Como funciona o prazo de entrega?</p></div></li>
          <li class="cv-m cv-eu" data-m="1"><div><p>Já fiz uma! Te conto como foi.</p></div></li>
          <li class="cv-m" data-m="2"><img src="{A('assets/comunidade/av-beatriz.webp')}" alt="" width="96" height="96"><div><b>Beatriz Nunes <span class="cv-mod">Moderador</span></b><p>Dica: gravem de manhã perto da janela. A luz natural resolve metade do trabalho.</p></div></li>
          <li class="cv-m" data-m="3"><img src="{A('assets/comunidade/av-larissa.webp')}" alt="" width="96" height="96"><div><b>Larissa Prado</b><p>Salvei a dica da luz natural!</p></div></li>
          <li class="cv-dig" data-dig><i></i><i></i><i></i></li>
        </ol>
        <div class="cv-inp" aria-hidden="true"><span>Escreva uma mensagem</span><i>{ico('M22 2 11 13M22 2l-7 20-4-9-9-4 20-7z', 18)}</i></div>
      </div>
      <span class="cv-nota">Conversa ilustrativa.</span>
    </div>
    <ul class="cv-grupos" aria-label="Exemplos de grupos"><li>Creators de Beleza</li><li>Fitness e Corrida</li><li class="cv-cinza">Grupo da sua campanha</li></ul>
    <ol class="cv-areas">
      <li><b><span>01</span> Grupos</b>Das suas campanhas e do seu nicho.</li>
      <li><b><span>02</span> Para você</b>Posts, dicas e conteúdos que deram certo.</li>
      <li><b><span>03</span> Lives</b>Ao vivo, com chat aberto. Comunidade moderada · <a href="{L('/regras-da-comunidade/')}">Regras</a></li>
    </ol>
  </div>
</section>

<section id="confianca" aria-labelledby="cf-h">
  <h2 id="cf-h" class="bt-h2">Quem está por trás</h2>
  <div class="bt-g bt-conf">
    <div class="bt bt-media bt-c1">{ilu('assets/ilustracoes/conf-fantasma.webp', 'Ilustração: creator sorrindo e estendendo na palma da mão o fantasminha do HypeApp', 'bt-fant')}</div>
    <div class="bt bt-branco"><b class="bt-t3">Você no Hype</b><span class="bt-p">Agência de marketing de influência de São Paulo. CNPJ 43.442.408/0001-26.</span><a class="bt-lk" href="{L('/sobre/')}">Sobre o HypeApp</a></div>
    <div class="bt bt-branco bt-ttk"><img src="{A('assets/parceiros/tiktok-shop-partner.webp')}" alt="TikTok Shop Partner" width="280" height="79" loading="lazy" decoding="async"><span class="bt-p">Agência parceira do TikTok Shop.</span></div>
    <div class="bt bt-branco bt-ctr"><b class="bt-t3">Contrato digital</b><span class="bt-p">Ao ser selecionado, o contrato chega por e-mail. Entregas, prazos e condições ficam por escrito.</span></div>
    <div class="bt bt-preto bt-c5"><b class="bt-t3">Seus dados protegidos</b><span class="bt-p">Tratados conforme a LGPD. O HypeApp nunca pede senha, código de verificação ou chave PIX por mensagem.</span><a class="bt-lk" href="{L('/privacidade/')}">Política de Privacidade</a></div>
  </div>
</section>

{cresca_carrossel(A)}

<section class="bt bt-branco bt-faqs" aria-labelledby="faq-c">
  <div class="between" style="align-items:baseline"><h2 id="faq-c" class="bt-h2" style="margin:0">Dúvidas de creators</h2><a class="link-strong" href="{L('/perguntas-frequentes/', '#creators')}">Ver todas</a></div>
  <div class="faq">{faq_html(faq)}</div>
</section>

<section class="bt-baixe" aria-labelledby="baixar-c">
  <div class="bt-baixe-tx">
    <h2 id="baixar-c" class="bt-baixe-h">Baixe e crie seu perfil hoje.</h2>
    <div class="row">{stores(L)}</div>
  </div>
  <img class="bt-baixe-v" src="{A('assets/ilustracoes/baixe-perfil.webp')}" alt="Ilustração: mãos segurando o celular com a tela Crie seu perfil, com os campos Nome e Seu @ e o botão Criar perfil" width="1100" height="786" loading="lazy" decoding="async">
</section>'''

def p_marcas(L, A):
    """Versão B do estudo de 04/11 (bento, como a página de creators), com a seção de agências."""
    return p_marcas_b(L, A)

# ---------- /marcas/: 3 versões de estudo (04/11), só no endereço de teste ----------
# Todas mantêm as telas funcionando: a animação do painel (motion_painel) e as vitrines clicáveis (showcase).
MV_STEPS = [('Mural da campanha', 'Objetivo, público, formatos, prazos e remuneração, publicados no painel.'),
            ('Inscrições e convites', 'Creators se inscrevem pelo mural. Você também busca por nicho e rede e envia convites.'),
            ('Aprovações', 'Roteiros e conteúdos revisados antes de ir ao ar.'),
            ('Entregas e resultados', 'Publicações registradas e métricas da campanha no painel.')]
MV_AG = 'Agências gerenciam as campanhas de cada cliente em espaços separados. Cada marca tem configurações próprias (marca, empresa e equipe), e a equipe alterna entre as marcas pelo seletor no topo do menu.'

def mv_faq():
    return [('Qual a diferença entre self-service e gerenciada?', 'No self-service sua equipe opera tudo no painel. Na gerenciada, a Você no Hype cuida da estratégia, da curadoria e da operação.'),
            ('Quanto custa uma campanha?', 'Os valores são sob consulta e dependem do escopo, do volume e da forma de trabalho.'),
            ('Quais métricas eu acompanho?', METRICAS_TXT),
            ('Como os creators são selecionados?', CURADORIA_TXT),
            ('E se o creator não entregar?', 'O valor reservado para aquela participação volta ao saldo da campanha.'),
            ('Agências podem gerir várias marcas?', AGENCIAS_TXT)]

def mv_aviso(L, letra, nome):
    outras = ''.join(f'<a href="{L("/marcas/versao-" + x.lower() + "/")}"{" aria-current=\"page\"" if x == letra else ""}>Versão {x}</a>' for x in 'ABC')
    return (f'<div class="mv-aviso" role="note"><span><b>Estudo · Versão {letra}:</b> {nome}. Só no endereço de teste.</span>'
            f'<nav aria-label="Versões da página de marcas">{outras}<a href="{L("/marcas/")}">Atual</a></nav></div>')

MV_TELAS = [('bo-n04', 'Catálogo de creators', 'Cada rede com @, seguidores e engajamento. Ver perfil, Convidar e Favoritar.'),
            ('bo-n05', 'Perfil do creator', 'Redes, nichos, bio, campanhas no HypeApp e índice de confiança.'),
            ('bo-n03a', 'Visão geral da campanha', 'Arte da campanha, progresso geral, etapas e o botão Verificar publicações.'),
            ('bo-n03b', 'Precisa da sua ação', 'Inscrições novas para triar e tudo o que aguarda a sua decisão.'),
            ('bo-n01', 'Início', 'Tarefas e aprovações de cada campanha, com o botão Revisar, e as métricas do workspace.'),
            ('bo-n02', 'Campanhas', 'Cartões com capa, status, progresso de publicação, alcance e pendências.'),
            ('bo-n06', 'Lives', 'Ao vivo, agendadas, anteriores e canceladas. Agende ou transmita agora.'),
            ('bo-n07', 'Financeiro', 'Saldo disponível, valor reservado, depósitos e pagamentos aos creators.')]

def p_marcas_a(L, A):
    """Versão A · Produto primeiro: faixa escura com o painel animado, uma vitrine única com todas as telas, modalidades lado a lado."""
    li = ''.join(f'<li><span class="mv-n">0{i + 1}</span><b>{t}</b><span>{d}</span></li>' for i, (t, d) in enumerate(MV_STEPS))
    return f'''{mv_aviso(L, 'A', 'produto primeiro')}
<section class="mva-hero" aria-labelledby="mva-h">
  <div class="mva-top">
    <span class="mv-pill">Para marcas e agências</span>
    <h1 id="mva-h" class="mva-h1">Campanhas com creators do jeito que sua equipe preferir.</h1>
    <p class="mva-lead">Monte o mural da campanha no painel, receba as inscrições, aprove roteiros e conteúdos e acompanhe as métricas. Ou deixe a operação com a Você no Hype.</p>
    <div class="row"><a class="btn btn-cta btn-lg" href="{L('/contato/marcas/')}">Falar com nosso time</a><a class="btn mva-ghost btn-lg" href="#funcionalidades">Ver o painel por dentro</a></div>
  </div>
  {motion_painel(A)}
  <span class="mva-nota">Valores sob consulta, conforme escopo e volume.</span>
</section>

<div id="funcionalidades" class="mv-sc">{showcase(A, 'sc-tudo', 'web', 'Painel', 'Tudo o que a campanha precisa, numa tela só', 'Clique em cada item para ver a tela do painel.', MV_TELAS)}</div>

<section id="modalidades" class="mva-mod" aria-labelledby="mva-mod">
  <h2 id="mva-mod" class="h2">Duas formas de trabalhar</h2>
  <div class="mva-mod-g">
    <div class="mva-card"><span class="tag soft">Self-service</span><b class="h3">Sua equipe opera a campanha no painel.</b>
      <ul><li>Monta o mural da campanha, com briefing e fases</li><li>Seleciona as inscrições e convida creators</li><li>Aprova roteiros e conteúdos</li><li>Acompanha entregas e métricas</li></ul></div>
    <div class="mva-card mva-dark"><span class="tag">Gerenciada</span><b class="h3">A Você no Hype opera a campanha por você.</b>
      <ul><li>Estratégia e curadoria de creators</li><li>Negociação e contratos</li><li>Acompanhamento das entregas</li><li>Relatório de resultados</li></ul></div>
  </div>
</section>

<section class="mva-proc" aria-labelledby="mva-proc"><h2 id="mva-proc" class="h2">Do briefing ao resultado</h2><ol class="mva-steps">{li}</ol></section>

<section id="agencias" class="mva-ag" aria-labelledby="mva-ag"><span class="mv-pill mv-pill-l">Para agências</span><h2 id="mva-ag" class="h2">Várias marcas, um painel.</h2><p>{rev(MV_AG)}</p><a class="btn btn-cta" href="{L('/contato/marcas/')}">Falar com nosso time</a></section>

<section class="faq-block" aria-labelledby="faq-ma"><div class="stack"><h2 id="faq-ma" class="h2">Dúvidas de marcas</h2><a class="link-strong" href="{L('/perguntas-frequentes/', '#marcas')}">Ver todas as dúvidas de marcas</a></div><div class="faq">{faq_html(mv_faq())}</div></section>

<section class="band-dark between" aria-labelledby="mva-cta" style="align-items:center"><h2 id="mva-cta" class="h2" style="flex:1 1 420px">Marque uma demonstração e veja como fica a sua gestão de marketing.</h2><a class="btn btn-cta btn-xl" href="{L('/contato/marcas/')}">Falar com nosso time {ico(I_ARROW, 22)}</a></section>'''

def p_marcas_b(L, A):
    """Versão B · Bento, no mesmo estilo da página de creators."""
    passos = ''.join(f'<div class="bt {c}"><span class="bt-n">0{i + 1}</span><b class="bt-t3">{t}</b><span class="bt-p">{d}</span></div>'
                     for i, ((t, d), c) in enumerate(zip(MV_STEPS, ['bt-branco', 'bt-branco', 'bt-lima', 'bt-preto'])))
    return f'''
<section class="bt-g mvb-hero" aria-labelledby="mvb-h">
  <div class="bt bt-roxo mvb-h1">
    <span class="bt-pill">Para marcas e agências</span>
    <div class="stack" style="gap:20px">
      <h1 id="mvb-h" class="bt-d">Campanhas com creators, do seu jeito.</h1>
      <p class="bt-lead">Opere pelo painel ou deixe a operação com a Você no Hype. Valores sob consulta, conforme escopo e volume.</p>
      <div class="row"><a class="btn btn-ink btn-lg" href="{L('/contato/marcas/')}">Falar com nosso time</a><a class="btn btn-soft btn-lg" href="#funcionalidades">Ver o painel</a></div>
    </div>
  </div>
  <div class="bt bt-preto mvb-demo">{motion_painel(A)}</div>
</section>

<section id="modalidades" aria-labelledby="mvb-mod">
  <h2 id="mvb-mod" class="bt-h2">Quem opera a campanha?</h2>
  <div class="bt-g bt-3">
    <div class="bt bt-branco"><span class="bt-n">Self-service</span><b class="bt-t2">Sua equipe, no painel</b><span class="bt-p">Monta o mural, seleciona as inscrições, convida creators, aprova roteiros e conteúdos e acompanha as métricas.</span></div>
    <div class="bt bt-preto"><span class="bt-n bt-n-l">Gerenciada</span><b class="bt-t2">A Você no Hype, por você</b><span class="bt-p">Estratégia, curadoria de creators, negociação, contratos, acompanhamento das entregas e relatório de resultados.</span></div>
    <a class="bt bt-lima mvb-aglk" href="#agencias"><span class="bt-n">Agências</span><b class="bt-t2">Várias marcas, um painel</b><span class="bt-p">Sua equipe gerencia as campanhas de cada cliente em espaços separados.</span><span class="bt-lk">Ver como funciona</span></a>
  </div>
</section>

<div id="funcionalidades" class="mvb-sc">
{showcase(A, 'sc-painel', 'web', 'Painel', 'Tudo o que pede atenção, logo na entrada', 'Pendências agrupadas por campanha, métricas do workspace e a lista de campanhas.', [MV_TELAS[4], MV_TELAS[5]])}
{showcase(A, 'sc-criadores', 'web', 'Creators', 'Encontre e convide os creators certos', 'Catálogo com as redes de cada creator e um perfil completo antes de convidar.', [MV_TELAS[0], MV_TELAS[1]], flip=True)}
{showcase(A, 'sc-acompanhar', 'web', 'Acompanhamento', 'Cada etapa da campanha à vista', 'Progresso da seleção ao pagamento, indicadores e o que precisa da sua ação.', [MV_TELAS[2], MV_TELAS[3]])}
{showcase(A, 'sc-financeiro', 'web', 'Lives e financeiro', 'Lives e pagamentos no mesmo painel', 'Transmita ao vivo e acompanhe o saldo, o valor reservado e as movimentações.', [MV_TELAS[6], MV_TELAS[7]], flip=True)}
</div>

<section id="agencias" class="ag" aria-labelledby="ag-h">
  <div class="ag-tx">
    <span class="ag-pill">Para agências</span>
    <h2 id="ag-h" class="ag-h">Sua equipe toda, todas as marcas, um painel só.</h2>
    <p class="ag-p">{rev('Cada cliente tem um espaço próprio, com as configurações da marca, da empresa e da equipe. Várias pessoas do seu time cuidam das campanhas de cada marca, e quem atende mais de um cliente troca de marca pelo seletor no topo do menu.')}</p>
    <ul class="ag-lista">
      <li><b>Um espaço por cliente</b>Campanhas, creators e financeiro de cada marca, separados.</li>
      <li><b>Equipe por marca</b>As pessoas certas cuidando de cada cliente.</li>
      <li><b>Várias campanhas ao mesmo tempo</b>Pendências e aprovações de cada campanha logo na entrada do painel.</li>
    </ul>
    <a class="btn btn-cta btn-lg" href="{L('/contato/marcas/')}">Falar com nosso time</a>
  </div>
  <div class="ag-arte">
    <div class="ag-pers ag-p1"><img src="{A('assets/ilustracoes/agencia-1.webp')}" alt="Ilustração: profissional de agência de óculos, de braços cruzados com o caderno" width="600" height="1208" loading="lazy" decoding="async"></div>
    <div class="ag-pers ag-p2"><img src="{A('assets/ilustracoes/agencia-2.webp')}" alt="Ilustração: profissional de agência sorrindo, com o notebook embaixo do braço" width="600" height="1215" loading="lazy" decoding="async"></div>
    <div class="ag-sel" aria-hidden="true">
      <span class="ag-sel-h">Trocar de marca</span>
      <span class="ag-m on"><i>CL</i>Casa Lume<em>4 campanhas</em></span>
      <span class="ag-m"><i>AU</i>Aurora<em>2 campanhas</em></span>
      <span class="ag-m"><i>BR</i>Brisa<em>3 campanhas</em></span>
    </div>
  </div>
</section>

<section aria-labelledby="mvb-proc"><h2 id="mvb-proc" class="bt-h2">Do briefing ao resultado</h2><div class="bt-g mvb-4">{passos}</div></section>

<section class="bt bt-branco mvb-faq" aria-labelledby="faq-mb"><div class="between" style="align-items:baseline"><h2 id="faq-mb" class="bt-h2" style="margin:0">Dúvidas de marcas</h2><a class="link-strong" href="{L('/perguntas-frequentes/', '#marcas')}">Ver todas</a></div><div class="faq">{faq_html(mv_faq())}</div></section>

<section class="bt-baixe" aria-labelledby="mvb-cta"><div class="bt-baixe-tx"><h2 id="mvb-cta" class="bt-baixe-h">Marque uma demonstração.</h2><div class="row"><a class="btn btn-ink btn-xl" href="{L('/contato/marcas/')}">Falar com nosso time {ico(I_ARROW, 22)}</a></div></div><img class="bt-baixe-v" src="{A('assets/menu/monitor-painel.webp')}" alt="Monitor com o painel das marcas do HypeApp" width="480" height="424" loading="lazy" decoding="async"></section>'''

def p_marcas_c(L, A):
    """Versão C · Perguntas da marca: cada seção responde uma dúvida, com a tela que prova a resposta."""
    def q(n, t):
        return f'<div class="mvc-q"><span class="mvc-num">{n}</span><h2 class="mvc-qt">{t}</h2></div>'
    return f'''{mv_aviso(L, 'C', 'perguntas da marca')}
<section class="mvc-hero" aria-labelledby="mvc-h">
  <span class="mv-pill mv-pill-l">Para marcas e agências</span>
  <h1 id="mvc-h" class="mvc-h1">Tudo o que sua marca quer saber antes de rodar uma campanha com creators.</h1>
  <ul class="mvc-chips" aria-label="Perguntas respondidas nesta página">
    <li><a href="#q1">Como encontro os creators certos?</a></li><li><a href="#q2">Como controlo o que vai ao ar?</a></li>
    <li><a href="#q3">Como acompanho os resultados?</a></li><li><a href="#q4">Como pago os creators?</a></li><li><a href="#modalidades">Quem opera a campanha?</a></li>
  </ul>
</section>

<section id="q1" class="mvc-sec">{q('01', 'Como encontro os creators certos?')}
{showcase(A, 'sc-criadores', 'web', 'Creators', 'Busque por nicho e rede, veja o perfil e convide', 'Creators também se inscrevem pelo mural da campanha. Você escolhe quem participa.', [MV_TELAS[0], MV_TELAS[1]])}</section>

<section id="q2" class="mvc-sec mvc-dark">{q('02', 'Como controlo o que vai ao ar?')}
  <p class="mvc-p">Roteiros e conteúdos passam pela sua aprovação antes da publicação. Veja o painel em ação: encontrar creators, aprovar conteúdo, resultados e financeiro.</p>
  {motion_painel(A)}
</section>

<section id="q3" class="mvc-sec">{q('03', 'Como acompanho os resultados?')}
{showcase(A, 'sc-acompanhar', 'web', 'Acompanhamento', 'Cada etapa da campanha à vista', 'Progresso da seleção ao pagamento, indicadores e o que precisa da sua ação.', [MV_TELAS[2], MV_TELAS[3], MV_TELAS[4], MV_TELAS[5]], flip=True)}</section>

<section id="q4" class="mvc-sec">{q('04', 'Como pago os creators?')}
{showcase(A, 'sc-financeiro', 'web', 'Financeiro', 'Saldo, valor reservado e pagamentos no painel', 'Se o creator não entregar, o valor reservado para aquela participação volta ao saldo da campanha.', [MV_TELAS[7], MV_TELAS[6]])}</section>

<section id="modalidades" class="mvc-sec">{q('05', 'Quem opera a campanha?')}
  <div class="grid-300">
    <div class="mode"><span class="tag soft">Self-service</span><span class="h3">Sua equipe opera a campanha no painel.</span>
      <ul><li>Monta o mural da campanha, com briefing e fases</li><li>Seleciona as inscrições e convida creators</li><li>Aprova roteiros e conteúdos</li><li>Acompanha entregas e métricas</li></ul></div>
    <div class="mode dark"><span class="tag">Gerenciada</span><span class="h3">A Você no Hype opera a campanha por você.</span>
      <ul><li>Estratégia e curadoria de creators</li><li>Negociação e contratos</li><li>Acompanhamento das entregas</li><li>Relatório de resultados</li></ul></div>
  </div>
</section>

<section id="agencias" class="mvc-sec">{q('06', 'E se eu for agência?')}<p class="mvc-p">{rev(MV_AG)}</p></section>

<section class="mvc-sec">{q('07', 'Quanto custa?')}<p class="mvc-p">O valor depende do escopo, do volume e da forma de trabalho. O comercial monta a proposta depois de entender sua campanha.</p>
  <div class="faq">{faq_html(mv_faq()[2:5])}</div></section>

<section class="band-dark between" aria-labelledby="mvc-cta" style="align-items:center"><h2 id="mvc-cta" class="h2" style="flex:1 1 420px">Ficou alguma pergunta? A gente responde numa demonstração.</h2><a class="btn btn-cta btn-xl" href="{L('/contato/marcas/')}">Falar com nosso time {ico(I_ARROW, 22)}</a></section>'''

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
        ('Como recebo o pagamento?', PIX_TXT),
        ('Preciso emitir nota fiscal?', 'Depende da campanha e do seu cadastro como pessoa física ou jurídica. O app informa o que é exigido antes do pagamento.'),
        ('Recebidos e permuta: o produto fica comigo?', 'Depende da campanha. O mural de cada campanha informa se o produto é seu ou se precisa ser devolvido.'),
        ('A marca pode usar meu conteúdo depois?', 'Depende do contrato da campanha, firmado entre você e a marca. Confira as condições de uso de imagem antes de aceitar o convite.'),
        ('Como funciona a comunidade?', COMUNIDADE_TXT),
    ]),
    ('marcas', 'Para marcas e agências', [
        ('Como marcas e agências começam?', 'Pelo formulário Falar com nosso time. O comercial entende a campanha, envia uma proposta e libera o acesso ao painel.'),
        ('Como os creators chegam à minha campanha?', 'Você monta o mural da campanha no painel e os creators se inscrevem por ele. Também dá para buscar creators e enviar convites.'),
        ('Quanto custa uma campanha?', 'Os valores são sob consulta e dependem do escopo, do volume e da forma de trabalho.'),
        ('Qual a diferença entre self-service e gerenciada?', 'No self-service sua equipe opera tudo no painel. Na gerenciada, a Você no Hype cuida da estratégia, da curadoria e da operação.'),
        ('Quais métricas eu acompanho?', METRICAS_TXT),
           ('Como os creators são selecionados?', CURADORIA_TXT),
        ('E se o creator não entregar?', 'O valor reservado para aquela participação volta ao saldo da campanha.'),
        ('Agências podem gerir várias marcas?', AGENCIAS_TXT),
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
  <div class="card stack" style="background:var(--ink);color:var(--purple-ink)"><span class="h4">Quem opera</span><p class="small" style="font-size:15px">Desenvolvido e operado pela Você no Hype Marketing e Entretenimento LTDA, CNPJ 43.442.408/0001-26. R. Joaquim Floriano, 243, cj. 71, Itaim Bibi, São Paulo/SP, CEP 04534-010.</p></div>
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
  <form class="card form form-steps" style="flex:1 1 560px" data-form data-clarity-mask="true" name="comercial" method="POST" action="{'/api/lead' if WEB else L('/contato/enviado/')}" data-next="{L('/contato/enviado/')}"{FORM_LIVE} novalidate>
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
  <form class="card form" style="flex:1 1 520px" data-form data-clarity-mask="true" name="suporte" method="POST" action="{'/api/lead' if WEB else L('/suporte/enviado/')}" data-next="{L('/suporte/enviado/')}"{FORM_LIVE} novalidate>
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
    <div class="cols-2">{field('nome', 'Nome', extra=' autocomplete="name" data-min="2" maxlength="100"')}{field('email', 'E-mail para resposta', 'email', extra=' autocomplete="email"', ph='nome@email.com')}</div>
    {field('descricao', 'Descreva o que aconteceu', 'textarea', extra=' data-min="10" maxlength="3000"')}
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
  <p class="sup-num" data-pedido hidden>Pedido <b>#<span data-pedido-n></span></b> enviado</p>
  <p class="lead">A primeira resposta chega em até 2 dias úteis, de segunda a sexta, das 10h às 18h.</p>
  <p class="small">Você vai receber uma confirmação automática por e-mail com o número do pedido. Não responda a ela: se precisar complementar, abra um novo chamado.</p>
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

COOKIES_GA = [
    ('necessarios', 'Necessários', rev('Para funcionar, o site guarda no seu navegador a sua escolha sobre cookies (por até 12 meses) e, só enquanto a aba estiver aberta, '
        'a página de entrada e os parâmetros da campanha que trouxe você (utm, gclid e fbclid), que seguem junto com o formulário de contato. '
        'Isso não identifica você e não precisa de consentimento.')),
    ('medicao', 'Medição de visitas', rev('Se você aceitar os cookies de medição, '
        'usamos o Google Analytics 4, carregado pelo Google Tag Manager, para saber quais páginas são vistas, de onde vêm as visitas, '
        'quais botões são clicados e quantos formulários são enviados, e o Microsoft Clarity, que registra cliques, rolagem e movimentos na página '
        'para gerar mapas de calor e gravações da navegação. Os campos de formulário ficam ocultos nas gravações. '
        'Não enviamos nome, e-mail, telefone nem o texto dos formulários ao Google ou à Microsoft.')),
    ('google-analytics', 'Cookies do Google Analytics', rev('Os cookies _ga e _ga_ seguido do código da propriedade distinguem visitantes e visitas e duram até 2 anos. '
        'Só são gravados depois do seu aceite. O Google atua como operador desses dados e pode tratá-los fora do Brasil, '
        'conforme a <a href="{{PRIVACIDADE}}">Política de Privacidade</a>.')),
    ('microsoft-clarity', 'Cookies do Microsoft Clarity', rev('Os cookies _clck (até 1 ano) e _clsk (1 dia) ligam as páginas de uma mesma visita. '
        'Só são gravados depois do seu aceite. A Microsoft atua como operadora desses dados e pode tratá-los fora do Brasil, '
        'conforme a <a href="{{PRIVACIDADE}}">Política de Privacidade</a>.')),
    ('publicidade', 'Publicidade', rev('O site não usa cookies de publicidade. Se isso mudar, esta política será atualizada e o site vai pedir a sua escolha antes de ativá-los.')),
    ('escolha', 'Como mudar a sua escolha', rev('Use o link <a href="#preferencias-cookies">Preferências de cookies</a>, no rodapé de qualquer página. '
        'Se você recusar depois de ter aceitado, o site apaga os cookies do Google Analytics e do Clarity. Você também pode apagar cookies nas configurações do navegador.')),
]

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
    '/cookies/': ('Política de cookies', 'Quais tecnologias o site usa, para quê e como mudar sua escolha.', COOKIES_GA) if ANALYTICS else ('Política de cookies', 'Quais tecnologias o site usa e para quê.', [
        ('necessarios', 'Cookies necessários', 'O site não usa cookies de publicidade nem de rastreamento. Usa apenas o necessário para funcionar.'),
        ('medicao', 'Medição de visitas', 'O site não usa ferramentas de medição de visitas.'),
        ('opcionais', 'Cookies opcionais', 'Se alguma ferramenta de publicidade ou de análise com cookies for adicionada, o site vai pedir sua escolha antes de carregá-la.')]),
    '/exclusao-de-conta/': ('Exclusão de conta', 'Como pedir a exclusão da sua conta do HypeApp e dos dados associados.', [
        ('app', 'Pelo app', '[Caminho no app a confirmar, por exemplo: Perfil, Configurações, Excluir conta.]'),
        ('site', 'Pelo site', 'Abra um chamado no suporte com o assunto Excluir minha conta, usando o e-mail da conta.'),
        ('o-que-acontece', 'O que é apagado', '[Dados apagados, prazo e o que fica guardado por obrigação legal, como registros fiscais de pagamentos.]'),
        ('saldo', 'Saldo e campanhas em andamento', '[Regra aprovada para saldo a liberar e entregas abertas.]')]),
}

def aviso_cookies(L):
    """Aviso de cookies (LGPD). Começa escondido; o site.js mostra quando ainda não há escolha salva."""
    return f'''<section class="ck" id="ck" hidden role="dialog" aria-modal="false" aria-labelledby="ck-t" aria-describedby="ck-d">
  <div class="ck-in">
    <h2 class="ck-t" id="ck-t" tabindex="-1">Cookies no HypeApp</h2>
    <p class="ck-d" id="ck-d">Com a sua permissão, usamos cookies de medição do Google Analytics e do Microsoft Clarity para entender como o site é usado e melhorar as páginas. Eles só são ativados se você aceitar. <a href="{L('/cookies/')}">Política de cookies</a></p>
    <div class="ck-pref" id="ck-pref" hidden>
      <div class="ck-op"><div><b>Necessários</b><span>Guardam a sua escolha sobre cookies e a origem da visita para o formulário de contato. Não identificam você.</span></div><span class="ck-sempre">Sempre ativos</span></div>
      <label class="ck-op" for="ck-med"><div><b>Medição</b><span>Google Analytics (páginas vistas, cliques e envios de formulário) e Microsoft Clarity (mapas de cliques e gravações da navegação, com os campos de formulário ocultos). Nada de nome, e-mail ou telefone.</span></div><input type="checkbox" class="ck-sw" id="ck-med" role="switch"></label>
    </div>
    <div class="ck-bt">
      <button type="button" class="btn btn-ghost" data-ck="recusar">Recusar</button>
      <button type="button" class="btn btn-soft ck-mais" data-ck="personalizar" aria-controls="ck-pref" aria-expanded="false">Personalizar</button>
      <button type="button" class="btn btn-ghost" data-ck="salvar" hidden>Salvar escolhas</button>
      <button type="button" class="btn btn-ink" data-ck="aceitar">Aceitar</button>
    </div>
  </div>
</section>
'''

def p_legal(url):
    def f(L, A):
        t, d, secs = LEGAL[url]
        toc = ''.join(f'<a href="#{sid}">{st}</a>' for sid, st, _ in secs)
        body = ''.join(f'<h2 id="{sid}">{st}</h2><p>{tx}</p>' for sid, st, tx in secs).replace('{{PRIVACIDADE}}', L('/privacidade/'))
        extra = ''
        if url == '/exclusao-de-conta/':
            extra = f'<p><a class="btn btn-ink" href="{L("/suporte/")}">Abrir pedido de exclusão</a></p>'
        return f'''
<section class="page-hero" aria-labelledby="lg-h"><h1 id="lg-h" class="display" style="font-size:clamp(36px,5vw,56px)">{t}</h1><p class="lead">{d}</p>
</section>
<div class="doc-layout"><nav class="toc" aria-label="Nesta página">{toc}</nav><article class="prose card">{body}{extra}</article></div>'''
    return f

def p_regras(L, A):
    nao = ['assédio, bullying, ameaças ou incitação ao ódio;', 'nudez, conteúdo sexual explícito ou exploração;', 'violência gráfica ou apologia a ela;',
           'spam, golpes ou desinformação;', 'conteúdo ilegal, discriminatório ou que viole direitos de terceiros.']
    secs = [('tolerancia', 'Tolerância zero', '<p>A comunidade do HypeApp tem tolerância zero a conteúdo censurável e a comportamento abusivo. Isso vale para publicações, comentários, grupos, lives e mensagens.</p>'),
            ('proibido', 'O que não é permitido', '<ul>' + ''.join(f'<li>{x}</li>' for x in nao) + '</ul>'),
            ('denunciar', 'Como denunciar', '<p>Toque no menu "…" da publicação, ou segure sobre o comentário, o comentário da live ou a mensagem, e escolha "Denunciar". As denúncias são analisadas em até 24 horas.</p>'),
            ('consequencias', 'O que acontece com quem viola as regras', '<p>Contas que violarem estas diretrizes podem ter o conteúdo removido e o acesso suspenso ou encerrado, conforme os <a href="' + L('/termos/') + '">Termos de Uso</a>.</p>'),
            ('bloquear', 'Bloquear outro usuário', '<p>Você também pode bloquear outro usuário. Quem você bloqueia deixa de interagir com você na comunidade.</p>')]
    toc = ''.join(f'<a href="#{i}">{t}</a>' for i, t, _ in secs)
    body = ''.join(f'<h2 id="{i}">{t}</h2>{c}' for i, t, c in secs)
    rv = ('' if WEB else '<aside class="legal-review" aria-label="Pontos para revisão"><b>Só na prévia · rascunho</b><ul><li>Texto da tela Diretrizes da comunidade do app. Precisa do ok do jurídico antes de publicar.</li>'
          '<li>Confirmar com o produto o que o bloqueio faz exatamente (ocultar conteúdo, impedir mensagens).</li></ul></aside>')
    return f'''
<section class="page-hero" aria-labelledby="rc-h"><h1 id="rc-h" class="display" style="font-size:clamp(36px,5vw,56px)">Regras da comunidade</h1>
  <p class="lead">Como manter a comunidade do HypeApp segura para creators e marcas, e o que fazer quando algo passar do limite.</p></section>
<div class="doc-layout"><nav class="toc" aria-label="Nesta página">{toc}</nav><article class="prose card legal">{body}</article></div>'''

def p_legal_hub(L, A):
    docs = [('Política de privacidade', 'Como tratamos dados pessoais no site, no app e no painel, e os seus direitos.', L('/privacidade/')),
            ('Termos de uso', 'Regras para usar o site, o app e o painel do HypeApp.', L('/termos/')),
            ('Política de cookies', 'Quais tecnologias o site usa e como mudar suas preferências.', L('/cookies/')),
            ('Encarregado de dados', 'Quem responde por dados pessoais e como falar com ele.', L('/privacidade/', '#encarregado')),
            ('Regras da comunidade', 'O que não é permitido na comunidade, como denunciar e o que acontece com quem viola as regras.', L('/regras-da-comunidade/')),
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
        ['Versão 2.0 de 03/11, montada a partir da política da Você no Hype (2025) e da anterior do HypeApp (02/09/2026). Precisa da aprovação do jurídico.',
         'Sede confirmada pelo Lucas em 03/11 (R. Joaquim Floriano, 243, cj. 71). Conferir o CEP 04534-010 com o cartão CNPJ.',
         'Instagram: a conexão é pelo código na bio, sem login da Meta. A tecnologia precisa dizer de onde vêm as métricas (dados públicos, prints ou outro provedor); a resposta muda a seção 7.1.',
         'TikTok: a lista de dados da seção 7.2 precisa bater com os escopos aprovados (por exemplo user.info.basic, user.info.stats, video.list). Aguardando a tecnologia.',
         'Login com Google ou Apple: o app ainda não tem. O texto fala "quando estiver disponível".',
         'Prazos de retenção vieram da política da Você no Hype (leads 24 meses, clientes 5 anos). Confirmar se valem para o HypeApp.',
         'Hype Points (seção 6): aguarda a confirmação do Lucas para aparecer nos textos legais.']),
    '/termos/': ('termos.html', 'Termos de Uso', 'Termos e condições gerais de uso do HypeApp para creators, marcas e agências.',
        ['Versão 2.0 de 03/11: atualiza o texto de 2022 para o modelo atual (campanhas, carteira, reservas, PIX, redes conectadas, Hype Points e comunidade). Precisa da aprovação do jurídico.',
         'A antiga cláusula 9.4 (sem responsabilidade sobre transações) virou 14.2 e 14.3: a plataforma responde pela movimentação da carteira e não pelas obrigações entre marca e creator.',
         'Seção 6 atualizada com as respostas do Lucas (03/11): chave PIX do titular, sem taxa, sem valor máximo, mínimo de R$ 1,00, saque em até 2 horas úteis, liberação 30 dias após o encerramento. Falta o prazo máximo de análise de contestação (6.6).',
         'Hype Points (seção 8): aguarda a confirmação do Lucas.',
         'Foro: incluída a ressalva do foro do domicílio do consumidor. Confirmar com o jurídico.']),
    '/exclusao-de-conta/': ('exclusao.html', 'Exclusão de conta e dados', 'Como excluir sua conta no HypeApp e o que acontece com os seus dados.',
        ['Texto da página oficial de exclusão (api-v2.hypeapp.com.br/api/legal/solicitar-exclusao-dados), sem a linha técnica sobre a chamada da API.',
         'Se as lojas apontam para o endereço antigo, mantenha os dois no ar ou redirecione o antigo para cá.']),
}

def p_legal_file(url):
    def f(L, A):
        fn, t, d, notes = LEGAL_FILES[url]
        body = open(os.path.join(HERE, 'content', fn), encoding='utf-8').read()
        body = body.replace('{{PRIVACIDADE}}', L('/privacidade/')).replace('{{EXCLUSAO}}', L('/exclusao-de-conta/')).replace('{{COOKIES}}', L('/cookies/')).replace('{{REGRAS}}', L('/regras-da-comunidade/'))
        toc = ''.join('<a href="#%s">%s</a>' % (i, re.sub('<[^>]+>', '', x)) for i, x in re.findall(r'<h2 id="([^"]+)">(.*?)</h2>', body))
        rev = ''
        if False and CFG['preview'] and notes:  # políticas aprovadas em 04/11: sem a lista de pontos para o jurídico
            rev = ('<aside class="legal-review" aria-label="Pontos para o jurídico"><b>Só na prévia · pontos para o jurídico revisar</b><ul>'
                   + ''.join('<li>%s</li>' % n for n in notes) + '</ul></aside>')
        return ('<section class="page-hero" aria-labelledby="lg-h"><h1 id="lg-h" class="display" style="font-size:clamp(36px,5vw,56px)">%s</h1><p class="lead">%s</p></section>\n%s\n'
                '<div class="doc-layout"><nav class="toc" aria-label="Nesta página">%s</nav><article class="prose card legal">%s</article></div>') % (t, d, rev, toc, body)
    return f

# ---------- Blog (content/blog/*.md, ver blog_build.py) ----------
import blog_build as _blog
POSTS = _blog.load_posts(HERE, WEB)
BLOG_ON = bool(POSTS)   # sem artigo, /blog/ não existe e os links para ele somem
PUBLICADOS = [_p for _p in POSTS if _p['status'] == 'publicado']
# Só no ambiente de teste (artigos em revisão): no www esses endereços redirecionam para a Início (make_vercel.py)
SO_TESTE = ([] if PUBLICADOS else ['/blog/']) + ['/blog/' + _p['slug'] + '/' for _p in POSTS if _p['status'] == 'revisao'] if WEB else []
POST_META = _blog.post_meta(POSTS, BASE)

PAGES = [
    ('/', p_home, 'wide'), ('/criadores/', p_criadores, 'wide'), ('/marcas/', p_marcas, 'wide'),
    ('/baixar/', p_baixar, 'tight'), ('/perguntas-frequentes/', p_faq, 'mid'), ('/sobre/', p_sobre, 'mid'),
    ('/contato/', p_contato, 'mid'), ('/contato/marcas/', p_contato_marcas, 'mid'), ('/contato/enviado/', p_enviado, 'mid'),
    ('/suporte/', p_suporte, 'mid'), ('/suporte/enviado/', p_sup_enviado, 'mid'), ('/entrar/', p_entrar, 'mid'),
    ('/app', p_app, 'mid'),
    ('/privacidade/', p_legal_file('/privacidade/'), 'mid'), ('/termos/', p_legal_file('/termos/'), 'mid'),
    ('/cookies/', p_legal('/cookies/'), 'mid'), ('/exclusao-de-conta/', p_legal_file('/exclusao-de-conta/'), 'mid'),
    ('/legal/', p_legal_hub, 'mid'), ('/regras-da-comunidade/', p_regras, 'mid'),
    ('/404', p_404, 'mid'),
]

if BLOG_ON:
    PAGES += [('/blog/', _blog.p_blog(POSTS), 'wide')] + [('/blog/' + _p['slug'] + '/', _blog.p_post(_p), 'mid') for _p in POSTS]

FALLBACK = {
    '/entrar/': ('Entrar no HypeApp', 'Creators entram pelo app. Marcas e agências entram pelo painel.'),
    '/app': ('Baixar o HypeApp', 'Leva à loja certa para o seu celular.'),
    '/404': ('Página não encontrada | HypeApp', 'O endereço pode ter mudado.'),
    '/marcas/versao-a/': ('Para marcas · versão A (estudo) | HypeApp', 'Estudo da página de marcas: produto primeiro.'),
    '/marcas/versao-b/': ('Para marcas · versão B (estudo) | HypeApp', 'Estudo da página de marcas: bento.'),
    '/marcas/versao-c/': ('Para marcas · versão C (estudo) | HypeApp', 'Estudo da página de marcas: perguntas da marca.'),
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

# ---------- Dados estruturados (JSON-LD) ----------
EMPRESA = 'Você no Hype Marketing e Entretenimento LTDA'
CNPJ = '43.442.408/0001-26'
EMAIL = 'contato@vocenohype.com.br'
FONE = '+55 11 3834-5221'
# Sede confirmada pelo Lucas em 03/11 (conferir o CEP com o cartão CNPJ).
ENDERECO = {'@type': 'PostalAddress', 'streetAddress': 'R. Joaquim Floriano, 243, cj. 71, Itaim Bibi', 'addressLocality': 'São Paulo',
            'addressRegion': 'SP', 'postalCode': '04534-010', 'addressCountry': 'BR'}
ORG_ID, SITE_ID, APP_ID = BASE + '/#organizacao', BASE + '/#site', BASE + '/#app'
ORG = {'@context': 'https://schema.org', '@type': 'Organization', '@id': ORG_ID, 'name': 'HypeApp', 'alternateName': 'Hype App',
       'legalName': EMPRESA, 'taxID': CNPJ, 'url': BASE + '/',
       # logo em PNG quadrado (o Google não garante SVG no logo da organização)
       'logo': {'@type': 'ImageObject', 'url': BASE + '/icon-512.png', 'width': 512, 'height': 512},
       'email': EMAIL, 'telephone': FONE, 'address': ENDERECO,
       'contactPoint': [
           {'@type': 'ContactPoint', 'contactType': 'customer support', 'email': EMAIL, 'telephone': FONE, 'url': BASE + '/suporte/',
            'areaServed': 'BR', 'availableLanguage': 'pt-BR',
            'hoursAvailable': {'@type': 'OpeningHoursSpecification', 'dayOfWeek': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'], 'opens': '10:00', 'closes': '18:00'}},
           {'@type': 'ContactPoint', 'contactType': 'sales', 'email': EMAIL, 'url': BASE + '/contato/marcas/', 'areaServed': 'BR', 'availableLanguage': 'pt-BR'},
           {'@type': 'ContactPoint', 'contactType': 'encarregado de dados pessoais (LGPD)', 'email': EMAIL, 'url': BASE + '/privacidade/#encarregado', 'availableLanguage': 'pt-BR'}],
       'sameAs': [u for _, u, _, _ in SOCIAL]}
WEBSITE = {'@context': 'https://schema.org', '@type': 'WebSite', '@id': SITE_ID, 'name': 'HypeApp', 'alternateName': ['Hype App', 'hypeapp.com.br'], 'url': BASE + '/',
           'inLanguage': 'pt-BR', 'publisher': {'@id': ORG_ID}}
APP = {'@context': 'https://schema.org', '@type': 'MobileApplication', '@id': APP_ID, 'name': 'HypeApp',
       'description': 'App para creators participarem de campanhas com marcas: inscrição, entregas, chat com a marca e pagamentos na carteira.',
       'operatingSystem': 'iOS 15.1 ou superior, Android', 'applicationCategory': 'BusinessApplication', 'inLanguage': 'pt-BR',
       'offers': {'@type': 'Offer', 'price': '0', 'priceCurrency': 'BRL'},
       'downloadUrl': [CFG['ios'], CFG['android']], 'installUrl': CFG['android'], 'sameAs': [CFG['ios'], CFG['android']],
       'publisher': {'@id': ORG_ID}}
SERVICOS = [{'@context': 'https://schema.org', '@type': 'Service', 'name': nome, 'serviceType': 'Campanhas de marketing de influência com creators',
             'description': desc, 'provider': {'@id': ORG_ID}, 'areaServed': {'@type': 'Country', 'name': 'Brasil'},
             'audience': {'@type': 'BusinessAudience', 'audienceType': 'Marcas e agências'}, 'url': BASE + '/marcas/'}
            for nome, desc in [
                ('Campanhas self-service no painel', 'Sua equipe opera tudo no painel: cria a campanha, encontra e convida creators, aprova conteúdos, acompanha métricas e faz os pagamentos.'),
                ('Campanhas gerenciadas', 'A Você no Hype cuida da estratégia, da curadoria de creators e da operação da campanha.')]]
TIPO_PAGINA = {'/perguntas-frequentes/': 'FAQPage', '/sobre/': 'AboutPage', '/contato/': 'ContactPage', '/contato/marcas/': 'ContactPage', '/suporte/': 'ContactPage'}

def faq_entities():
    limpa = lambda s: ' '.join(html.unescape(re.sub(r'<[^>]+>', ' ', s)).split())
    return [{'@type': 'Question', 'name': limpa(q), 'acceptedAnswer': {'@type': 'Answer', 'text': limpa(a)}}
            for _, _, items in FAQ_GROUPS for q, a in items]

# Datas de publicação e de alteração: mudam só quando o conteúdo da página muda (registro em datas.json)
from datetime import datetime as _dt
from zoneinfo import ZoneInfo as _Z
HOJE = _dt.now(_Z('America/Sao_Paulo')).date().isoformat()
DATAS_F = os.path.join(HERE, 'datas.json')
DATAS = json.load(open(DATAS_F, encoding='utf-8')) if os.path.exists(DATAS_F) else {}

def datas_da(url, conteudo):
    h = _hl.md5(conteudo.encode('utf-8')).hexdigest()
    d = DATAS.get(url)
    if not d:
        d = {'publicado': HOJE, 'alterado': HOJE, 'hash': h}
    elif d['hash'] != h:
        d = dict(d, alterado=HOJE, hash=h)
    if WEB:
        DATAS[url] = d
    return d

def jsonld(url, title, desc, d):
    if url in ('/404', '/app'):
        return []
    pag = {'@context': 'https://schema.org', '@type': TIPO_PAGINA.get(url, 'WebPage'), '@id': BASE + url + '#pagina', 'url': BASE + url,
           'name': title, 'description': desc, 'inLanguage': 'pt-BR', 'isPartOf': {'@id': SITE_ID}, 'publisher': {'@id': ORG_ID},
           'datePublished': d['publicado'], 'dateModified': d['alterado']}
    if url == '/perguntas-frequentes/':
        pag['mainEntity'] = faq_entities()
    if url in ('/criadores/', '/baixar/'):
        pag['about'] = {'@id': APP_ID}
    out = [pag]
    if url == '/':
        out = [ORG, WEBSITE, APP, pag]
    else:
        out.append(crumbs(url))
    if url in ('/criadores/', '/baixar/'):
        out.append(APP)
    if url == '/marcas/':
        out += SERVICOS
    if url in POST_META:
        out.append(POST_META[url]['ld'])
    return out

# Texto alternativo da imagem de compartilhamento: o que está escrito nela (make_media.OG)
try:
    import importlib.util as _ilu
    _spec = _ilu.spec_from_file_location('make_media', os.path.join(HERE, 'make_media.py')); _mm = _ilu.module_from_spec(_spec); _spec.loader.exec_module(_mm)
    OG_TXT = {k: f'HypeApp · {v[0]}: {v[1]}' for k, v in _mm.OG.items()}
except Exception:
    OG_TXT = {}
def og_alt(img, title):
    return OG_TXT.get(img) or f'{title.split(" | ")[0]} · HypeApp'

# Imagens e vídeos com ?v=<hash do arquivo>: trocar uma imagem com o mesmo nome invalida o cache do navegador (04/11).
_VH = {}
def versiona(page):
    import hashlib
    def rep(m):
        rel = m.group(2)
        f = os.path.join(HERE, rel)
        if rel not in _VH:
            _VH[rel] = hashlib.md5(open(f, 'rb').read()).hexdigest()[:8] if os.path.isfile(f) else ''
        return m.group(1) + rel + (('?v=' + _VH[rel]) if _VH[rel] else '')
    page = re.sub(r'((?:src|poster|href|srcset)="(?:/|(?:\.\./)*))(assets/[\w./-]+\.(?:webp|png|jpg|jpeg|svg|mp4))(?=")', rep, page)
    # srcset com várias larguras: versiona cada endereço da lista
    item = re.compile(r'((?:^|,\s*)(?:/|(?:\.\./)*))(assets/[\w./-]+\.(?:webp|png|jpg|jpeg))(?=\s)')
    return re.sub(r'srcset="([^"]+)"', lambda m: 'srcset="' + item.sub(rep, m.group(1)) + '"', page)

def build_page(url, fn, kind):
    L, A = make_link(url)
    m = META.get(url) or POST_META.get(url)
    title, desc = (m['title'], m['desc']) if m else FALLBACK[url]
    robots = 'noindex, nofollow' if CFG['preview'] or url in SO_TESTE else (m['robots'] if m else 'noindex, follow')
    canon = (BASE + '/marcas/' if url.startswith('/marcas/versao-') else BASE + url) if url not in ('/404', '/app') else ''  # /app é página de passagem, sem índice
    main = fn(L, A)
    cls = 'home' if url == '/' else 'wrap' + (' tight' if kind == 'tight' else '')
    body = header(url, L, A) + f'\n<main class="{cls}" id="conteudo">{main}</main>\n' + tiktok_shop(L, A, url) + '\n' + footer(L, A)
    body = mark_ph(body)
    for p, _ in [('/criadores/', 0), ('/marcas/', 0), ('/perguntas-frequentes/', 0)]:
        pass
    d = datas_da(url, title + desc + main)
    mdoc = re.search(r'[ÚU]ltima atualiza[çc][ãa]o:\s*(\d{1,2}) de (\w+) de (\d{4})', main)
    if mdoc:  # documentos legais: vale a data escrita no próprio texto
        mes = ['janeiro', 'fevereiro', 'março', 'abril', 'maio', 'junho', 'julho', 'agosto', 'setembro', 'outubro', 'novembro', 'dezembro'].index(mdoc.group(2).lower()) + 1
        doc = f'{mdoc.group(3)}-{mes:02d}-{int(mdoc.group(1)):02d}'
        d = dict(d, publicado=min(d['publicado'], doc), alterado=doc)
    jl = jsonld(url, title, desc, d)
    ld = ''.join(f'<script type="application/ld+json">{json.dumps(j, ensure_ascii=False)}</script>' for j in jl)
    bar = (f'<div class="preview-bar"><strong>Prévia do site</strong> · conteúdo em revisão. Textos entre colchetes aguardam aprovação; trechos em amarelo são rascunhos em revisão. Envios de formulário são simulados. <a href="{A("iphone/index.html")}">Ver no iPhone</a></div>' if CFG['preview'] else '')
    head = f'''<title>{html.escape(title)}</title>
{'' if WEB else '<meta name="claude:viewport-fit-sides" content="cover">'}
<meta name="description" content="{html.escape(desc)}">
<meta name="robots" content="{robots}">
{f'<link rel="canonical" href="{canon}">' if canon else ''}
<meta property="og:type" content="{'article' if url in POST_META else 'website'}">
<meta property="og:site_name" content="HypeApp">
<meta property="og:title" content="{html.escape(title.split(' | ')[0])}">
<meta property="og:description" content="{html.escape(desc)}">
{f'<meta property="og:url" content="{canon}">' if canon else ''}
<meta property="og:image" content="{BASE}/{(m or {}).get('img', 'og/padrao.jpg')}">
<meta property="og:image:width" content="{1200 if (m or {}).get('img', 'og/').startswith('og/') else 960}">
<meta property="og:image:height" content="{630 if (m or {}).get('img', 'og/').startswith('og/') else 600}">
<meta property="og:image:alt" content="{html.escape(og_alt((m or {}).get('img', 'og/padrao.jpg'), title))}">
<meta property="og:locale" content="pt_BR">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{html.escape(title.split(' | ')[0])}">
<meta name="twitter:description" content="{html.escape(desc)}">
<meta name="twitter:image" content="{BASE}/{(m or {}).get('img', 'og/padrao.jpg')}">
<meta name="theme-color" content="#EFEFEF">
<link rel="preload" href="{A('assets/fonts/inter-latin-wght-normal.woff2')}" as="font" type="font/woff2" crossorigin>
{f'<link rel="preload" as="image" type="image/webp" fetchpriority="high" href="{A(HX_TELAS["app"][0])}">' if url == '/' else ''}
<link rel="icon" href="{A('favicon.ico')}" sizes="48x48">
<link rel="icon" href="{A('icon-192.png')}" type="image/png" sizes="192x192">
<link rel="icon" href="{A('favicon.svg')}" type="image/svg+xml">
<link rel="apple-touch-icon" href="{A('apple-touch-icon.png')}">
<link rel="manifest" href="{A('site.webmanifest')}">
{f'<link rel="alternate" type="application/rss+xml" title="Blog HypeApp" href="{BASE}/blog/feed.xml">' if WEB and BLOG_ON and any(_p['status'] == 'publicado' for _p in POSTS) else ''}
<link rel="stylesheet" href="{A('assets/site.css')}?v={VER['site.css']}">
{f'<meta name="hh-gtm" content="{CFG["gtm"]}">' if ANALYTICS and CFG['gtm'] else ''}{f'<meta name="hh-ga4" content="{CFG["ga4"]}">' if ANALYTICS and CFG['ga4'] else ''}{f'<meta name="hh-clarity" content="{CFG["clarity"]}">' if ANALYTICS and CFG['clarity'] else ''}{f'<meta name="hh-ios-pt" content="{CFG["ios_pt"]}">' if WEB and CFG['ios_pt'] else ''}
{ld}'''
    if url == '/app' and WEB:
        pass
    inner = f'<a class="sr-only" href="#conteudo">Pular para o conteúdo</a>\n{aviso_cookies(L) if ANALYTICS else ""}{bar}\n{body}\n<script src="{A("assets/site.js")}?v={VER['site.js']}" defer></script>'
    is_root = url == '/'
    if is_root and not WEB:
        # A página principal da prévia é publicada sem esqueleto (a publicação acrescenta doctype, head e body).
        return head + '\n' + inner
    # email_off: impede o Cloudflare de esconder os e-mails (crawlers e IAs precisam ler o endereço no HTML)
    return f'<!doctype html>\n<html lang="pt-BR">\n<!--email_off-->\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n{head}\n</head>\n<body>\n{inner}\n</body>\n<!--/email_off-->\n</html>\n'

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
/Privacidade.html    /privacidade/            301
/privacidade.html    /privacidade/            301
/Privacidade         /privacidade/            301
/politica-de-privacidade.html  /privacidade/  301
/Termos.html         /termos/                 301
/termos.html         /termos/                 301
/Termos              /termos/                 301
/termos-de-uso.html  /termos/                 301
/influenciadores/*   /criadores/              301
'''

def csp_ga(h):
    """Domínios do Google Tag Manager, do GA4 e do modo de visualização do GTM (Tag Assistant), conforme o guia de CSP do Google."""
    add = {
        "script-src 'self'": "script-src 'self' https://*.googletagmanager.com https://tagmanager.google.com",
        "img-src 'self' data:": "img-src 'self' data: https://*.google-analytics.com https://*.googletagmanager.com https://ssl.gstatic.com https://www.gstatic.com",
        "style-src 'self' 'unsafe-inline'": "style-src 'self' 'unsafe-inline' https://*.googletagmanager.com https://tagmanager.google.com https://fonts.googleapis.com",
        "font-src 'self'": "font-src 'self' data: https://fonts.gstatic.com",
        "connect-src 'self'": "connect-src 'self' https://*.google-analytics.com https://*.analytics.google.com https://*.googletagmanager.com",
    }
    if CFG['clarity']:  # guia de CSP do Microsoft Clarity
        add = {k: v + (' https://*.clarity.ms https://c.bing.com' if k.split('-')[0] in ('script', 'img', 'connect') else '') for k, v in add.items()}
    for k, v in add.items():
        assert h.count(k) == 1, k
        h = h.replace(k, v)
    return h

HEADERS = '''/*
  Strict-Transport-Security: max-age=63072000
  X-Content-Type-Options: nosniff
  X-Frame-Options: DENY
  Referrer-Policy: strict-origin-when-cross-origin
  Permissions-Policy: camera=(), microphone=(), geolocation=(), interest-cohort=()
  Content-Security-Policy: default-src 'self'; img-src 'self' data:; style-src 'self' 'unsafe-inline'; script-src 'self'; font-src 'self'; connect-src 'self'; form-action 'self'; frame-ancestors 'none'; base-uri 'self'; object-src 'none'

/assets/fonts/*
  Cache-Control: public, max-age=31536000, immutable

/assets/site.css
  Cache-Control: public, max-age=31536000, immutable

/assets/site.js
  Cache-Control: public, max-age=31536000, immutable

/assets/telas/*
  Cache-Control: public, max-age=31536000, immutable

/assets/hero/*
  Cache-Control: public, max-age=31536000, immutable

/assets/como-funciona/*
  Cache-Control: public, max-age=31536000, immutable

/assets/carreira/*
  Cache-Control: public, max-age=31536000, immutable

/assets/menu/*
  Cache-Control: public, max-age=31536000, immutable

/assets/blog/*
  Cache-Control: public, max-age=31536000, immutable

/assets/ilustracoes/*
  Cache-Control: public, max-age=31536000, immutable

/assets/comunidade/*
  Cache-Control: public, max-age=31536000, immutable

/assets/parceiros/*
  Cache-Control: public, max-age=31536000, immutable

/og/*
  Cache-Control: public, max-age=86400
'''

def out_path(url):
    if url == '/':
        return 'index.html'
    if url == '/404':
        return '404.html'
    return url.strip('/') + '/index.html'

# ---------- Arquivos técnicos (só na versão --web) ----------
from html.parser import HTMLParser as _HP

class _Texto(_HP):
    """Converte o <main> de uma página em texto de leitura com títulos em Markdown (para o llms-full.txt).
    Ignora ilustrações e telas de demonstração (role=img, aria-hidden, hidden), formulários e botões."""
    BLOCO = {'p', 'li', 'h1', 'h2', 'h3', 'h4', 'summary', 'dt', 'dd', 'figcaption', 'blockquote', 'th', 'td'}
    PULA = {'script', 'style', 'svg', 'form', 'button', 'template', 'nav', 'select', 'textarea'}
    VAZIAS = {'img', 'input', 'br', 'hr', 'meta', 'link', 'source', 'wbr', 'col', 'area', 'base', 'embed', 'track'}
    def __init__(self):
        super().__init__(); self.dentro = False; self.pilha = []; self.pula = 0
        self.linhas = []; self.atual = ''; self.tag = ''
    def handle_starttag(self, t, a):
        if t in self.VAZIAS: return
        a = dict(a)
        pular = t in self.PULA or a.get('role') == 'img' or a.get('aria-hidden') == 'true' or 'hidden' in a \
            or 'browser-bar' in (a.get('class') or '') or 'sample' in (a.get('class') or '')
        self.pilha.append((t, pular))
        if pular: self.pula += 1
        if t == 'main': self.dentro = True
        if self.dentro and not self.pula and t in self.BLOCO: self.fecha(); self.tag = t
    def handle_endtag(self, t):
        if t in self.VAZIAS: return
        while self.pilha:
            tt, pular = self.pilha.pop()
            if pular: self.pula -= 1
            if tt == t: break
        if self.dentro and not self.pula and t in self.BLOCO: self.fecha()
        if t == 'main': self.fecha(); self.dentro = False
    def handle_data(self, d):
        if self.dentro and not self.pula and self.tag: self.atual += d
    def fecha(self):
        t = ' '.join(self.atual.split())
        if t and t not in ('Dados de exemplo.', 'Dados de exemplo'):
            pre = {'h1': '# ', 'h2': '## ', 'h3': '### ', 'h4': '#### ', 'summary': '**P:** ', 'li': '- ', 'dt': '- '}.get(self.tag, '')
            if not self.linhas or self.linhas[-1] != pre + t:
                self.linhas.append(pre + t)
        self.atual = ''; self.tag = ''

def _texto_da_pagina(html_txt):
    p = _Texto(); p.feed(html_txt); p.fecha()
    return '\n\n'.join(p.linhas)

def arquivos_tecnicos(OUT):
    # 1. Datas: grava o registro e acrescenta <lastmod> ao sitemap (só quando o conteúdo muda de verdade)
    json.dump(dict(sorted(DATAS.items())), open(DATAS_F, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    sm = os.path.join(OUT, 'sitemap.xml'); x = open(sm, encoding='utf-8').read()
    for _u in ('/legal/', '/regras-da-comunidade/'):
        if f'<loc>{BASE}{_u}</loc>' not in x:
            x = x.replace('</urlset>', f'  <url><loc>{BASE}{_u}</loc></url>\n</urlset>')
    x = re.sub(r'\s*<lastmod>[^<]*</lastmod>', '', x)
    x = x.replace('O CMS deve acrescentar <lastmod> quando o conteúdo mudar de verdade.', '<lastmod> = última mudança real do conteúdo (datas.json).')
    x = re.sub(r'gerado em \d{2}/\d{2}/\d{4} a partir da matriz de metadados', 'gerado a cada publicação a partir da matriz de metadados', x)
    def _lm(m):
        u = m.group(1)[len(BASE):]
        return m.group(0) + (f'<lastmod>{DATAS[u]["alterado"]}</lastmod>' if u in DATAS else '')
    x = re.sub(r'<loc>([^<]+)</loc>', _lm, x)
    open(sm, 'w', encoding='utf-8').write(x)
    urls = re.findall(r'<loc>([^<]+)</loc>', x)

    # 2. llms-full.txt: o texto completo das páginas públicas, na ordem do sitemap
    partes = [open(os.path.join(OUT, 'llms.txt'), encoding='utf-8').read().split('\n## ')[0].strip(), '']
    for full in urls:
        u = full[len(BASE):]
        f = os.path.join(OUT, out_path(u))
        if not os.path.exists(f):
            continue
        t = open(f, encoding='utf-8').read()
        titulo = html.unescape(re.search(r'<title>(.*?)</title>', t).group(1))
        partes.append(f'---\n\nFonte: {full}\nTítulo: {titulo}\nAtualizado em: {DATAS.get(u, {}).get("alterado", HOJE)}\n\n{_texto_da_pagina(t)}\n')
    open(os.path.join(OUT, 'llms-full.txt'), 'w', encoding='utf-8').write('\n'.join(partes))
    llms = os.path.join(OUT, 'llms.txt'); lt = open(llms, encoding='utf-8').read()
    if 'llms-full.txt' not in lt:
        lt = lt.rstrip() + f'\n\n## Texto completo\n\n- [llms-full.txt]({BASE}/llms-full.txt): o texto de todas as páginas públicas em um só arquivo.\n'
        open(llms, 'w', encoding='utf-8').write(lt)

    # 3. security.txt (RFC 9116), válido por um ano a partir da publicação
    exp = _dt.now(_Z('America/Sao_Paulo')).replace(microsecond=0)
    exp = exp.replace(year=exp.year + 1).isoformat()
    os.makedirs(os.path.join(OUT, '.well-known'), exist_ok=True)
    sec = (f'Contact: mailto:{EMAIL}\nExpires: {exp}\nPreferred-Languages: pt, en\n'
           f'Canonical: {BASE}/.well-known/security.txt\n')
    open(os.path.join(OUT, '.well-known', 'security.txt'), 'w', encoding='utf-8').write(sec)

    # 4. IndexNow: arquivo de chave na raiz (o envio é feito pelo GitHub Actions, ver README)
    chave = open(os.path.join(HERE, 'indexnow.key')).read().strip()
    open(os.path.join(OUT, chave + '.txt'), 'w').write(chave)

    # 5. RSS do blog, só com artigo publicado
    if BLOG_ON:
        from email.utils import format_datetime as _fd
        itens = ''
        for p in POSTS:
            if p['status'] != 'publicado':
                continue
            u = f"{BASE}/blog/{p['slug']}/"
            data = f"<pubDate>{_fd(_dt.combine(p['data'], _dt.min.time(), tzinfo=_Z('America/Sao_Paulo')))}</pubDate>" if p['data'] else ''
            itens += f"<item><title>{html.escape(p['titulo'])}</title><link>{u}</link><guid>{u}</guid>{data}<description>{html.escape(p['resumo'])}</description></item>"
        if itens:
            os.makedirs(os.path.join(OUT, 'blog'), exist_ok=True)
            open(os.path.join(OUT, 'blog', 'feed.xml'), 'w', encoding='utf-8').write(
                f'<?xml version="1.0" encoding="UTF-8"?><rss version="2.0"><channel><title>Blog HypeApp</title><link>{BASE}/blog/</link>'
                f'<description>Conteúdo para creators, marcas e agências.</description><language>pt-BR</language>{itens}</channel></rss>')

def main():
    if os.path.exists(OUT):
        shutil.rmtree(OUT)
    os.makedirs(os.path.join(OUT, 'assets'))
    for f in ('site.css', 'site.js', 'logo-hypeapp.svg', 'logo-hypeapp-branco.svg'):
        shutil.copy(os.path.join(HERE, 'assets', f), os.path.join(OUT, 'assets', f))
    if WEB:  # produção: CSS e JS minificados (pip install rcssmin rjsmin; sem eles, copia como está)
        try:
            import rcssmin, rjsmin
            for f, mini in (('site.css', rcssmin.cssmin), ('site.js', rjsmin.jsmin)):
                src = open(os.path.join(HERE, 'assets', f), encoding='utf-8').read()
                open(os.path.join(OUT, 'assets', f), 'w', encoding='utf-8').write(mini(src))
        except ImportError:
            print('aviso: rcssmin/rjsmin não instalados; CSS e JS saem sem minificar')
    shutil.copytree(os.path.join(HERE, 'assets', 'fonts'), os.path.join(OUT, 'assets', 'fonts'))
    shutil.copytree(os.path.join(HERE, 'assets', 'hero'), os.path.join(OUT, 'assets', 'hero'))
    shutil.copytree(os.path.join(HERE, 'assets', 'como-funciona'), os.path.join(OUT, 'assets', 'como-funciona'))
    shutil.copytree(os.path.join(HERE, 'assets', 'carreira'), os.path.join(OUT, 'assets', 'carreira'))
    shutil.copytree(os.path.join(HERE, 'assets', 'menu'), os.path.join(OUT, 'assets', 'menu'))
    shutil.copytree(os.path.join(HERE, 'assets', 'parceiros'), os.path.join(OUT, 'assets', 'parceiros'))
    shutil.copytree(os.path.join(HERE, 'assets', 'ilustracoes'), os.path.join(OUT, 'assets', 'ilustracoes'))  # biblioteca roxa (página de creators)
    shutil.copytree(os.path.join(HERE, 'assets', 'comunidade'), os.path.join(OUT, 'assets', 'comunidade'))  # avatares do chat da comunidade
    shutil.copytree(os.path.join(HERE, 'assets', 'email'), os.path.join(OUT, 'assets', 'email'))  # logo em PNG para os e-mails de confirmação
    os.makedirs(os.path.join(OUT, 'assets', 'blog'))
    for _p in POSTS:
        shutil.copy(os.path.join(HERE, 'assets', 'blog', _p['capa']), os.path.join(OUT, 'assets', 'blog', _p['capa']))
    shutil.copytree(os.path.join(HERE, 'assets', 'blog', 'autores'), os.path.join(OUT, 'assets', 'blog', 'autores'))  # fotos da equipe do blog
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
        used.update(re.findall(r'assets/telas/([\w-]+\.webp)', page))
        page = versiona(page)
        open(p, 'w', encoding='utf-8').write(page)
    for f in sorted(used):  # só as telas usadas nas páginas
        shutil.copy(os.path.join(HERE, 'assets', 'telas', f), os.path.join(OUT, 'assets', 'telas', f))
    if WEB:
        seo = os.path.join(HERE, '..', 'seo', 'out')
        for f in ('robots.txt', 'robots-homologacao.txt', 'sitemap.xml', 'llms.txt'):
            shutil.copy(os.path.join(seo, f), os.path.join(OUT, f))
        if BLOG_ON:  # o blog entra no sitemap só com artigo publicado
            sm = os.path.join(OUT, 'sitemap.xml'); x = open(sm, encoding='utf-8').read()
            urls = (['/blog/'] if PUBLICADOS else []) + ['/blog/' + _p['slug'] + '/' for _p in PUBLICADOS]
            x = x.replace('</urlset>', ''.join(f'  <url><loc>{BASE}{u}</loc></url>\n' for u in urls) + '</urlset>')
            open(sm, 'w', encoding='utf-8').write(x)
        arquivos_tecnicos(OUT)
        open(os.path.join(OUT, '_redirects'), 'w').write(REDIRECTS)
        open(os.path.join(OUT, '_so_teste.json'), 'w').write(json.dumps(SO_TESTE))
        open(os.path.join(OUT, '_headers'), 'w').write(csp_ga(HEADERS) if ANALYTICS else HEADERS)
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
