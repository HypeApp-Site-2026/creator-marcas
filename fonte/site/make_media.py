# -*- coding: utf-8 -*-
"""Gera ícones, manifest e imagens sociais (Open Graph) em site/static/.

Uso: python3 make_media.py   (rodar de novo quando mudar título de página principal ou tela)
Precisa de: playwright (Python) e Pillow.
As imagens sociais usam a fonte Inter do próprio site e telas reais de assets/telas/
(nunca app-C1, app-C4, app-G8 nem a barra lateral do painel com "Admin da plataforma").
"""
import json, os, re, shutil, sys, base64
from io import BytesIO
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'seo'))
sys.path.insert(0, HERE)
from data import R  # noqa: E402

OUT = os.path.join(HERE, 'static')
INK, PURPLE, GROUND = '#050505', '#9E2CFA', '#EFEFEF'

# ---------- Marca: o "h" + sorriso roxo, recortados da logo oficial ----------
logo = open(os.path.join(HERE, 'assets', 'logo-hypeapp.svg'), encoding='utf-8').read()
paths = re.findall(r'<path class="(cls-\d)" d="([^"]+)"', logo)
H_PATH = next(d for c, d in paths if d.startswith('M141.12'))
SMILE = next(d for c, d in paths if c == 'cls-1')

def mark_svg(bg=True, pad=0.18, radius=0.22):
    # recorte da marca: x 1..181, y 1..363 (unidades da logo)
    size = 362 / (1 - 2 * pad)
    x0, y0 = 91 - size / 2, 182 - size / 2
    rect = (f'<rect x="{x0:.1f}" y="{y0:.1f}" width="{size:.1f}" height="{size:.1f}" rx="{size*radius:.1f}" fill="#FFFFFF"/>' if bg else '')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{x0:.1f} {y0:.1f} {size:.1f} {size:.1f}">{rect}'
            f'<path fill="{INK}" d="{H_PATH}"/><path fill="{PURPLE}" d="{SMILE}"/></svg>')

def font_b64():
    return base64.b64encode(open(os.path.join(HERE, 'assets', 'fonts', 'inter-latin-wght-normal.woff2'), 'rb').read()).decode()

def img_b64(code, crop=None):
    im = Image.open(os.path.join(HERE, 'assets', 'telas', code + '.webp')).convert('RGB')
    if crop:
        im = im.crop(crop)
    b = BytesIO(); im.save(b, 'PNG'); return 'data:image/png;base64,' + base64.b64encode(b.getvalue()).decode()

# ---------- Imagens sociais ----------
# (selo, título, visual, tema)
# visual: ('phones', [a, b]) dois celulares · ('phone', a) um celular grande inclinado · ('web', tela) painel
#         ('combo', tela_web, tela_app) painel com um celular na frente
# tema: 'claro' (cartão branco), 'escuro' (cartão preto), 'roxo' (cartão roxo)
# Telas reais de assets/telas (nunca app-C1, app-C4, app-G8 nem a lateral do painel com Administração).
OG = {
    'og/padrao.jpg':         ('HypeApp', 'Creators e marcas, do convite ao pagamento.', ('phones', ['app-D1', 'app-F1']), 'claro'),
    'og/inicio.jpg':         ('App e painel', 'Creators e marcas. Campanhas que conectam.', ('combo', 'bo-n01', 'app-E4'), 'escuro'),
    'og/para-criadores.jpg': ('Para creators', 'Sua carreira de creator, mais organizada.', ('phones', ['app-E4', 'app-H1']), 'roxo'),
    'og/para-marcas.jpg':    ('Para marcas e agências', 'Gerencie suas campanhas com creators em um só painel.', ('web', 'bo-n03a'), 'escuro'),
    'og/baixar.jpg':         ('Disponível para iPhone e Android', 'Sua próxima conexão começa no HypeApp.', ('phone', 'app-B7'), 'roxo'),
    'og/sobre.jpg':          ('Da Você no Hype', 'A experiência da Você no Hype conectando creators e marcas.', ('combo', 'bo-n02', 'app-F2'), 'claro'),
    'og/ajuda.jpg':          ('Perguntas frequentes', 'Tire suas dúvidas sobre o HypeApp.', ('ilustra', 'ajuda'), 'claro'),
    'og/suporte.jpg':        ('Suporte', 'Precisa de ajuda? Fale com o suporte.', ('ilustra', 'suporte'), 'escuro'),
    'og/contato.jpg':        ('Contato', 'Vamos conversar sobre o que você precisa.', ('ilustra', 'contato'), 'roxo'),
    'og/legal.jpg':          ('Documentos legais', 'Privacidade, termos e proteção dos seus dados.', ('ilustra', 'legal'), 'claro'),
    'og/blog.jpg':           ('Blog', 'Ideias para sua próxima fase.', ('blog', None), 'escuro'),
}

# Ilustrações simples no desenho do HypeApp (formas arredondadas, roxo, preto e branco), sem telas nem dados
I_PATH = {
    'mais': 'M12 5v14M5 12h14', 'check': 'M5 12.5l4.5 4.5L19 7.5',
    'headset': 'M4 14v-2a8 8 0 0 1 16 0v2M4 14a2 2 0 0 1 2-2h1v6H6a2 2 0 0 1-2-2zM20 14a2 2 0 0 0-2-2h-1v6h1a2 2 0 0 0 2-2zM18 18v1a3 3 0 0 1-3 3h-3',
}
def _ico(d, cor, tam=34, w=2.4):
    return f'<svg width="{tam}" height="{tam}" viewBox="0 0 24 24" fill="none" stroke="{cor}" stroke-width="{w}" stroke-linecap="round" stroke-linejoin="round"><path d="{d}"/></svg>'
def ilustra(tipo):
    if tipo == 'ajuda':
        rows = ''.join(f'<div class="faq-r"><i style="width:{w}px"></i><span>{_ico(I_PATH["mais"], INK, 22)}</span></div>' for w in (230, 180, 250, 150))
        return f'<div class="il"><div class="pn faq">{rows}</div><div class="bub roxo q">?</div></div>'
    if tipo == 'suporte':
        return ('<div class="il"><div class="pn chat1"><i style="width:250px"></i><i style="width:190px"></i><i style="width:120px"></i></div>'
                '<div class="bub roxo dots"><b></b><b></b><b></b></div>'
                f'<div class="badge">{_ico(I_PATH["headset"], "#FFFFFF", 68, 2)}</div></div>')
    if tipo == 'contato':
        return ('<div class="il"><div class="env"><svg viewBox="0 0 360 240" width="360" height="240"><rect x="4" y="4" width="352" height="232" rx="34" fill="#FFFFFF"/>'
                f'<path d="M24 34l156 112L336 34" fill="none" stroke="{INK}" stroke-width="12" stroke-linecap="round" stroke-linejoin="round"/></svg></div>'
                '<div class="pn chat2"><i style="width:170px"></i><i style="width:120px"></i></div><div class="bub preto dots"><b></b><b></b><b></b></div></div>')
    if tipo == 'legal':
        linhas = ''.join(f'<i style="width:{w}px"></i>' for w in (200, 240, 220, 170, 230, 140))
        return (f'<div class="il"><div class="pn doc"><b class="dt"></b>{linhas}</div>'
                f'<div class="shield"><svg viewBox="0 0 120 140" width="170" height="198"><path d="M60 6l50 18v38c0 34-22 60-50 72C32 122 10 96 10 62V24z" fill="{PURPLE}"/></svg>'
                f'<span>{_ico(I_PATH["check"], "#FFFFFF", 70, 3)}</span></div></div>')
    return ''

TEMAS = {
    'claro':  {'card': '#FFFFFF', 'tx': INK, 'url': '#5B5B5B', 'tag_bg': PURPLE, 'tag_tx': '#FFFFFF', 'logo': 'normal'},
    'escuro': {'card': '#0A0A0A', 'tx': '#FFFFFF', 'url': '#A3A3A3', 'tag_bg': PURPLE, 'tag_tx': '#FFFFFF', 'logo': 'branco'},
    'roxo':   {'card': PURPLE, 'tx': '#FFFFFF', 'url': '#EBD9FF', 'tag_bg': '#FFFFFF', 'tag_tx': INK, 'logo': 'branco'},
}

def web_crop(code):
    w, h = Image.open(os.path.join(HERE, 'assets', 'telas', code + '.webp')).size
    return (225, 0, w, h) if code.startswith('bo-n') else (280, 0, 1400, 875)  # sem a barra lateral

def og_html(tag, title, visual, tema='claro'):
    T = TEMAS[tema]
    logo_src = logo if T['logo'] == 'normal' else open(os.path.join(HERE, 'assets', 'logo-hypeapp-branco.svg'), encoding='utf-8').read()
    if tema == 'roxo':  # no fundo roxo, o sorriso também fica branco
        logo_src = logo_src.replace('fill: #9e2cfa;', 'fill: #fff;')
    logo_uri = 'data:image/svg+xml;base64,' + base64.b64encode(logo_src.encode()).decode()
    if visual[0] == 'phones':
        a, b = visual[1]
        vis = f'''<div class="ph p1"><img src="{img_b64(a)}"></div><div class="ph p2"><img src="{img_b64(b)}"></div>'''
    elif visual[0] == 'phone':
        vis = f'''<div class="ph pbig"><img src="{img_b64(visual[1])}"></div>'''
    elif visual[0] == 'combo':
        vis = (f'''<div class="web wcombo"><img src="{img_b64(visual[1], web_crop(visual[1]))}"></div>'''
               f'''<div class="ph pcombo"><img src="{img_b64(visual[2])}"></div>''')
    elif visual[0] == 'ilustra':
        vis = ilustra(visual[1])
    elif visual[0] == 'blog':
        capa = visual[1]
        if capa:
            b64 = base64.b64encode(open(os.path.join(HERE, 'assets', 'blog', capa), 'rb').read()).decode()
            vis = f'<div class="capa"><img src="data:image/webp;base64,{b64}"></div>'
        else:  # página do blog: três cartões de artigo, sem texto
            vis = '<div class="il"><div class="bc b1"></div><div class="bc b2"></div><div class="bc b3"></div></div>'
    else:
        vis = f'''<div class="web"><img src="{img_b64(visual[1], web_crop(visual[1]))}"></div>'''
    return f'''<!doctype html><html><head><meta charset="utf-8"><style>
@font-face {{ font-family: Inter; src: url(data:font/woff2;base64,{font_b64()}) format("woff2"); font-weight: 100 900; }}
* {{ box-sizing: border-box; margin: 0; }}
body {{ width: 1200px; height: 630px; background: {GROUND}; font-family: Inter, sans-serif; color: {T['tx']}; overflow: hidden; }}
.card {{ position: absolute; inset: 32px; background: {T['card']}; border-radius: 32px; overflow: hidden; }}
.txt {{ position: absolute; left: 64px; top: 60px; width: 560px; height: 446px; display: flex; flex-direction: column; }}
.logo {{ width: 128px; height: auto; }}
.tag {{ align-self: flex-start; margin-top: auto; background: {T['tag_bg']}; color: {T['tag_tx']}; font-weight: 600; font-size: 22px; padding: 9px 20px; border-radius: 999px; }}
h1 {{ font-weight: 600; font-size: 58px; line-height: 1.04; letter-spacing: -0.035em; margin-top: 22px; }}
.url {{ margin-top: 26px; font-size: 22px; font-weight: 500; color: {T['url']}; }}
.ph {{ position: absolute; width: 236px; height: 510px; border-radius: 40px; background: {INK}; padding: 9px; box-shadow: 0 30px 60px rgba(0,0,0,.22); border: 2px solid rgba(255,255,255,.14); }}
.ph img {{ width: 100%; height: 100%; object-fit: cover; object-position: top; border-radius: 32px; display: block; }}
.p1 {{ left: 690px; top: 48px; }}
.p2 {{ left: 900px; top: 110px; }}
.pbig {{ left: 760px; top: 46px; width: 262px; height: 566px; transform: rotate(-6deg); }}
.web {{ position: absolute; left: 676px; top: 70px; width: 640px; height: 480px; border-radius: 22px; overflow: hidden; background: {GROUND}; box-shadow: 0 30px 60px rgba(0,0,0,.2); border: 8px solid {INK}; }}
.web img {{ width: 100%; display: block; }}
.wcombo {{ left: 700px; top: 56px; width: 620px; height: 400px; }}
.pcombo {{ left: 640px; top: 220px; width: 190px; height: 410px; border-radius: 34px; padding: 7px; }}
.pcombo img {{ border-radius: 28px; }}
.nota {{ font-size: 15px; font-weight: 500; opacity: .75; }}
.il {{ position: absolute; left: 660px; top: 0; width: 476px; height: 566px; }}
.pn {{ position: absolute; background: #FFFFFF; border-radius: 30px; box-shadow: 0 30px 60px rgba(0,0,0,.14); display: flex; flex-direction: column; gap: 18px; padding: 30px; }}
.pn i {{ display: block; height: 16px; border-radius: 999px; background: #E6E6E6; }}
.faq {{ left: 20px; top: 120px; width: 400px; gap: 14px; padding: 22px; background: {GROUND}; }}
.faq-r {{ display: flex; align-items: center; justify-content: space-between; background: #FFFFFF; border-radius: 20px; padding: 20px 22px; }}
.faq-r i {{ background: #D9D9D9; }}
.faq-r span {{ width: 40px; height: 40px; border-radius: 50%; background: {GROUND}; display: flex; align-items: center; justify-content: center; }}
.bub {{ position: absolute; border-radius: 40px; display: flex; align-items: center; justify-content: center; gap: 12px; box-shadow: 0 24px 50px rgba(0,0,0,.18); }}
.bub.roxo {{ background: {PURPLE}; color: #FFFFFF; }}
.bub.preto {{ background: {INK}; color: #FFFFFF; }}
.q {{ right: 30px; top: 50px; width: 150px; height: 150px; border-radius: 50% 50% 50% 16px; font-size: 96px; font-weight: 700; }}
.dots b {{ width: 18px; height: 18px; border-radius: 50%; background: currentColor; display: block; }}
.chat1 {{ left: 40px; top: 70px; width: 360px; border-radius: 30px 30px 30px 10px; }}
.suporte {{}}
.il .dots {{ width: 150px; height: 84px; }}
.chat1 + .dots {{ right: 40px; top: 270px; border-radius: 40px 40px 10px 40px; }}
.badge {{ position: absolute; left: 70px; top: 330px; width: 150px; height: 150px; border-radius: 50%; background: {PURPLE}; display: flex; align-items: center; justify-content: center; box-shadow: 0 24px 50px rgba(0,0,0,.3); border: 4px solid #FFFFFF; }}
.env {{ position: absolute; left: 40px; top: 70px; filter: drop-shadow(0 30px 50px rgba(0,0,0,.18)); }}
.chat2 {{ left: 170px; top: 300px; width: 260px; border-radius: 30px 30px 10px 30px; padding: 26px; }}
.chat2 + .dots {{ left: 40px; top: 400px; border-radius: 40px 40px 40px 10px; }}
.doc {{ left: 40px; top: 60px; width: 330px; height: 430px; gap: 20px; }}
.doc .dt {{ width: 120px; height: 22px; border-radius: 999px; background: {INK}; display: block; margin-bottom: 10px; }}
.shield {{ position: absolute; right: 30px; top: 290px; filter: drop-shadow(0 24px 40px rgba(0,0,0,.22)); }}
.shield span {{ position: absolute; left: 50%; top: 46%; transform: translate(-50%, -50%); }}
.capa {{ position: absolute; left: 640px; top: 70px; width: 470px; height: 426px; border-radius: 26px; overflow: hidden; box-shadow: 0 30px 60px rgba(0,0,0,.25); }}
.capa img {{ width: 100%; height: 100%; object-fit: cover; display: block; }}
.bc {{ position: absolute; width: 300px; height: 340px; border-radius: 28px; background: #FFFFFF; box-shadow: 0 24px 50px rgba(0,0,0,.3); }}
.bc::before {{ content: ""; position: absolute; left: 14px; right: 14px; top: 14px; height: 170px; border-radius: 18px; background: {PURPLE}; }}
.bc::after {{ content: ""; position: absolute; left: 24px; top: 210px; width: 200px; height: 18px; border-radius: 999px; background: #D9D9D9; box-shadow: 0 34px 0 -2px #E6E6E6, 0 68px 0 -4px #EDEDED; }}
.b1 {{ left: 0px; top: 150px; transform: rotate(-8deg); }}
.b2 {{ left: 80px; top: 90px; transform: rotate(-2deg); }}
.b2::before {{ background: #050505; }}
.b3 {{ left: 150px; top: 130px; transform: rotate(6deg); }}
.b3::before {{ background: #EFEFEF; }}
</style></head><body><div class="card">
<div class="txt"><img class="logo" src="{logo_uri}"><span class="tag">{tag}</span><h1>{title}</h1><div class="url">hypeapp.com.br{'<span class="nota"> · Interface e dados ilustrativos</span>' if visual[0] in ('phones', 'phone', 'web', 'combo') else ''}</div></div>
{vis}</div></body></html>'''

def main():
    from playwright.sync_api import sync_playwright
    if os.path.exists(OUT):
        shutil.rmtree(OUT)
    os.makedirs(os.path.join(OUT, 'og'))
    # favicon.svg
    open(os.path.join(OUT, 'favicon.svg'), 'w', encoding='utf-8').write(mark_svg())
    used = {r['img'] for r in R} | {'og/padrao.jpg'}
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={'width': 512, 'height': 512})
        def raster(svg, size, name):
            pg.set_viewport_size({'width': size, 'height': size})
            pg.set_content(f'<html><body style="margin:0;background:transparent">{svg.replace("<svg ", f"<svg width=\"{size}\" height=\"{size}\" ", 1)}</body></html>')
            pg.screenshot(path=os.path.join(OUT, name), omit_background=True, clip={'x': 0, 'y': 0, 'width': size, 'height': size})
        raster(mark_svg(), 512, 'icon-512.png')
        raster(mark_svg(), 192, 'icon-192.png')
        raster(mark_svg(radius=0, pad=0.24), 512, 'icon-maskable-512.png')
        raster(mark_svg(radius=0, pad=0.16), 180, 'apple-touch-icon.png')
        Image.open(os.path.join(OUT, 'icon-512.png')).save(os.path.join(OUT, 'favicon.ico'), sizes=[(16, 16), (32, 32), (48, 48)])
        # imagens sociais
        pg.set_viewport_size({'width': 1200, 'height': 630})
        made = []
        import blog_build as _blog
        lista = dict(OG)
        for _p in _blog.load_posts(HERE, False):
            lista['og/blog/' + _p['slug'] + '.jpg'] = (_p['categoria'], _p['titulo'], ('blog', _p['capa']), 'claro')
        os.makedirs(os.path.join(OUT, 'og', 'blog'), exist_ok=True)
        for name, (tag, title, visual, tema) in lista.items():
            pg.set_content(og_html(tag, title, visual, tema), wait_until='load')
            pg.wait_for_timeout(150)
            png = pg.screenshot(clip={'x': 0, 'y': 0, 'width': 1200, 'height': 630})
            Image.open(BytesIO(png)).convert('RGB').save(os.path.join(OUT, name), 'JPEG', quality=86, optimize=True, progressive=True)
            made.append(name)
        b.close()
    missing = sorted(u for u in used if u not in OG and '{' not in u)
    json.dump({
        'name': 'HypeApp', 'short_name': 'HypeApp', 'lang': 'pt-BR', 'start_url': '/', 'display': 'browser',
        'background_color': GROUND, 'theme_color': GROUND,
        'icons': [{'src': '/icon-192.png', 'sizes': '192x192', 'type': 'image/png'},
                  {'src': '/icon-512.png', 'sizes': '512x512', 'type': 'image/png'},
                  {'src': '/icon-maskable-512.png', 'sizes': '512x512', 'type': 'image/png', 'purpose': 'maskable'}]},
        open(os.path.join(OUT, 'site.webmanifest'), 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    print('ok', len(made), 'imagens sociais;', 'sem imagem própria (páginas futuras):', ', '.join(missing))

if __name__ == '__main__':
    main()
