// Recebe o formulário "Fale com nosso time" (marcas e agências) e cria o lead no CRM Comercial
// da plataforma Você no Hype, pelo webhook. Função do Vercel (Node), roda só no servidor.
//
// Variável de ambiente obrigatória (somente servidor, nunca exposta ao navegador):
//   PLATAFORMA_WEBHOOK_SECRET   segredo enviado no cabeçalho X-Webhook-Secret
//
// Regras:
// - o segredo nunca vai para o navegador, para respostas ou para logs;
// - o navegador recebe só "ok" ou uma mensagem genérica de erro;
// - nunca reenvia sozinho após erro ou timeout (o webhook não deduplica).

const WEBHOOK_URL = 'https://plataforma.vocenohype.com.br/api/public/leads';
const TIMEOUT_MS = 10000;
const MAX_BODY = 16 * 1024;
const PROXIMA = '/contato/enviado/';

// Rótulos legíveis das opções do formulário (mesmos textos da página /contato/marcas/)
const OPCOES = {
  segmento: { moda: 'Moda', beleza: 'Beleza', alimentos: 'Alimentos', tecnologia: 'Tecnologia', servicos: 'Serviços', outro: 'Outro' },
  experiencia: { nunca: 'Nunca', ocasional: 'Ocasionalmente', frequente: 'Com frequência' },
  campanhas_mes: { '1-2': '1 a 2', '3-10': '3 a 10', '10-mais': 'Mais de 10' },
  verba: { 'ate-5k': 'Até R$ 5 mil', '5-20k': 'R$ 5 mil a R$ 20 mil', '20-50k': 'R$ 20 mil a R$ 50 mil', '50k-mais': 'Acima de R$ 50 mil', 'nao-sei': 'Ainda não sei' },
  redes: { instagram: 'Instagram', tiktok: 'TikTok', youtube: 'YouTube', kwai: 'Kwai' },
  objetivo: { lancamento: 'Lançar produto', alcance: 'Ganhar alcance', vendas: 'Gerar vendas', recorrencia: 'Recorrência', outro: 'Outro' },
  interesses: { criadores: 'Encontrar creators', aprovacoes: 'Aprovar roteiros e conteúdos', pagamentos: 'Pagamentos', lives: 'Lives', metricas: 'Métricas' },
  gestao_hoje: { planilha: 'Planilha', agencia: 'Agência', plataforma: 'Outra plataforma', nada: 'Ainda não gerencio' },
  usuarios: { 1: '1', '2-5': '2 a 5', '6-mais': '6 ou mais' },
  agencia: { sim: 'Sim', nao: 'Não' },
  inicio: { agora: 'Agora', '30-dias': 'Em até 30 dias', pesquisando: 'Só pesquisando' },
};

// Limite de tamanho por campo recebido do formulário (validação no servidor)
const LIMITES = {
  nome: 200, email: 200, whatsapp: 60, empresa: 200, cargo: 120, site: 300, cidade: 120, mensagem: 3000,
  pagina: 500, referrer: 500, landing: 500, utm_source: 120, utm_medium: 120, utm_campaign: 200, utm_content: 200, utm_term: 200,
  gclid: 300, fbclid: 300,
};
const LIMITE_PADRAO = 300;

const OBRIGATORIOS = ['empresa', 'site', 'segmento', 'cidade', 'nome', 'cargo', 'email', 'whatsapp', 'experiencia', 'campanhas_mes', 'verba',
  'redes', 'objetivo', 'interesses', 'gestao_hoje', 'usuarios', 'agencia', 'inicio', 'aceite'];

const MSG = {
  invalido: 'Revise os campos do formulário e tente de novo.',
  temporario: 'Não foi possível enviar agora, tente novamente em instantes.',
  limite: 'Muitos envios em pouco tempo. Tente de novo em instantes.',
};

const emailOk = (s) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(s || '');
const corta = (s, n) => (s.length > n ? s.slice(0, n - 1) + '…' : s);
const esc = (s) => String(s).replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));

function lerCorpo(req) {
  if (req.body && typeof req.body === 'object') return req.body;
  const txt = typeof req.body === 'string' ? req.body : '';
  const p = new URLSearchParams(txt), o = {};
  for (const k of new Set(p.keys())) { const v = p.getAll(k); o[k] = v.length > 1 ? v : v[0]; }
  return o;
}

// Normaliza: texto simples, sem espaços nas pontas; listas viram arrays de texto
function normaliza(bruto) {
  const d = {};
  for (const [k, v] of Object.entries(bruto)) {
    d[k] = Array.isArray(v) ? v.map((x) => String(x).trim()).filter(Boolean) : String(v ?? '').trim();
  }
  return d;
}

const rotulo = (campo, v) => {
  const m = OPCOES[campo];
  if (Array.isArray(v)) return v.map((x) => (m && m[x]) || x).join(', ');
  return (m && m[v]) || v;
};

function responder(req, res, status, ok, erro, campos) {
  const querJson = (req.headers.accept || '').includes('application/json');
  if (querJson) return res.status(status).json(ok ? { ok: true } : campos ? { ok: false, erro, campos } : { ok: false, erro });
  if (ok) { res.setHeader('Location', PROXIMA); return res.status(303).end(); }
  res.setHeader('Content-Type', 'text/html; charset=utf-8');
  return res.status(status).send(`<!doctype html><meta charset="utf-8"><title>Não foi possível enviar</title>
<p style="font-family:sans-serif;max-width:560px;margin:60px auto">${esc(erro)}
<br><a href="javascript:history.back()">Voltar ao formulário</a></p>`);
}

function montaLead(d, agora) {
  const temGclid = !!d.gclid, temFbclid = !!d.fbclid;
  const source = temGclid ? 'google-ads' : temFbclid ? 'meta-ads' : (d.utm_source || 'site');

  const motivos = [];
  if (d.agencia === 'sim') motivos.push('agência');
  if (['20-50k', '50k-mais'].includes(d.verba)) motivos.push('verba alta');
  if (d.inicio === 'agora') motivos.push('começar agora');

  const linha = (p, r) => (r ? `${p}: ${r}` : null);
  const respostas = [
    linha('Fila', motivos.length ? `PRIORITÁRIA (${motivos.join(', ')})` : 'normal'),
    linha('Site ou Instagram', d.site),
    linha('Cidade e estado', d.cidade),
    linha('Quantas campanhas pretende fazer por mês', rotulo('campanhas_mes', d.campanhas_mes)),
    linha('Que redes importam', rotulo('redes', d.redes)),
    linha('Qual o principal objetivo', rotulo('objetivo', d.objetivo)),
    linha('O que mais interessa no painel', rotulo('interesses', d.interesses)),
    linha('Como gerencia isso hoje', rotulo('gestao_hoje', d.gestao_hoje)),
    linha('Quantas pessoas da equipe usariam o painel', rotulo('usuarios', d.usuarios)),
    linha('É uma agência que atende várias marcas', rotulo('agencia', d.agencia)),
    linha('Consentimento LGPD', d.aceite ? 'Sim' : ''),
    linha('Quer contar algo mais', d.mensagem && d.mensagem.replace(/\s*\n\s*/g, ' / ')),
  ];
  const origem = [
    linha('Página de origem', d.pagina),
    linha('Primeira página da visita', d.landing),
    linha('Referrer', d.referrer),
    ...['utm_source', 'utm_medium', 'utm_campaign', 'utm_content', 'utm_term', 'gclid', 'fbclid'].map((k) => linha(k, d[k])),
    linha('Data/hora do envio', agora.toISOString()),
  ];
  const notes = corta([...respostas, ...origem].filter(Boolean).join('\n'), 5000);

  const lead = {
    name: corta(d.nome, 200),
    email: d.email ? corta(d.email, 200) : undefined,
    phone: d.whatsapp ? corta(d.whatsapp, 60) : undefined,
    company: d.empresa ? corta(d.empresa, 200) : undefined,
    role: d.cargo ? corta(d.cargo, 120) : undefined,
    industry: d.segmento ? corta(rotulo('segmento', d.segmento), 120) : undefined,
    monthly_budget: d.verba ? corta(rotulo('verba', d.verba), 60) : undefined,
    urgency: d.inicio ? corta(rotulo('inicio', d.inicio), 120) : undefined,
    agency_experience: d.experiencia ? corta(`Já trabalha com influenciadores: ${rotulo('experiencia', d.experiencia)}`, 500) : undefined,
    source: corta(source, 120),
    source_form: 'Site-HypeApp',
    notes,
  };
  for (const k of Object.keys(lead)) if (lead[k] === undefined || lead[k] === '') delete lead[k];

  // Garante o teto de 16 KB do corpo
  let corpo = JSON.stringify(lead);
  while (Buffer.byteLength(corpo, 'utf8') > MAX_BODY && lead.notes.length > 200) {
    lead.notes = corta(lead.notes, Math.floor(lead.notes.length * 0.8));
    corpo = JSON.stringify(lead);
  }
  return corpo;
}

async function handler(req, res) {
  if (req.method !== 'POST') { res.setHeader('Allow', 'POST'); return res.status(405).end(); }

  const d = normaliza(lerCorpo(req));
  if (d['bot-field']) return responder(req, res, 200, true); // robô: finge que deu certo, não chama o webhook

  // Validação no servidor (espelha a do formulário) e limite de tamanho por campo.
  // Devolve só os nomes dos campos do próprio formulário, nunca detalhes do webhook.
  const vazio = (v) => (Array.isArray(v) ? v.length === 0 : !v);
  const ruins = new Set(OBRIGATORIOS.filter((k) => vazio(d[k])));
  if (!d.nome) ruins.add('nome');
  if (!d.email && !d.whatsapp) { ruins.add('email'); ruins.add('whatsapp'); }
  if (d.email && !emailOk(d.email)) ruins.add('email');
  for (const [k, v] of Object.entries(d)) {
    const lim = LIMITES[k] || LIMITE_PADRAO;
    const partes = Array.isArray(v) ? v : [v];
    if (partes.length > 20 || partes.some((x) => x.length > lim)) ruins.add(k);
  }
  for (const campo of Object.keys(OPCOES)) {
    const partes = Array.isArray(d[campo]) ? d[campo] : d[campo] ? [d[campo]] : [];
    if (partes.some((x) => !(x in OPCOES[campo]))) ruins.add(campo);
  }
  if (ruins.size) {
    console.error('[lead] formulário recusado na validação do site, campos:', [...ruins].join(', '));
    return responder(req, res, 400, false, MSG.invalido, [...ruins]);
  }

  const segredo = process.env.PLATAFORMA_WEBHOOK_SECRET;
  if (!segredo) {
    console.error('[lead] PLATAFORMA_WEBHOOK_SECRET não configurada: lead não enviado ao CRM.');
    return responder(req, res, 503, false, MSG.temporario);
  }

  const corpo = montaLead(d, new Date());
  const ctrl = new AbortController();
  const timer = setTimeout(() => ctrl.abort(), TIMEOUT_MS);
  let r;
  try {
    r = await fetch(WEBHOOK_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'X-Webhook-Secret': segredo },
      body: corpo,
      signal: ctrl.signal,
    });
  } catch (e) {
    console.error('[lead] falha ao chamar o webhook:', e && e.name === 'AbortError' ? 'timeout de 10 s' : (e && e.message) || 'erro de rede');
    return responder(req, res, 502, false, MSG.temporario);
  } finally {
    clearTimeout(timer);
  }

  if (r.status === 201) return responder(req, res, 200, true);
  if (r.status === 400) { console.error('[lead] webhook recusou os dados (400).'); return responder(req, res, 400, false, MSG.invalido); }
  if (r.status === 401) { console.error('[lead] webhook respondeu 401: segredo ausente ou errado. Confira PLATAFORMA_WEBHOOK_SECRET no Vercel.'); return responder(req, res, 502, false, MSG.temporario); }
  if (r.status === 429) { console.error('[lead] webhook respondeu 429: limite de envios.'); return responder(req, res, 429, false, MSG.limite); }
  console.error(`[lead] webhook respondeu ${r.status}.`);
  return responder(req, res, 502, false, MSG.temporario);
}

module.exports = handler;
module.exports.montaLead = montaLead;
