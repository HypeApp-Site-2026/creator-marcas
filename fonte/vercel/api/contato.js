// Recebe os formulários "Falar com nosso time" (comercial) e "Suporte" e envia por e-mail.
// Função do Vercel (Node). O envio usa a API do Resend (https://resend.com):
//   RESEND_API_KEY  chave da conta no Resend (obrigatória)
//   FORM_TO         destino (padrão: contato@vocenohype.com.br)
//   FORM_FROM       remetente verificado no Resend (padrão: "Site HypeApp <onboarding@resend.dev>",
//                   que só entrega para o e-mail dono da conta Resend; troque depois de verificar o domínio)

const DESTINO = process.env.FORM_TO || 'contato@vocenohype.com.br';
const REMETENTE = process.env.FORM_FROM || 'Site HypeApp <onboarding@resend.dev>';

const FORMS = {
  comercial: {
    titulo: 'Falar com nosso time (marcas e agências)',
    proxima: '/contato/enviado/',
    obrigatorios: ['empresa', 'site', 'segmento', 'cidade', 'nome', 'cargo', 'email', 'whatsapp', 'experiencia', 'campanhas_mes', 'verba',
      'redes', 'objetivo', 'interesses', 'gestao_hoje', 'usuarios', 'agencia', 'inicio', 'aceite'],
    rotulos: {
      prioridade: 'Fila', empresa: 'Empresa', site: 'Site ou Instagram', segmento: 'Segmento', cidade: 'Cidade e estado',
      nome: 'Nome', cargo: 'Cargo', email: 'E-mail', whatsapp: 'WhatsApp',
      experiencia: 'Já trabalha com influenciadores', campanhas_mes: 'Campanhas por mês', verba: 'Verba mensal', redes: 'Redes',
      objetivo: 'Objetivo', interesses: 'Interesses no painel', gestao_hoje: 'Como gerencia hoje',
      usuarios: 'Pessoas que usariam o painel', agencia: 'É agência', inicio: 'Quando começar', mensagem: 'Algo mais',
    },
  },
  suporte: {
    titulo: 'Chamado de suporte',
    proxima: '/suporte/enviado/',
    obrigatorios: ['uso', 'assunto', 'nome', 'email', 'descricao', 'aceite'],
    rotulos: {
      uso: 'Usa', assunto: 'Assunto', email_conta: 'E-mail da conta', rede: 'Rede', arroba: '@ na rede', erro_rede: 'Erro da rede',
      campanha_nome: 'Campanha', etapa: 'Etapa', data_saque: 'Data do saque', valor: 'Valor', aparelho: 'Aparelho',
      versao: 'Versão do app', passos: 'Passos até o erro', alvo: 'Denúncia (link ou @)', nome: 'Nome', email: 'E-mail', descricao: 'Descrição',
    },
  },
};

const esc = (s) => String(s).replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
const emailOk = (s) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(s || '');

function lerCorpo(req) {
  if (req.body && typeof req.body === 'object') return req.body;
  const txt = typeof req.body === 'string' ? req.body : '';
  return Object.fromEntries(new URLSearchParams(txt));
}

function responder(req, res, status, ok, proxima, erro) {
  const querJson = (req.headers.accept || '').includes('application/json');
  if (querJson) return res.status(status).json(ok ? { ok: true } : { ok: false, erro });
  if (ok) { res.setHeader('Location', proxima); return res.status(303).end(); }
  res.setHeader('Content-Type', 'text/html; charset=utf-8');
  return res.status(status).send(`<!doctype html><meta charset="utf-8"><title>Não foi possível enviar</title>
<p style="font-family:sans-serif;max-width:560px;margin:60px auto">Não foi possível enviar: ${esc(erro)}.
<br><a href="javascript:history.back()">Voltar ao formulário</a> ou escreva para ${esc(DESTINO)}.</p>`);
}

module.exports = async (req, res) => {
  if (req.method !== 'POST') { res.setHeader('Allow', 'POST'); return res.status(405).end(); }
  const bruto = lerCorpo(req);
  const d = Object.fromEntries(Object.entries(bruto).map(([k, v]) => [k, Array.isArray(v) ? v.join(', ') : v]));
  const form = FORMS[d['form-name']];
  if (!form) return responder(req, res, 400, false, '/', 'formulário desconhecido');
  if (d['bot-field']) return responder(req, res, 200, true, form.proxima); // robô: finge que deu certo

  const faltando = form.obrigatorios.filter((k) => !String(d[k] || '').trim());
  if (faltando.length) return responder(req, res, 400, false, form.proxima, 'faltam campos obrigatórios');
  if (!emailOk(d.email)) return responder(req, res, 400, false, form.proxima, 'e-mail inválido');
  if (Object.values(d).some((v) => String(v).length > 5000)) return responder(req, res, 400, false, form.proxima, 'texto muito longo');

  if (!process.env.RESEND_API_KEY) {
    console.error('RESEND_API_KEY não configurada');
    return responder(req, res, 503, false, form.proxima, 'o envio ainda não está configurado');
  }

  // Fila prioritária: agência, verba alta (a partir de R$ 20 mil/mês) ou começar agora
  if (form === FORMS.comercial) {
    const motivos = [];
    if (d.agencia === 'sim') motivos.push('agência');
    if (['20-50k', '50k-mais'].includes(d.verba)) motivos.push('verba alta');
    if (d.inicio === 'agora') motivos.push('começar agora');
    d.prioridade = motivos.length ? `PRIORITÁRIA (${motivos.join(', ')})` : 'normal';
  }

  const linhas = Object.entries(form.rotulos)
    .filter(([k]) => String(d[k] || '').trim())
    .map(([k, r]) => `<tr><td style="padding:6px 12px 6px 0;color:#666;vertical-align:top">${esc(r)}</td><td style="padding:6px 0">${esc(d[k]).replace(/\n/g, '<br>')}</td></tr>`)
    .join('');
  const texto = Object.entries(form.rotulos).filter(([k]) => String(d[k] || '').trim()).map(([k, r]) => `${r}: ${d[k]}`).join('\n');
  const assunto = form === FORMS.comercial
    ? `[Site]${d.prioridade && d.prioridade !== 'normal' ? ' [PRIORIDADE]' : ''} Marca: ${d.empresa} (${d.nome})`
    : `[Site] Suporte: ${d.assunto} (${d.nome})`;

  try {
    const r = await fetch('https://api.resend.com/emails', {
      method: 'POST',
      headers: { Authorization: `Bearer ${process.env.RESEND_API_KEY}`, 'Content-Type': 'application/json' },
      body: JSON.stringify({
        from: REMETENTE, to: [DESTINO], reply_to: d.email, subject: assunto.slice(0, 180), text: texto,
        html: `<h2 style="font-family:sans-serif">${esc(form.titulo)}</h2><table style="font-family:sans-serif;font-size:14px">${linhas}</table>`,
      }),
    });
    if (!r.ok) { console.error('Resend', r.status, await r.text()); return responder(req, res, 502, false, form.proxima, 'falha no envio'); }
  } catch (e) {
    console.error(e);
    return responder(req, res, 502, false, form.proxima, 'falha no envio');
  }
  return responder(req, res, 200, true, form.proxima);
};
