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
# url da página -> (selo, título, visual)  · visual: ('phones', [telas]) | ('web', tela)
# (selo, título, visual, selo do TikTok Shop) · telas do painel de novembro/2026 (bo-n*)
OG = {
    'og/padrao.jpg':         ('HypeApp', 'Campanhas entre creators e marcas, do convite ao pagamento.', ('phones', ['app-E4', 'app-G2']), False),
    'og/inicio.jpg':         ('App e painel', 'O app de quem cria conteúdo. O painel de quem contrata.', ('phones', ['app-E4', 'app-G2']), True),
    'og/para-criadores.jpg': ('Para creators', 'Campanhas com marcas, entregas e pagamento no app.', ('phones', ['app-D1', 'app-G2']), False),
    'og/para-marcas.jpg':    ('Para marcas e agências', 'Campanhas com influenciadores em um só painel.', ('web', 'bo-n01'), True),
    'og/baixar.jpg':         ('Grátis · iPhone e Android', 'Baixe o HypeApp na App Store ou no Google Play.', ('phones', ['app-D1', 'app-E4']), False),
    'og/sobre.jpg':          ('Da Você no Hype', 'A plataforma de campanhas entre creators e marcas.', ('phones', ['app-E4', 'app-G2']), True),
    'og/ajuda.jpg':          ('Perguntas frequentes', 'Campanhas, pagamento via PIX, conta e segurança.', ('phones', ['app-G2', 'app-E4']), False),
    'og/suporte.jpg':        ('Suporte', 'Abra um chamado de segunda a sexta, das 10h às 18h.', ('phones', ['app-E4', 'app-D1']), False),
    'og/contato.jpg':        ('Contato', 'Comercial, suporte e privacidade em um só lugar.', ('web', 'bo-n02'), False),
    'og/legal.jpg':          ('Documentos legais', 'Privacidade, termos e seus direitos sobre dados.', ('phones', ['app-D1', 'app-G2']), False),
}

def og_html(tag, title, visual, parceiro=False):
    logo_uri = 'data:image/svg+xml;base64,' + base64.b64encode(logo.encode()).decode()
    if visual[0] == 'phones':
        a, b = visual[1]
        vis = f'''<div class="ph p1"><img src="{img_b64(a)}"></div><div class="ph p2"><img src="{img_b64(b)}"></div>'''
    else:
        im_w = Image.open(os.path.join(HERE, 'assets', 'telas', visual[1] + '.webp')).size
        crop = (225, 0, im_w[0], im_w[1]) if visual[1].startswith('bo-n') else (280, 0, 1400, 875)  # sem a barra lateral
        vis = f'''<div class="web"><img src="{img_b64(visual[1], crop)}"></div>'''
    tts = ''
    if parceiro:  # selo oficial, sem alteração, sobre fundo branco
        b64 = base64.b64encode(open(os.path.join(HERE, 'assets', 'parceiros', 'tiktok-shop-partner.webp'), 'rb').read()).decode()
        tts = f'<img class="tts" src="data:image/webp;base64,{b64}" alt="">'
    return f'''<!doctype html><html><head><meta charset="utf-8"><style>
@font-face {{ font-family: Inter; src: url(data:font/woff2;base64,{font_b64()}) format("woff2"); font-weight: 100 900; }}
* {{ box-sizing: border-box; margin: 0; }}
body {{ width: 1200px; height: 630px; background: {GROUND}; font-family: Inter, sans-serif; color: {INK}; overflow: hidden; }}
.card {{ position: absolute; inset: 32px; background: #fff; border-radius: 32px; overflow: hidden; }}
.txt {{ position: absolute; left: 64px; top: 60px; width: 560px; height: 446px; display: flex; flex-direction: column; }}
.logo {{ width: 128px; height: auto; }}
.tag {{ align-self: flex-start; margin-top: auto; background: {PURPLE}; color: #fff; font-weight: 600; font-size: 22px; padding: 9px 20px; border-radius: 999px; }}
h1 {{ font-weight: 600; font-size: 58px; line-height: 1.04; letter-spacing: -0.035em; margin-top: 22px; }}
.url {{ margin-top: 26px; font-size: 22px; font-weight: 500; color: #5b5b5b; }}
.ph {{ position: absolute; width: 236px; height: 510px; border-radius: 40px; background: {INK}; padding: 9px; box-shadow: 0 30px 60px rgba(0,0,0,.18); }}
.ph img {{ width: 100%; height: 100%; object-fit: cover; object-position: top; border-radius: 32px; display: block; }}
.p1 {{ left: 690px; top: 48px; }}
.p2 {{ left: 900px; top: 110px; }}
.web {{ position: absolute; left: 676px; top: 70px; width: 640px; height: 480px; border-radius: 22px; overflow: hidden; background: {GROUND}; box-shadow: 0 30px 60px rgba(0,0,0,.16); border: 8px solid {INK}; }}
.web img {{ width: 100%; display: block; }}
.tts {{ position: absolute; right: 24px; top: 2px; width: 168px; height: auto; }}
</style></head><body><div class="card">
<div class="txt"><img class="logo" src="{logo_uri}"><span class="tag">{tag}</span><h1>{title}</h1><div class="url">hypeapp.com.br</div>{tts}</div>
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
        for name, (tag, title, visual, parceiro) in OG.items():
            pg.set_content(og_html(tag, title, visual, parceiro), wait_until='load')
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
