// Envia por e-mail o relatório semanal do HypeApp (resumo, indicadores principais, alertas e ações).
// Roda no GitHub Actions (workflow "Relatório semanal (e-mail)"), disparado pelo agente de análise depois de publicar o relatório.
// O conteúdo chega em RELATORIO_JSON (o mesmo objeto da semana gravado na página do relatório).
// Destinatários fixos na variável RELATORIO_EMAILS (separados por vírgula): o pedido do agente não escolhe destinatário.
// SMTP: segredos SMTP_USER e SMTP_PASS (os mesmos do Vercel), servidor smtp.purelymail.com:465.

import { createRequire } from 'node:module';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const require = createRequire(import.meta.url);
const aqui = path.dirname(fileURLToPath(import.meta.url));
const modulo = [path.join(aqui, '..', 'api', '_email.js'), path.join(aqui, '..', 'vercel', 'api', '_email.js')].find((p) => fs.existsSync(p));
const { smtp, enc, emailValido, C } = require(modulo);

const LINK = process.env.RELATORIO_URL || 'https://claude.ai/artifact/WiFZnPxjsxYKdAh1Qi3dsN';
const esc = (s) => String(s == null ? '' : s).replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
const dataBR = (iso) => (iso ? iso.slice(8, 10) + '/' + iso.slice(5, 7) : '');
const num = (v, tipo) => {
  if (v == null || v === '') return null;
  if (tipo === 'pct') return (v * 100).toLocaleString('pt-BR', { maximumFractionDigits: 1 }) + '%';
  if (tipo === 'dec') return Number(v).toLocaleString('pt-BR', { maximumFractionDigits: 1 });
  return Number(v).toLocaleString('pt-BR');
};
const variacao = (v, base, menorMelhor) => {
  if (v == null || base == null || base === 0) return { txt: 'sem comparação', cor: C.cinza };
  const d = (v - base) / base, bom = menorMelhor ? d < 0 : d > 0;
  return { txt: `${d > 0 ? '+' : ''}${Math.round(d * 100)}% vs. semana anterior`, cor: Math.abs(d) < 0.005 ? C.cinza : bom ? '#1F7A4D' : '#B42318' };
};

function monta(r) {
  const semana = `${dataBR(r.semana.inicio)} a ${dataBR(r.semana.fim)}`;
  const principais = (r.indicadores || []).filter((k) => k.principal);
  const outros = (r.indicadores || []).filter((k) => !k.principal && k.valor != null);
  const kpi = (k) => {
    const v = num(k.valor, k.tipo), d = variacao(k.valor, k.anterior, k.menor_melhor);
    return `<td width="50%" style="padding:6px;vertical-align:top"><div style="border:1px solid #E3DEEA;border-radius:14px;padding:14px">
      <div style="font-size:12px;font-weight:700;color:${C.cinza}">${esc(k.nome)}</div>
      <div style="font-size:${v == null ? '15px;font-weight:700' : '26px;font-weight:800'};color:${v == null ? '#A15C00' : C.preto};margin:4px 0">${esc(v == null ? (k.pendente || 'preencher') : v)}</div>
      ${v == null ? '' : `<div style="font-size:12px;font-weight:700;color:${d.cor}">${esc(d.txt)}</div>`}</div></td>`;
  };
  const linhasKpi = [];
  for (let i = 0; i < principais.length; i += 2) linhasKpi.push(`<tr>${kpi(principais[i])}${principais[i + 1] ? kpi(principais[i + 1]) : '<td width="50%"></td>'}</tr>`);
  const lista = (itens, f) => (itens && itens.length ? `<ul style="margin:0 0 18px;padding-left:20px">${itens.map((x) => `<li style="margin:0 0 8px">${f(x)}</li>`).join('')}</ul>` : '');
  const h2 = (t) => `<h2 style="margin:22px 0 10px;font-size:17px;color:${C.preto}">${esc(t)}</h2>`;
  const html = `<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="color-scheme" content="light"><title>Relatório semanal HypeApp</title></head>
<body style="margin:0;padding:0;background:#ffffff;font-family:Inter,Helvetica,Arial,sans-serif;color:${C.preto}">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0"><tr><td align="center" style="padding:16px 12px">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="max-width:640px">
  <tr><td bgcolor="${C.preto}" style="background:${C.preto};padding:20px 24px;border-radius:20px;color:#ffffff">
    <div style="font-size:12px;font-weight:700;letter-spacing:.08em;color:${C.lima}">RELATÓRIO SEMANAL · HYPEAPP</div>
    <div style="font-size:24px;font-weight:800;margin-top:6px">Semana de ${esc(semana)}</div>
  </td></tr>
  <tr><td style="padding:18px 6px 0;font-size:15px;line-height:1.55">
    ${(r.resumo || []).map((p) => `<p style="margin:0 0 12px">${esc(p)}</p>`).join('')}
    ${r.alertas && r.alertas.length ? h2('Alertas') + lista(r.alertas, (a) => `<b style="color:#A15C00">${esc(a.sinal)}</b>: ${esc(a.detalhe)}${a.acao ? `<br><span style="color:${C.cinza}">Primeira ação: ${esc(a.acao)}</span>` : ''}`) : ''}
    ${h2('Indicadores principais')}
  </td></tr>
  <tr><td><table role="presentation" width="100%" cellpadding="0" cellspacing="0">${linhasKpi.join('')}</table></td></tr>
  <tr><td style="padding:0 6px;font-size:15px;line-height:1.55">
    ${outros.length ? h2('Outros números') + lista(outros, (k) => `${esc(k.nome)}: <b>${esc(num(k.valor, k.tipo))}</b> <span style="color:${variacao(k.valor, k.anterior, k.menor_melhor).cor}">(${esc(variacao(k.valor, k.anterior, k.menor_melhor).txt)})</span>`) : ''}
    ${r.acoes && r.acoes.length ? h2('Ações sugeridas para a reunião') + lista(r.acoes, (a) => `<b>${esc(a.acao)}</b>${a.porque ? `<br><span style="color:${C.cinza}">${esc(a.porque)}</span>` : ''}`) : ''}
    ${r.pendencias && r.pendencias.length ? h2('Para completar') + lista(r.pendencias, (p) => esc(p)) : ''}
    <p style="margin:22px 0"><a href="${esc(LINK)}" style="display:inline-block;background:${C.roxo};color:#ffffff;text-decoration:none;font-weight:700;padding:12px 22px;border-radius:999px">Abrir o relatório completo</a></p>
  </td></tr>
  <tr><td bgcolor="${C.preto}" style="background:${C.preto};padding:16px 24px;border-radius:20px;color:#cfcfcf;font-size:12px;line-height:1.5">
    Enviado automaticamente pelo agente de análise do HypeApp, a partir do GA4 e do Search Console. O GA4 conta só quem aceitou os cookies de medição.
  </td></tr>
</table></td></tr></table></body></html>`;
  const texto = [`Relatório semanal HypeApp · semana de ${semana}`, '', ...(r.resumo || []), '',
    ...(r.alertas && r.alertas.length ? ['Alertas:', ...r.alertas.map((a) => `- ${a.sinal}: ${a.detalhe}`), ''] : []),
    'Indicadores principais:', ...principais.map((k) => `- ${k.nome}: ${num(k.valor, k.tipo) ?? (k.pendente || 'preencher')}`), '',
    ...(r.acoes && r.acoes.length ? ['Ações sugeridas:', ...r.acoes.map((a) => `- ${a.acao}`), ''] : []),
    `Relatório completo: ${LINK}`].join('\n');
  return { assunto: `Relatório semanal HypeApp · ${semana}`, html, texto };
}

async function main() {
  const r = JSON.parse(process.env.RELATORIO_JSON || 'null');
  if (!r || !r.semana) throw new Error('RELATORIO_JSON vazio ou sem a semana');
  const para = String(process.env.RELATORIO_EMAILS || '').split(',').map((s) => s.trim()).filter(emailValido);
  if (!para.length) throw new Error('variável RELATORIO_EMAILS sem e-mails válidos');
  const user = process.env.SMTP_USER, pass = process.env.SMTP_PASS;
  if (!user || !pass) throw new Error('segredos SMTP_USER e SMTP_PASS não configurados no GitHub');
  const from = process.env.SMTP_FROM || 'noreply@hypeapp.com.br';
  const { assunto, html, texto } = monta(r);
  const b64 = (s) => Buffer.from(s, 'utf8').toString('base64').replace(/.{76}/g, '$&\r\n');
  const id = () => Date.now().toString(36) + Math.random().toString(36).slice(2);
  const alt = 'hh-alt-' + id();
  const msg = [`From: HypeApp <${from}>`, `To: ${para.map((e) => `<${e}>`).join(', ')}`, `Subject: ${enc(assunto)}`, `Date: ${new Date().toUTCString()}`,
    `Message-ID: <${id()}@hypeapp.com.br>`, 'MIME-Version: 1.0', 'Auto-Submitted: auto-generated', `Content-Type: multipart/alternative; boundary="${alt}"`, '',
    `--${alt}`, 'Content-Type: text/plain; charset=UTF-8', 'Content-Transfer-Encoding: base64', '', b64(texto),
    `--${alt}`, 'Content-Type: text/html; charset=UTF-8', 'Content-Transfer-Encoding: base64', '', b64(html), `--${alt}--`].join('\r\n');
  if (process.env.SO_GERAR) { fs.writeFileSync(process.env.SO_GERAR, html); console.log('gerado', process.env.SO_GERAR); return; }
  let falhas = 0;
  for (const to of para) {
    try { await smtp({ host: process.env.SMTP_HOST || 'smtp.purelymail.com', port: +(process.env.SMTP_PORT || 465), user, pass, from, to, msg }); console.log('enviado para', to.replace(/^(.).*(@.*)$/, '$1***$2')); }
    catch (e) { falhas++; console.error('falha no envio:', e.message); }
  }
  if (falhas) process.exit(1);
}
main().catch((e) => { console.error(e.message); process.exit(1); });
