"""Telas vivas da hero: demonstrações em loop do app (iPhone) e do painel (MacBook), em HTML.

Ficam por cima das imagens tela-app.webp e tela-painel.webp, que continuam no HTML (texto alternativo, sem JavaScript
e movimento reduzido). Só aparecem com .hx-live; o site.js escala cada tela e roda a demonstração só com a cena parada
e visível na tela. Fluxos (apenas telas e textos que existem no app e no painel):
- app: Descobrir > campanha > Quero participar > Minhas inscrições (em análise > aprovada) > Roteiro (digita e envia)
  > aguardando aprovação > campanha concluída, pagamento liberado na carteira;
- painel: Campanhas > Verão Glow (progresso e etapas) > Criadores > Convidar dois creators > Campanhas.
Marcas, creators e números são de exemplo. Estilos: bloco "Telas vivas" no site.css; roteiro: DEMO_APP/DEMO_PLAT no site.js.
"""

# ---------- ilustrações das campanhas (SVG, estilo chapado do app; ids com prefixo para não colidir) ----------
def _svg(body, defs):
    return (f'<svg class="ls-art" viewBox="0 0 400 300" preserveAspectRatio="xMidYMid slice" aria-hidden="true" focusable="false">'
            f'<defs>{defs}</defs>{body}</svg>')

def _grad(i, a, b):
    return f'<linearGradient id="{i}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{a}"/><stop offset="1" stop-color="{b}"/></linearGradient>'

ART = {
    'lume': _svg('''<rect width="400" height="300" fill="url(#ls-g1)"/><path d="M95 300V120a105 105 0 0 1 210 0v180z" fill="#fff" opacity=".28"/>
<ellipse cx="200" cy="262" rx="190" ry="44" fill="#A655C8"/><ellipse cx="200" cy="250" rx="150" ry="22" fill="#B86AD6"/>
<rect x="128" y="128" width="62" height="122" rx="16" fill="#fff"/><rect x="140" y="100" width="38" height="34" rx="8" fill="#2A0B3B"/>
<rect x="141" y="160" width="36" height="36" rx="8" fill="#EFE2FF"/><circle cx="159" cy="178" r="8" fill="#9E2CFA"/>
<rect x="200" y="96" width="54" height="154" rx="14" fill="#F9C6E6"/><rect x="214" y="150" width="26" height="44" rx="6" fill="#fff" opacity=".55"/>
<rect x="219" y="66" width="16" height="32" fill="#2A0B3B"/><rect x="211" y="58" width="44" height="13" rx="6.5" fill="#2A0B3B"/>
<rect x="264" y="180" width="72" height="70" rx="14" fill="#fff"/><rect x="258" y="166" width="84" height="22" rx="11" fill="#D2F51A"/>''',
                 _grad('ls-g1', '#F8DDF0', '#C47BE0')),
    'aurora': _svg('''<rect width="400" height="300" fill="url(#ls-g2)"/><path d="M250 300V70a70 70 0 0 1 140 0v230z" fill="#F9D8C2" opacity=".85"/>
<path d="M320 2v298M250 150h140" stroke="#E9A985" stroke-width="7"/><rect x="0" y="236" width="400" height="64" fill="#5B1E3B"/>
<ellipse cx="200" cy="238" rx="210" ry="22" fill="#6E2747"/><ellipse cx="110" cy="246" rx="62" ry="12" fill="#F7E7CF"/><ellipse cx="110" cy="244" rx="40" ry="6" fill="#EAD3B4"/>
<ellipse cx="300" cy="250" rx="62" ry="12" fill="#F7E7CF"/><ellipse cx="300" cy="248" rx="40" ry="6" fill="#EAD3B4"/>
<path d="M150 108c10-2 14 20 30 60M196 72v96M240 124c-14 6-30 24-36 44" stroke="#2A0B2A" stroke-width="5" fill="none" stroke-linecap="round"/>
<circle cx="146" cy="104" r="17" fill="#A44BF0"/><circle cx="196" cy="68" r="17" fill="#CBF21E"/><circle cx="244" cy="120" r="14" fill="#fff"/>
<path d="M176 160h44l-6 22c8 14 10 34 6 54h-44c-4-20-2-40 6-54z" fill="#FCF0DC"/>''',
                   _grad('ls-g2', '#F3BE98', '#E2876A')),
    'brisa': _svg('''<rect width="400" height="300" fill="url(#ls-g3)"/><circle cx="90" cy="60" r="95" fill="#FBFDE8" opacity=".55"/>
<ellipse cx="200" cy="268" rx="120" ry="14" fill="#5E8E25" opacity=".55"/><path d="M136 92h128l-14 172a8 8 0 0 1-8 7h-84a8 8 0 0 1-8-7z" fill="#fff" opacity=".35"/>
<path d="M143 150h114l-9 112a7 7 0 0 1-7 6h-82a7 7 0 0 1-7-6z" fill="#F99A2C"/><path d="M214 150 238 18" stroke="#9E2CFA" stroke-width="11" stroke-linecap="round"/>
<circle cx="276" cy="92" r="40" fill="#F59A2A"/><circle cx="276" cy="92" r="31" fill="#FFC15E"/>
<path d="M276 61v62M245 92h62M254 70l44 44M298 70l-44 44" stroke="#F59A2A" stroke-width="3"/>''',
                  _grad('ls-g3', '#DDF0A2', '#79AF37')),
    'run': _svg('''<rect width="400" height="300" fill="url(#ls-g4)"/><circle cx="318" cy="70" r="74" fill="#F6F8CC"/>
<path d="M0 214C80 168 160 176 240 200S360 214 400 190V300H0z" fill="#4FAE67"/><path d="M0 252C110 222 220 236 400 226V300H0z" fill="#2F7E4A"/>
<path d="M44 130h70M24 160h82M58 190h60" stroke="#fff" stroke-width="7" stroke-linecap="round" opacity=".85"/>
<circle cx="214" cy="78" r="22" fill="#1A0A1F"/><path d="M226 76h30" stroke="#D2F51A" stroke-width="7" stroke-linecap="round"/>
<path d="M206 104l-16 70M200 130l40 18 22-24M200 130l-30 24-24-6M190 174l34 32 4 42M190 174l-26 40-38 6" stroke="#1A0A1F" stroke-width="14" fill="none" stroke-linecap="round" stroke-linejoin="round"/>''',
                _grad('ls-g4', '#CDEC95', '#9BD26A')),
}
AV_PACE = ('<svg class="ls-av" viewBox="0 0 40 40" aria-hidden="true" focusable="false"><circle cx="20" cy="20" r="20" fill="#14361F"/>'
           '<path d="M12 27l7-14 5 9 4-6" stroke="#D2F51A" stroke-width="3.4" fill="none" stroke-linecap="round" stroke-linejoin="round"/></svg>')

def _ic(paths, size, sw=2):
    return (f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="{sw}" '
            f'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false">{paths}</svg>')

I = {
    'home': '<path d="M15 21v-8a1 1 0 0 0-1-1h-4a1 1 0 0 0-1 1v8"/><path d="M3 10a2 2 0 0 1 .709-1.528l7-5.999a2 2 0 0 1 2.582 0l7 5.999A2 2 0 0 1 21 10v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>',
    'mega': '<path d="m3 11 18-5v12L3 14v-3z"/><path d="M11.6 16.8a3 3 0 1 1-5.8-1.6"/>',
    'users': '<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>',
    'user': '<path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/>',
    'upload': '<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><path d="m17 8-5-5-5 5"/><path d="M12 3v12"/>',
    'clock': '<circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/>',
    'check': '<path d="M20 6 9 17l-5-5"/>',
    'grid': '<rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/>',
    'video': '<path d="m16 13 5.223 3.482a.5.5 0 0 0 .777-.416V7.87a.5.5 0 0 0-.752-.432L16 10.5"/><rect x="2" y="6" width="14" height="12" rx="2"/>',
    'wallet': '<path d="M19 7V4a1 1 0 0 0-1-1H5a2 2 0 0 0 0 4h15a1 1 0 0 1 1 1v4h-3a2 2 0 0 0 0 4h3a1 1 0 0 0 1-1v-2a1 1 0 0 0-1-1"/><path d="M3 5v14a2 2 0 0 0 2 2h15a1 1 0 0 0 1-1v-4"/>',
    'chev': '<path d="m9 18 6-6-6-6"/>',
    'logout': '<path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><path d="m16 17 5-5-5-5"/><path d="M21 12H9"/>',
    'chat': '<path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>',
    'bell': '<path d="M10.268 21a2 2 0 0 0 3.464 0"/><path d="M3.262 15.326A1 1 0 0 0 4 17h16a1 1 0 0 0 .74-1.673C19.41 13.956 18 12.499 18 8A6 6 0 0 0 6 8c0 4.499-1.411 5.956-2.738 7.326"/>',
    'search': '<circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/>',
    'sort': '<path d="m3 16 4 4 4-4"/><path d="M7 20V4"/><path d="m21 8-4-4-4 4"/><path d="M17 4v16"/>',
    'list': '<path d="M3 12h.01"/><path d="M3 18h.01"/><path d="M3 6h.01"/><path d="M8 12h13"/><path d="M8 18h13"/><path d="M8 6h13"/>',
    'image': '<rect width="18" height="18" x="3" y="3" rx="2"/><circle cx="9" cy="9" r="2"/><path d="m21 15-3.086-3.086a2 2 0 0 0-2.828 0L6 21"/>',
}

I.update({
    'back': '<path d="m12 19-7-7 7-7"/><path d="M19 12H5"/>',
    'share': '<circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><path d="m8.59 13.51 6.83 3.98"/><path d="m15.41 6.51-6.82 3.98"/>',
    'filter': '<path d="M22 3H2l8 9.46V19l4 2v-8.54z"/>',
    'money': '<rect width="20" height="12" x="2" y="6" rx="2"/><circle cx="12" cy="12" r="2"/><path d="M6 12h.01M18 12h.01"/>',
    'cal': '<rect width="18" height="18" x="3" y="4" rx="2"/><path d="M16 2v4M8 2v4M3 10h18"/>',
    'clip': '<path d="m21.44 11.05-9.19 9.19a6 6 0 0 1-8.49-8.49l8.57-8.57A4 4 0 1 1 18 8.84l-8.59 8.57a2 2 0 0 1-2.83-2.83l8.49-8.48"/>',
    'x': '<path d="M18 6 6 18M6 6l12 12"/>',
    'heart': '<path d="M19 14c1.49-1.46 3-3.21 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.76 0-3 .5-4.5 2-1.5-1.5-2.74-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4.05 3 5.5l7 7Z"/>',
    'insta': '<rect width="20" height="20" x="2" y="2" rx="5"/><circle cx="12" cy="12" r="4"/><path d="M17.5 6.5h.01"/>',
    'tiktok': '<path d="M9 12a4 4 0 1 0 4 4V3c.5 2.5 2.5 4.5 5 5"/>',
    'eye': '<path d="M2.06 12.35a1 1 0 0 1 0-.7 10.75 10.75 0 0 1 19.88 0 1 1 0 0 1 0 .7 10.75 10.75 0 0 1-19.88 0"/><circle cx="12" cy="12" r="3"/>',
    'trend': '<path d="m22 7-8.5 8.5-5-5L2 17"/><path d="M16 7h6v6"/>',
    'refresh': '<path d="M3 12a9 9 0 0 1 9-9 9.75 9.75 0 0 1 6.74 2.74L21 8"/><path d="M21 3v5h-5"/><path d="M21 12a9 9 0 0 1-9 9 9.75 9.75 0 0 1-6.74-2.74L3 16"/><path d="M8 16H3v5"/>',
    'edit': '<rect width="8" height="4" x="8" y="2" rx="1"/><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/><path d="M12 11h4M12 16h4M8 11h.01M8 16h.01"/>',
    'arrowl': '<path d="m12 19-7-7 7-7"/><path d="M19 12H5"/>',
})

def _st(ico, t, d):
    """Caixa de status do cartão (ícone roxo, título e descrição). data-st permite trocar o estado no site.js."""
    return f'<div class="la-st"><span class="la-sti">{_ic(I[ico], 19, 2.2)}</span><div><b>{t}</b><span>{d}</span></div></div>'

# Estados do cartão Verão Glow em "Campanhas" (textos do app). O site.js troca o estado pelo data-k.
ESTADOS_APP = [
    ('analise', 'clock', 'Inscrição em análise', 'Em breve você será notificada se a sua inscrição foi aprovada.', 'Inscrita em 04/11'),
    ('roteiro', 'upload', 'Envie seus roteiros', 'Envie seus roteiros para aprovação até 24/10/2026.', 'Prazo 24/10'),
    ('aguarda', 'clock', 'Aguardando aprovação dos roteiros', 'Aguarde a aprovação dos seus roteiros.', 'Prazo 24/10'),
    ('concluida', 'check', 'Campanha concluída', 'Pagamento liberado na sua carteira.', 'Concluída em 30/10'),
]

def tela_app(A):
    status = ('<svg width="18" height="12" viewBox="0 0 18 12" aria-hidden="true"><rect x="0" y="8" width="3" height="4" rx="1"/><rect x="5" y="5.5" width="3" height="6.5" rx="1"/>'
              '<rect x="10" y="3" width="3" height="9" rx="1"/><rect x="15" y="0" width="3" height="12" rx="1"/></svg>'
              '<svg width="28" height="13" viewBox="0 0 28 13" aria-hidden="true"><rect x=".5" y=".5" width="24" height="12" rx="3.8" fill="none" stroke="currentColor" opacity=".4"/>'
              '<rect x="2.5" y="2.5" width="20" height="8" rx="2.2"/><path d="M26 4.5v4c.9-.3 1.5-1.1 1.5-2s-.6-1.7-1.5-2z" opacity=".45"/></svg>')
    av = f'<img class="la-av" src="{A("assets/hero/telas/av-lume.webp")}" alt="" width="46" height="46" loading="lazy" decoding="async">'
    seg = lambda on: '<div class="la-seg">' + ''.join(f'<span class="{"on" if i == on else ""}">{t}</span>' for i, t in enumerate(('Descobrir', 'Campanhas', 'Convites'))) + '</div>'
    estados = ''.join(f'<div class="la-sk" data-k="{k}">{_st(ic, t, d)}</div>' for k, ic, t, d, _ in ESTADOS_APP)
    rodapes = ''.join(f'<span class="la-sk" data-k="{k}">{r}</span>' for k, _, _, _, r in ESTADOS_APP)
    chips = ('Minhas inscrições', 'Ativas', 'Finalizadas')
    chips_html = ''.join(f'<span data-c="{i}">{t}</span>' for i, t in enumerate(chips))
    return f'''<div class="ls ls-app" aria-hidden="true" data-ls="app"><div class="ls-in">
<div class="la-sb" data-sb><b>9:41</b><span>{status}</span></div>
<div class="la-v on" data-v="descobrir">
  <p class="la-t">Campanhas</p>{seg(0)}
  <div class="la-busca"><span class="la-in">{_ic(I['search'], 18)}Buscar campanhas</span><span class="la-fi">{_ic(I['filter'], 18)}</span></div>
  <p class="la-h2">Campanhas em destaque</p>
  <div class="la-dest" data-alvo="destaque"><div class="la-dart">{ART['lume']}</div><span class="la-pill">Beleza</span><span class="la-pill la-pr">R$ 1.800</span>
    <div class="la-dcap">{av}<div><b>Verão Glow</b><span>Rotina de verão com a linha Glow. 1 reels e 2 stories.</span></div></div></div>
  <div class="la-dest la-dest2"><div class="la-dart">{ART['run']}</div><span class="la-pill">Fitness</span><span class="la-pill la-pr">R$ 2.500</span></div>
</div>
<div class="la-v la-det" data-v="detalhe">
  <div class="la-hero">{ART['lume']}<span class="la-cb la-cb-l">{_ic(I['back'], 20)}</span><span class="la-cb la-cb-r">{_ic(I['share'], 18)}</span>
    <span class="la-pill la-pb">Beleza</span><span class="la-pill la-pr la-pb2">R$ 1.800</span></div>
  <div class="la-sheet0">
    <div class="la-marca">{av}<div><b>Casa Lume</b><span>Beleza</span></div></div>
    <p class="la-tt">Verão Glow</p><p class="la-desc">Rotina de verão com a linha Glow. 1 reels e 2 stories.</p>
    <div class="la-tiles"><div>{_ic(I['money'], 20, 1.8)}<span>Ganho</span><b>R$ 1.800</b></div><div>{_ic(I['cal'], 20, 1.8)}<span>Duração</span><b>30 dias</b></div><div>{_ic(I['upload'], 20, 1.8)}<span>Entregas</span><b>1 reels, 2 stories</b></div></div>
  </div>
  <div class="la-cta"><div><span>Ganho</span><b>R$ 1.800</b></div><span class="la-btn" data-alvo="participar"><span data-btn="0">Quero participar</span><span data-btn="1">{_ic(I['check'], 18, 2.4)}Inscrição enviada</span></span></div>
  <div class="la-dim" data-dim></div>
  <div class="la-rot" data-rot>
    <i class="la-grab"></i>
    <div class="la-rh"><b>Roteiro: Reels</b><span class="la-x">{_ic(I['x'], 18)}</span></div>
    <p class="la-rs">Vídeo vertical, até 90 segundos. Prazo 24/10.</p>
    <span class="la-rl">Roteiro</span>
    <div class="la-ta"><span class="la-ph" data-ph>Abertura, aplicação do produto e fechamento com a hashtag</span><span data-type></span><i class="la-caret" data-caret></i></div>
    <span class="la-anx">{_ic(I['clip'], 18)}Anexar arquivo</span>
    <div class="la-rb"><span>Salvar rascunho</span><span class="la-env" data-alvo="enviar">Enviar</span></div>
  </div>
</div>
<div class="la-v" data-v="campanhas">
  <p class="la-t">Campanhas</p>{seg(1)}
  <div class="la-chips">{chips_html}<i class="la-hl" data-hl><span class="la-hl-in" data-hli>{''.join(f'<span>{t}</span>' for t in chips)}</span></i></div>
  <div class="la-lista">
    <article class="la-cd" data-cdv><div class="la-h"><div class="la-th">{ART['lume']}</div><div class="la-n"><b>Verão Glow</b><span>Casa Lume</span></div><span class="la-tg">Beleza</span></div>
      <div class="la-sts" data-alvo="status">{estados}</div>
      <div class="la-f"><span class="la-fs">{rodapes}</span><b data-valor>R$ 1.800</b></div></article>
    <article class="la-cd la-cd2" data-cd2><div class="la-h"><div class="la-th">{ART['run']}</div><div class="la-n"><b>Run Club SP</b><span>Pace Running</span></div><span class="la-tg">Fitness</span></div>
      {_st('clock', 'Aguardando aprovação dos roteiros', 'Aguarde a aprovação dos seus roteiros.')}<div class="la-f"><span>Prazo 02/11</span><b>R$ 2.500</b></div></article>
  </div>
</div>
<div class="la-toast" data-toast>{_ic(I['check'], 16, 2.6)}<span data-toast-t></span></div>
<div class="la-nav" data-nav><span style="left:34px">{_ic(I['home'], 22, 1.8)}</span><span class="on">{_ic(I['mega'], 20)}Campanhas</span>
<span style="left:261px">{_ic(I['users'], 22, 1.8)}</span><span style="left:327px">{_ic(I['user'], 22, 1.8)}</span></div>
<i class="ls-tap" data-tap></i>
</div></div>'''

# ---------- MacBook: painel (1920 x 1152 px) ----------
def _cd_bo(A, art, status, criadores, av, t, desc, prog, alc, pub, pend, i, alvo=''):
    cor = {'Ativa': '#9E2CFA', 'Finalizada': '#050505', 'Rascunho': '#6B6B6B'}[status]
    cover = ART[art] if art else f'<div class="lp-vaz">{_ic(I["image"], 34, 1.6)}<span>Sem capa</span></div>'
    avh = AV_PACE if av == 'pace' else f'<img class="ls-av" src="{A("assets/hero/telas/" + av + ".webp")}" alt="" width="46" height="46" loading="lazy" decoding="async">'
    dot = '<i></i>' if pend not in ('0', '–') else ''
    return (f'<article class="lp-cd" style="--i:{i}" data-cd{f" data-alvo={alvo}" if alvo else ""}><div class="lp-cv">{cover}<span class="lp-ch">{criadores}</span><span class="lp-sp" style="background:{cor}">{status}</span></div>'
            f'<div class="lp-bb"><div class="lp-bh">{avh}<div><b>{t}</b><span>{desc}</span></div></div>'
            f'<div class="lp-pg"><span>Progresso de publicação</span><b data-pct="{prog}">{prog}%</b></div><div class="lp-bar"><i style="width:{prog}%" data-bar></i></div>'
            f'<div class="lp-ks"><div><span>Alcance</span><b>{alc}</b></div><div><span>Publicados</span><b>{pub}</b></div><div><span>Pendentes</span><b>{dot}{pend}</b></div></div></div></article>')

# creators de exemplo (os mesmos nomes fictícios do app)
CRIADORES = [
    ('Marina Duarte', 'MD', '#F3D9FF', '#7A1FC2', 3, ['Beleza', 'Lifestyle'], [('insta', 'Instagram', '@marinaduarte', '28,7 mil', '4,1% eng.'), ('tiktok', 'TikTok', '@marinaduarte', '12,4 mil', '6,8% eng.')]),
    ('Beatriz Nunes', 'BN', '#FFE3D6', '#B4461C', 2, ['Moda & Beleza', 'UGC'], [('insta', 'Instagram', '@beatriznunes', '16,6 mil', '3,2% eng.')]),
    ('Caio Ferraz', 'CF', '#DDF3E4', '#1F7A44', 1, ['Fitness & Saúde'], [('insta', 'Instagram', '@caioferraz', '10,8 mil', '5,0% eng.')]),
    ('Larissa Prado', 'LP', '#DCEBFF', '#1F57B4', 2, ['Casa & Decoração', '+2'], [('tiktok', 'TikTok', '@larissaprado', '43,4 mil', '7,9% eng.'), ('insta', 'Instagram', '@larissaprado', '21,3 mil', '2,7% eng.')]),
]

def _criador(c, i):
    nome, ini, bg, fg, redes, tags, rs = c
    tg = ''.join(f'<span>{t}</span>' for t in tags)
    rows = ''.join(f'<div class="lp-rede">{_ic(I[ic], 18, 1.8)}<div><b>{n}</b><span>{h}</span></div><div class="lp-rn"><b>{s}</b><span>{e}</span></div></div>' for ic, n, h, s, e in rs)
    return (f'<article class="lp-cr"><div class="lp-crh"><span class="lp-cav" style="background:{bg};color:{fg}">{ini}</span><div><b>{nome}</b><span>{redes} {"rede social" if redes == 1 else "redes sociais"}</span></div></div>'
            f'<div class="lp-tags">{tg}</div><div class="lp-redes">{rows}</div>'
            f'<div class="lp-crb"><span class="lp-vp">Ver perfil</span><span class="lp-conv" data-conv="{i}" data-alvo="conv{i}"><span data-btn="0">Convidar</span><span data-btn="1">{_ic(I["check"], 16, 2.6)}Convidado</span></span>'
            f'<span class="lp-fav">{_ic(I["heart"], 18, 1.8)}</span></div></article>')

ETAPAS = [('Seleção', '', '12 pessoas'), ('Roteiros', '', '12 de 12'), ('Conteúdos', 'até 27/11', '9 de 12'), ('Publicação', '01/12', '6 de 12'), ('Pagamento', 'após publicar', '0 de 12')]

def tela_painel(A, logo_branco):
    cards = (_cd_bo(A, 'lume', 'Ativa', '12 criadores', 'av-lume', 'Verão Glow', 'Rotina de skincare de verão com a linha Glow', 68, '1,2 mi', '17', '8', 0, 'card')
             + _cd_bo(A, 'run', 'Ativa', '8 criadores', 'pace', 'Run Club SP', 'Treinos de corrida com a comunidade de São Paulo', 35, '640 mil', '6', '11', 1)
             + _cd_bo(A, 'aurora', 'Ativa', '5 criadores', 'av-aurora', 'Casa Aurora', 'Decoração de mesa para receber em casa', 20, '210 mil', '2', '8', 2)
             + _cd_bo(A, 'brisa', 'Finalizada', '10 criadores', 'av-brisa', 'Brisa de Verão', 'Drinks sem álcool para os dias quentes', 100, '2,3 mi', '24', '0', 3)
             + _cd_bo(A, '', 'Rascunho', '0 criadores', 'av-lume', 'Pele de Seda', 'Lançamento do novo hidratante corporal', 0, '–', '0', '–', 4))
    nav = lambda ico, txt, k, badge='': (f'<span class="lp-a{" on" if k == "campanhas" else ""}" data-nav-k="{k}" data-alvo="nav-{k}">{_ic(I[ico], 20, 1.8)}<span>{txt}</span>'
                                          + (f'<em>{badge}</em>' if badge else '') + '</span>')
    tabs = ''.join(f'<span class="{"on" if on else ""}">{t}<em>{n}</em></span>' for t, n, on in
                   [('Todas', '5', True), ('Ativas', '3', False), ('Rascunhos', '1', False), ('Finalizadas', '1', False)])
    etapas = ''.join(f'<div class="lp-et" data-et="{i}"><span class="lp-etn"><i>{i + 1}</i>{_ic(I["check"], 14, 3)}</span><b>{t}</b><span class="lp-ets">{s}</span><span class="lp-etv">{v}</span></div>'
                     for i, (t, s, v) in enumerate(ETAPAS))
    kpis = [('users', 'Criadores na campanha', 12, '', 0), ('image', 'Conteúdos no ar', 17, ' de 24', 0), ('eye', 'Alcance total', 1.2, ' mi', 1), ('trend', 'Engajamento', 5.4, '%', 1)]
    kp = ''.join(f'<div class="lp-kp">{_ic(I[ic], 20, 1.8)}<div><span>{t}</span><b data-n="{n}" data-suf="{suf}" data-dec="{dec}">{f"{n:.{dec}f}".replace(".", ",")}{suf}</b></div></div>'
                 for ic, t, n, suf, dec in kpis)
    filtros = ''.join(f'<span class="{"on" if i == 0 else ""}">{t}</span>' for i, t in enumerate(('Todos', 'Beleza', 'Moda', 'Fitness', 'Casa & Decoração', 'UGC')))
    return f'''<div class="ls ls-plat" aria-hidden="true" data-ls="plat"><div class="ls-in">
<div class="lp-sd"><img class="lp-lg" src="{logo_branco}" alt="" width="64" height="36">
  <div class="lp-ws"><img src="{A('assets/hero/telas/vnh.webp')}" alt="" width="36" height="36" loading="lazy" decoding="async"><div><b>Você no Hype</b><span>Membro</span></div>{_ic(I['chev'], 16)}</div>
  <div class="lp-lb">WORKSPACE</div>{nav('grid', 'Início', 'inicio')}<hr>
  <div class="lp-lb">GESTÃO DE CAMPANHAS</div>{nav('mega', 'Campanhas', 'campanhas', '3')}{nav('users', 'Criadores', 'criadores')}{nav('video', 'Lives', 'lives')}<hr>
  <div class="lp-lb">FINANCEIRO</div>{nav('wallet', 'Financeiro', 'financeiro')}
  <div class="lp-me"><span class="lp-ini">AR</span><div><b>Ana Ribeiro</b><span>Membro</span></div>{_ic(I['logout'], 19, 1.8)}</div>
</div>
<div class="lp-tp"><span>{_ic(I['chat'], 19, 1.8)}</span><span>{_ic(I['bell'], 19, 1.8)}</span></div>
<div class="lp-v on" data-v="campanhas"><div class="lp-mn"><p class="lp-t">Campanhas</p><p class="lp-sub">Crie, acompanhe e aprove tudo em um só lugar.</p>
  <div class="lp-fl"><div class="lp-tb">{tabs}</div><div class="lp-bs">{_ic(I['search'], 18)}Pesquisar</div>
    <div class="lp-so">{_ic(I['sort'], 17)}Mais recentes</div><div class="lp-vw"><span class="on">{_ic(I['grid'], 17)}</span><span>{_ic(I['list'], 17)}</span></div></div>
  <div class="lp-gr">{cards}</div>
</div></div>
<div class="lp-v" data-v="campanha"><div class="lp-mn">
  <span class="lp-voltar">{_ic(I['arrowl'], 17)}Campanhas</span>
  <div class="lp-cab"><div class="lp-cabart">{ART['lume']}</div>
    <div class="lp-cabtx"><div class="lp-meta"><span class="lp-pub">Publicado</span><b>12</b> criadores<i class="lp-mbar"><i data-mbar></i></i><b data-mpct>68%</b> concluído</div>
      <p class="lp-ct">Verão Glow</p><p class="lp-cd2">Campanha de verão da Casa Lume com creators de beleza e lifestyle: a rotina da manhã com a linha Glow, em 1 reels e 2 stories.</p></div>
    <div class="lp-cabb"><span class="lp-bk">{_ic(I['refresh'], 17)}Verificar publicações</span><span class="lp-bg">{_ic(I['edit'], 17)}Editar</span><span class="lp-lk">{_ic(I['eye'], 17)}Ver convite</span><span class="lp-lk">{_ic(I['share'], 16)}Compartilhar</span></div>
    <div class="lp-abas"><span class="on">Visão geral</span><span>Gerenciamento<em>8</em></span><span>Gestão</span></div></div>
  <div class="lp-prog"><div class="lp-pgl"><span>Progresso geral</span><div><b data-geral>68%</b><span>campanha em andamento</span></div></div><div class="lp-ets-w">{etapas}</div>
    <div class="lp-kps">{kp}</div></div>
  <div class="lp-acao"><p>Precisa da sua ação</p><span>8 itens aguardando</span><div class="lp-ac"><span class="lp-aci">{_ic(I['image'], 18)}</span><b data-acao>8</b><span>Conteúdos para aprovar</span><span class="lp-acb">Revisar {_ic(I['chev'], 14, 2.4)}</span></div></div>
</div></div>
<div class="lp-v" data-v="criadores"><div class="lp-mn">
  <p class="lp-t">Criadores</p><p class="lp-sub">Encontre creators para as suas campanhas.</p>
  <div class="lp-fl"><div class="lp-bs lp-bs2">{_ic(I['search'], 18)}Buscar por nome ou @</div><div class="lp-filt">{filtros}</div></div>
  <div class="lp-crg">{''.join(_criador(c, i) for i, c in enumerate(CRIADORES))}</div>
</div></div>
<div class="lp-toast" data-toast>{_ic(I['check'], 18, 2.6)}<span data-toast-t></span></div>
<i class="ls-cur" data-cur><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 3l14 7-6 2-3 6z" fill="#050505" stroke="#fff" stroke-width="1.6" stroke-linejoin="round"/></svg></i>
</div></div>'''
