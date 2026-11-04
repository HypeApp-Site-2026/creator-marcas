"""Celular da Carteira em HTML (04/11), a partir do mockup enviado (hypeapp-carteira.html).
Anima o que existe no app hoje (telas G2 e G4): Visão geral, Histórico e Solicitar saque.
Valores sempre ocultos (bolinhas). A animação roda em site.js ([data-cw]); sem JS ou com
movimento reduzido, fica parada na Visão geral."""

ICO_HOME = '<path d="m2.5 10 9.5-8 9.5 8M4.5 8.7V22h5.2v-8h4.6v8h5.2V8.7"/>'
ICO_CAMP = '<path d="M9 10 24 4v20L9 18H6a4 4 0 0 1 0-8h3Zm0 0v8m1 1 2 6H8l-2-7m18-7h1a3 3 0 0 1 0 6h-1"/>'
ICO_COM = '<path d="M2 25v-3c0-5 16-5 16 0v3H2Zm18-14c5-1 5-9 0-9m1 15c5 0 5 5 5 8h-4"/><ellipse cx="10" cy="7" rx="4" ry="5"/>'
ICO_PERF = '<ellipse cx="12" cy="6.5" rx="4.5" ry="5"/><path d="M2.7 22v-2c0-9 18.6-9 18.6 0v2H2.7Z"/>'
DOWN = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 3v17m-6-6 6 6 6-6"/></svg>'
UP = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 21V4m-6 6 6-6 6 6"/></svg>'


def dots(n=5):
    return '<span class="cw-dots" aria-hidden="true">' + '<i></i>' * n + '</span>'


def linha(ico, pill, cls=''):
    return (f'<div class="cw-row {cls}"><span class="cw-disc">{ico}</span>'
            f'<span class="cw-sk"><i></i><i></i></span><span class="cw-pill">{pill}</span></div>')


def carteira_viva():
    resumo = ''.join(f'<div class="cw-card"><span>{t}</span>{dots()}</div>'
                     for t in ('Em campanha', 'A liberar', 'Total sacado', 'Total ganho'))
    hist = (linha(UP, 'Em processamento', 'cw-novo') + linha(DOWN, 'A liberar') + linha(DOWN, 'Disponível')
            + linha(UP, 'Saque via PIX') + linha(DOWN, 'Disponível'))
    nav = ''.join(f'<span class="cw-ni{" on" if k == 3 else ""}"><svg viewBox="0 0 {vb} {vb}" aria-hidden="true">{p}</svg></span>'
                  for k, (p, vb) in enumerate([(ICO_HOME, 24), (ICO_CAMP, 28), (ICO_COM, 28), (ICO_PERF, 24)]))
    return f'''<div class="cw" data-cw role="img" aria-label="Celular com a Carteira do HypeApp: visão geral com valores ocultos, histórico e a tela Solicitar saque">
  <div class="cw-art" aria-hidden="true">
    <div class="cw-shadow"></div>
    <div class="cw-phone">
      <span class="cw-btn cw-b1"></span><span class="cw-btn cw-b2"></span><span class="cw-btn cw-b3"></span>
      <div class="cw-screen">
        <div class="cw-status"><span>9:41</span><span class="cw-si"><span class="cw-sig"><i></i><i></i><i></i><i></i></span><span class="cw-bat"></span></span></div>
        <div class="cw-island"></div>
        <div class="cw-content">
          <b class="cw-title">Carteira</b>
          <div class="cw-tabs"><span class="cw-tab on" data-cw-t="geral">Visão geral</span><span class="cw-tab" data-cw-t="hist">Histórico</span><i class="cw-hl"></i></div>
          <div class="cw-v on" data-cw-v="geral">
            <div class="cw-bal"><span>Saldo disponível</span>{dots()}</div>
            <div class="cw-sum">{resumo}</div>
            <b class="cw-h2">Valores a liberar</b>
            <div class="cw-row cw-up"><span class="cw-disc">{DOWN}</span><span class="cw-sk"><i></i><i></i></span><span class="cw-pill">A liberar</span></div>
            <span class="cw-saque" data-cw-a="saque">Solicitar saque</span>
          </div>
          <div class="cw-v" data-cw-v="hist"><b class="cw-h2 cw-h2t">Movimentações</b>{hist}</div>
        </div>
        <div class="cw-nav">{nav}</div>
        <div class="cw-dim"></div>
        <div class="cw-sheet">
          <i class="cw-grab"></i>
          <div class="cw-sh"><b>Solicitar saque</b><span class="cw-x">×</span></div>
          <div class="cw-sbal"><span>Saldo disponível para saque</span>{dots()}</div>
          <span class="cw-lbl">Valor</span>
          <div class="cw-in cw-valor"><span class="cw-ph">R$ 0,00</span>{dots(6)}</div>
          <div class="cw-pcts"><span>25%</span><span>50%</span><span data-cw-a="tudo">Tudo</span></div>
          <span class="cw-lbl">Chave PIX</span>
          <div class="cw-in cw-pix"><span class="cw-ph">CPF, Telefone, E-mail ou Chave aleatória</span><span class="cw-sk1"><i></i></span></div>
          <div class="cw-imp"><b>Importante</b>Apenas o saldo disponível pode ser sacado. O saldo "A liberar" fica disponível 30 dias após o encerramento da campanha. Prazo de processamento: até 2 horas úteis. Valor mínimo para saque: R$ 1,00.</div>
          <div class="cw-acts"><span class="cw-cancel">Cancelar</span><span class="cw-conf" data-cw-a="conf">Confirmar saque</span></div>
        </div>
        <i class="cw-tap" data-cw-tap></i>
      </div>
    </div>
  </div>
</div>'''
