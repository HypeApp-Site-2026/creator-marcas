# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, '/home/claude/seo')
from data import *

# ---- Lançamento enxuto (26/10/2026): só URLs essenciais; o resto entra conforme a necessidade ----
LAUNCH = ["/", "/criadores/", "/marcas/", "/baixar/", "/perguntas-frequentes/",
          "/sobre/", "/contato/", "/suporte/", "/privacidade/", "/termos/", "/cookies/", "/exclusao-de-conta/"]
FUNCIONAL = ["/contato/marcas/", "/contato/enviado/",
             "/suporte/enviado/", "/entrar/", "/app"]
WHY = {
 "/": "Porta de entrada e escolha de público.",
 "/criadores/": "Conversão de creators. CTA principal: Baixar o app (ordem de 26/10).",
 "/marcas/": "Conversão de marcas, empresas e agências. CTA principal: formulário de interesse do comercial em /contato/marcas/. Tem a seção #agencias.",
 "/baixar/": "Caminho principal de creators: lojas e QR code. Inclui a seção \"Já tem conta?\".",
 "/perguntas-frequentes/": "Responde às dúvidas principais enquanto a central de ajuda não existe. Item \"Ajuda\" do menu aponta para cá.",
 "/sobre/": "Quem opera o produto e canais oficiais; base do Organization e do llms.txt.",
 "/contato/": "Triagem para comercial, parcerias e privacidade.",
 "/suporte/": "Atendimento a quem já usa o app.",
 "/privacidade/": "Obrigatória: o site coleta dados nos formulários. Inclui o encarregado e o canal de direitos.",
 "/termos/": "Obrigatória para cadastro e uso.",
 "/cookies/": "Obrigatória se o site usar cookies opcionais.",
 "/exclusao-de-conta/": "Exigida pelo Google Play: link público para pedir a exclusão da conta.",
}
for r in R:
    if r["url"] in LAUNCH:
        r["xml"] = "Sim"
        r["prio"] = "Lançamento"
        r["obs"] = (WHY[r["url"]] + (" " + r["obs"] if r["obs"] else "")).strip()
        if r["pub"] not in ("Sim",):
            r["pub"] = r["pub"] if r["pub"].startswith("Sim") else "Sim"
    elif r["url"] in FUNCIONAL:
        r["xml"] = "Não"
        r["prio"] = "Lançamento"
        r["pub"] = "Sim (página de apoio, fora do sitemap)"
    else:
        if r["xml"] == "Sim":
            r["xml"] = "Depois"
        r["pub"] = "Depois, conforme a necessidade"
        r["prio"] = "Próximas"
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.formatting.rule import FormulaRule
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.utils import get_column_letter
from xml.sax.saxutils import escape

import os
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out')
import os; os.makedirs(OUT, exist_ok=True)

F = 'Arial'
HEAD_FILL = PatternFill('solid', fgColor='050505')
HEAD_FONT = Font(name=F, bold=True, color='FFFFFF', size=10)
BODY = Font(name=F, size=10)
BOLD = Font(name=F, size=10, bold=True)
INPUT_FILL = PatternFill('solid', fgColor='FFF4C2')
WARN_FILL = PatternFill('solid', fgColor='F8D7DA')
SIM_FILL = PatternFill('solid', fgColor='EBDDFE')
thin = Side(style='thin', color='E0E0E0')
BORDER = Border(bottom=thin)
WRAP = Alignment(wrap_text=True, vertical='top')

wb = Workbook()

# ---------------- Regras (primeira, por causa da referência do domínio) ----------------
rg = wb.active
rg.title = 'Regras'
rg['A1'] = 'Regras de metadados do site HypeApp'; rg['A1'].font = Font(name=F, size=14, bold=True)
rg['A2'] = 'Domínio base'; rg['A2'].font = BOLD
rg['B2'] = BASE; rg['B2'].font = Font(name=F, size=10, color='0000FF'); rg['B2'].fill = INPUT_FILL
rg['C2'] = 'Usado nas fórmulas de canonical da aba Matriz.'; rg['C2'].font = BODY
hdr = ['Item', 'Padrão', 'Como aplicar']
for j, h in enumerate(hdr, 1):
    c = rg.cell(row=4, column=j, value=h); c.font = HEAD_FONT; c.fill = HEAD_FILL
for i, (a, b, c3) in enumerate(RULES, 5):
    for j, v in enumerate((a, b, c3), 1):
        c = rg.cell(row=i, column=j, value=v); c.font = BOLD if j == 1 else BODY; c.alignment = WRAP; c.border = BORDER
r0 = 5 + len(RULES) + 1
rg.cell(row=r0, column=1, value='Organization em JSON-LD (Início e Sobre)').font = BOLD
c = rg.cell(row=r0 + 1, column=1, value=ORG_JSONLD); c.font = Font(name='Courier New', size=9); c.alignment = WRAP
rg.merge_cells(start_row=r0 + 1, start_column=1, end_row=r0 + 1, end_column=3)
rg.row_dimensions[r0 + 1].height = 290
rg.cell(row=r0 + 2, column=1, value='Campos entre colchetes ficam para preencher com dados oficiais.').font = Font(name=F, size=9, italic=True)
for col, w in zip('ABC', (24, 46, 90)):
    rg.column_dimensions[col].width = w

# ---------------- Matriz ----------------
ws = wb.create_sheet('Matriz', 0)
cols = [
 ('URL', 34), ('Página', 26), ('Público', 10), ('Seção', 18), ('Prioridade', 9), ('Condição', 9),
 ('Publica no lançamento', 22), ('Meta robots', 16), ('No sitemap.xml', 12), ('Canonical', 44),
 ('Title', 46), ('Caracteres (title)', 10), ('Meta description', 60), ('Caracteres (descr.)', 10),
 ('H1', 36), ('Pergunta principal (AEO)', 32), ('Imagem social', 20), ('Dados estruturados', 22),
 ('Status', 12), ('Responsável', 16), ('Observações', 46)]
for j, (h, w) in enumerate(cols, 1):
    c = ws.cell(row=1, column=j, value=h); c.font = HEAD_FONT; c.fill = HEAD_FILL; c.alignment = Alignment(wrap_text=True, vertical='center')
    ws.column_dimensions[get_column_letter(j)].width = w
ws.row_dimensions[1].height = 32

for i, r in enumerate(R, 2):
    canon = f'=Regras!$B$2&A{i}'
    if r['url'] == '/app':
        canon = 'Não se aplica'
    elif '?q=' in r['url']:
        canon = 'Nenhuma'
    vals = [r['url'], r['pagina'], r['publico'], r['secao'], r['prio'], r['cond'] or '—', r['pub'], r['robots'],
            r['xml'], canon, r['title'], f'=LEN(K{i})', r['desc'], f'=LEN(M{i})', r['h1'], r['pergunta'] or '—',
            r['img'], r['schema'], 'Em revisão', None, r['obs']]
    for j, v in enumerate(vals, 1):
        c = ws.cell(row=i, column=j, value=v)
        c.font = BODY; c.alignment = WRAP; c.border = BORDER
    ws.cell(row=i, column=1).font = Font(name='Courier New', size=9)
    ws.cell(row=i, column=10).font = Font(name='Courier New', size=9)
    for j in (11, 13, 15, 16, 19, 20):  # campos editáveis
        ws.cell(row=i, column=j).fill = INPUT_FILL
    if r['xml'] == 'Sim':
        ws.cell(row=i, column=9).fill = SIM_FILL
        ws.cell(row=i, column=9).font = BOLD

last = len(R) + 1
ws.freeze_panes = 'C2'
ws.auto_filter.ref = f'A1:{get_column_letter(len(cols))}{last}'
dv = DataValidation(type='list', formula1='"A escrever,Em revisão,Aprovado"', allow_blank=True)
ws.add_data_validation(dv); dv.add(f'S2:S{last}')
dv2 = DataValidation(type='list', formula1='"Sim,Depois,Não"', allow_blank=False)
ws.add_data_validation(dv2); dv2.add(f'I2:I{last}')
ws.conditional_formatting.add(f'L2:L{last}', FormulaRule(formula=[f'L2>60'], fill=WARN_FILL))
ws.conditional_formatting.add(f'N2:N{last}', FormulaRule(formula=[f'N2>155'], fill=WARN_FILL))

# ---------------- Modelos de rota ----------------
mt = wb.create_sheet('Modelos de rota', 1)
mh = [('Rota', 36), ('Tipo', 22), ('Padrão do title', 40), ('Padrão da descrição', 46), ('Meta robots', 16),
      ('No sitemap.xml', 22), ('Canonical', 22), ('Dados estruturados', 22), ('Imagem social', 30), ('Observações', 50)]
for j, (h, w) in enumerate(mh, 1):
    c = mt.cell(row=1, column=j, value=h); c.font = HEAD_FONT; c.fill = HEAD_FILL; c.alignment = WRAP
    mt.column_dimensions[get_column_letter(j)].width = w
for i, t in enumerate(TEMPLATES, 2):
    for j, v in enumerate(t, 1):
        c = mt.cell(row=i, column=j, value=v); c.font = BODY; c.alignment = WRAP; c.border = BORDER
    mt.cell(row=i, column=1).font = Font(name='Courier New', size=9)
mt.freeze_panes = 'B2'

# ---------------- Legenda ----------------
lg = wb.create_sheet('Legenda', 0)
lg['A1'] = 'Matriz de metadados · site HypeApp'; lg['A1'].font = Font(name=F, size=16, bold=True)
lg['A2'] = 'Versão 1 · 26 de outubro de 2026 · domínio https://www.hypeapp.com.br'; lg['A2'].font = BODY
lg['A4'] = 'Resumo'; lg['A4'].font = Font(name=F, size=12, bold=True)
summary = [
 ('Páginas e rotas na matriz', '=COUNTA(Matriz!A2:A%d)' % last),
 ('No sitemap.xml do lançamento', '=COUNTIF(Matriz!I2:I%d,"Sim")' % last),
 ('Próximas (entram quando forem publicadas)', '=COUNTIF(Matriz!I2:I%d,"Depois")' % last),
 ('Páginas de apoio no ar, fora do sitemap', '=COUNTIFS(Matriz!E2:E%d,"Lançamento",Matriz!I2:I%d,"Não")' % (last,last)),
 ('Com noindex', '=COUNTIF(Matriz!H2:H%d,"noindex, follow")' % last),
 ('Titles acima de 60 caracteres', '=COUNTIF(Matriz!L2:L%d,">60")' % last),
 ('Descrições acima de 155 caracteres', '=COUNTIF(Matriz!N2:N%d,">155")' % last),
 ('Aprovadas', '=COUNTIF(Matriz!S2:S%d,"Aprovado")' % last),
]
for i, (a, f) in enumerate(summary, 5):
    lg.cell(row=i, column=1, value=a).font = BODY
    c = lg.cell(row=i, column=2, value=f); c.font = BOLD
row = 5 + len(summary) + 1
lg.cell(row=row, column=1, value='Como usar').font = Font(name=F, size=12, bold=True)
howto = [
 ('Células em amarelo', 'Campos para revisar e editar: Title, Meta description, H1, Pergunta principal, Status e Responsável.'),
 ('Caracteres', 'Calculados por fórmula. Ficam em vermelho acima de 60 (title) ou 155 (descrição).'),
 ('No sitemap.xml', 'Sim = entra no arquivo do lançamento (destacado em roxo). Depois = entra quando a página for publicada. Não = fica fora.'),
 ('Condição G', 'Página depende de validação de produto, operação ou jurídico antes de ir ao ar.'),
 ('Prioridade', 'Lançamento = no ar no primeiro dia (13 no sitemap + 7 de apoio). Próximas = entram conforme a necessidade; para incluir uma, mude "No sitemap.xml" para Sim e gere o sitemap.xml e o llms.txt de novo.'),
 ('Canonical', 'Fórmula que junta o domínio da aba Regras com a URL. Trocar o domínio lá atualiza todas.'),
 ('Status', 'Escolha na lista: A escrever, Em revisão ou Aprovado. Tudo começa em Em revisão.'),
 ('Placeholders', 'Textos entre colchetes, como [CNPJ], esperam dados oficiais.'),
 ('Modelos de rota', 'Padrões para páginas geradas em série (artigos, notas de versão, perfis, convites).'),
 ('Exemplo de linha pronta', 'Veja a linha do Início (primeira da Matriz): title, descrição, H1, pergunta, imagem e dados estruturados preenchidos.'),
]
for i, (a, b) in enumerate(howto, row + 1):
    lg.cell(row=i, column=1, value=a).font = BOLD
    c = lg.cell(row=i, column=2, value=b); c.font = BODY; c.alignment = WRAP
lg['A' + str(row + 1)].fill = INPUT_FILL
lg.column_dimensions['A'].width = 42
lg.column_dimensions['B'].width = 100

wb.move_sheet('Regras', offset=0)
order = ['Legenda', 'Matriz', 'Modelos de rota', 'Regras']
wb._sheets = [wb[n] for n in order]
wb.active = 1
wb.save(f'{OUT}/HypeApp_Matriz_de_Metadados.xlsx')

# ---------------- sitemap.xml ----------------
launch = [r for r in R if r['xml'] == 'Sim']
lines = ['<?xml version="1.0" encoding="UTF-8"?>',
         '<!-- sitemap.xml do lançamento · www.hypeapp.com.br · gerado em 26/10/2026 a partir da matriz de metadados.',
         '     Só URLs canônicas, publicadas e com resposta 200. O CMS deve acrescentar <lastmod> quando o conteúdo mudar de verdade.',
         '     Lançamento enxuto: só URLs essenciais. As demais entram conforme a necessidade, sempre a partir da matriz.',
         '     Páginas marcadas "Depois" na matriz entram aqui quando forem publicadas. -->',
         '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
sec = None
for r in launch:
    if r['secao'] != sec:
        sec = r['secao']; lines.append(f'  <!-- {sec} -->')
    lines.append(f'  <url><loc>{escape(BASE + r["url"])}</loc></url>')
lines.append('</urlset>')
open(f'{OUT}/sitemap.xml', 'w', encoding='utf-8').write('\n'.join(lines) + '\n')

# ---------------- robots.txt ----------------
robots = f"""# robots.txt · {BASE}
# Versão 1 · 26/10/2026
#
# Regra do site: nada é bloqueado em produção.
# Páginas de formulário, confirmação e busca usam a meta tag noindex
# e precisam continuar liberadas para que os buscadores leiam essa tag.
# Prévia e homologação ficam em outros endereços, com login e robots.txt próprio.

User-agent: *
Allow: /

# Buscadores e assistentes de IA (busca e respostas) estão liberados pela regra acima,
# entre eles Googlebot, Bingbot, OAI-SearchBot, ChatGPT-User, Claude-SearchBot,
# Claude-User e PerplexityBot.
#
# Treinamento de modelos: também liberado pela regra acima.
# Para não permitir treinamento, retire o "#" das linhas abaixo.
# Isso não afeta a presença nas buscas e respostas de IA.
#
# User-agent: GPTBot
# Disallow: /
#
# User-agent: ClaudeBot
# Disallow: /
#
# User-agent: Google-Extended
# Disallow: /
#
# User-agent: CCBot
# Disallow: /

Sitemap: {BASE}/sitemap.xml
"""
open(f'{OUT}/robots.txt', 'w', encoding='utf-8').write(robots)

staging = """# robots.txt · ambientes de prévia e homologação do site HypeApp
# Use este arquivo SOMENTE fora de produção. Estes ambientes também precisam de login.
User-agent: *
Disallow: /
"""
open(f'{OUT}/robots-homologacao.txt', 'w', encoding='utf-8').write(staging)

# ---------------- llms.txt ----------------
def L(path):
    r = next(x for x in R if x['url'] == path)
    assert r['xml'] == 'Sim', path
    return f"{BASE}{path}"
llms = f"""# HypeApp

> O HypeApp é a plataforma da Você no Hype que conecta creators e marcas em campanhas de marketing de influência, do convite ao pagamento. Creators usam o app no iPhone; marcas e agências usam o painel na web.

Informações oficiais:

- Nome do produto: HypeApp.
- Desenvolvido e operado por: Você no Hype Marketing e Entretenimento LTDA.
- A Você no Hype é agência parceira do TikTok Shop (TikTok Shop Partner).
- Site oficial: {BASE}/
- App para iPhone: https://apps.apple.com/br/app/hype-app-influenciadores/id6778357608
- Instagram: https://www.instagram.com/hypeappbrasil/
- YouTube: https://www.youtube.com/@hypeappbrasil
- LinkedIn: https://www.linkedin.com/company/hypeappbrasil/
- Para marcas e agências, os valores são sob consulta com o comercial.
- Creators baixam o app e criam a conta por ele. Ter conta não garante participação em campanhas.
- Cada campanha tem critérios próprios; a seleção é feita pela marca (ou pela Você no Hype, quando a marca contrata a gestão da campanha à parte).

## Sobre o HypeApp

- [Início]({L('/')}): o que é o HypeApp e para quem é.
- [Sobre]({L('/sobre/')}): quem opera o produto, relação com a Você no Hype e canais oficiais.
- [Perguntas frequentes]({L('/perguntas-frequentes/')}): respostas curtas sobre cadastro, campanhas, pagamentos, valores para marcas e segurança.

## Para creators

- [Para criadores]({L('/criadores/')}): como criadores e influenciadores participam de campanhas com marcas pelo app.
- [Baixar o app]({L('/baixar/')}): link oficial da App Store e orientação para quem já tem conta.

## Para marcas e agências

- [Para marcas e agências]({L('/marcas/')}): como marcas, empresas e agências encontram creators e acompanham campanhas no painel; formas de trabalhar self-service e gerenciada.
- [Contato]({L('/contato/')}): formulário de interesse para marcas e agências, parcerias e privacidade.

## Ajuda e confiança

- [Suporte]({L('/suporte/')}): como abrir um chamado.
- [Política de privacidade]({L('/privacidade/')}): tratamento de dados, encarregado e direitos dos titulares.
- [Termos de uso]({L('/termos/')})
- [Exclusão de conta]({L('/exclusao-de-conta/')}): como excluir a conta do app.
"""
open(f'{OUT}/llms.txt', 'w', encoding='utf-8').write(llms)
print('ok', len(launch), 'urls no sitemap')
