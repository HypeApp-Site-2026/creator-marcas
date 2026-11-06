// Recebe os formulários do site e cria o registro no CRM Comercial da plataforma Você no Hype, pelo webhook:
//   comercial  "Fale com nosso time" (marcas e agências)  → lead
//   suporte    chamado de suporte → API de chamados do HypeApp (POST /api/public/support/tickets), que devolve o número
//              do pedido. Se a API estiver fora do ar, o chamado vai ao CRM (como antes) para não se perder.
// Função do Vercel (Node), roda só no servidor.
//
// Variável opcional: SUPPORT_TICKETS_URL (padrão: https://api-v2.hypeapp.com.br/api/public/support/tickets).
//
// Variável de ambiente obrigatória (somente servidor, nunca exposta ao navegador):
//   PLATAFORMA_WEBHOOK_SECRET   segredo enviado no cabeçalho X-Webhook-Secret
//
// Regras:
// - o segredo nunca vai para o navegador, para respostas ou para logs;
// - o navegador recebe só "ok" ou uma mensagem genérica de erro;
// - nunca reenvia sozinho após erro ou timeout (o webhook não deduplica).

const { confirma } = require('./_email');

const WEBHOOK_URL = 'https://plataforma.vocenohype.com.br/api/public/leads';
const TICKETS_URL = process.env.SUPPORT_TICKETS_URL || 'https://api-v2.hypeapp.com.br/api/public/support/tickets';
// Assunto do formulário → category da API de chamados
const CATEGORIA = { conta: 'account', exclusao: 'account', redes: 'account', campanha: 'campaign', pagamento: 'billing',
  erro: 'bug', denuncia: 'other', outro: 'other' };
// Campo da API → campo do formulário (para marcar o campo certo quando a API recusar)
const CAMPO_API = { name: 'nome', email: 'email', subject: 'assunto', message: 'descricao' };
const TIMEOUT_MS = 10000;
const MAX_BODY = 16 * 1024;

// Rótulos legíveis das opções (mesmos textos das páginas /contato/marcas/ e /suporte/)
const OPCOES_COMERCIAL = {
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
const OPCOES_SUPORTE = {
  uso: { app: 'O app (creator)', painel: 'O painel (marca ou agência)' },
  assunto: { conta: 'Conta e acesso', redes: 'Redes sociais', campanha: 'Campanha ou entrega', pagamento: 'Pagamento ou saque',
    erro: 'Erro no app', denuncia: 'Denúncia', exclusao: 'Excluir minha conta', outro: 'Outro' },
  rede: { instagram: 'Instagram', tiktok: 'TikTok', youtube: 'YouTube' },
  etapa: { convite: 'Convite', roteiro: 'Roteiro', conteudo: 'Conteúdo', publicacao: 'Publicação' },
};

// Limite de tamanho por campo recebido do formulário (validação no servidor)
const LIMITES = {
  nome: 200, email: 200, whatsapp: 60, empresa: 200, cargo: 120, site: 300, cidade: 120, mensagem: 3000,
  descricao: 3000, passos: 3000, erro_rede: 500, email_conta: 200, campanha_nome: 200, alvo: 500, aparelho: 120, versao: 40,
  pagina: 500, referrer: 500, landing: 500, utm_source: 120, utm_medium: 120, utm_campaign: 200, utm_content: 200, utm_term: 200,
  gclid: 300, fbclid: 300,
};
const LIMITE_PADRAO = 300;

const FORMS = {
  comercial: {
    proxima: '/contato/enviado/', opcoes: OPCOES_COMERCIAL,
    obrigatorios: ['empresa', 'site', 'segmento', 'cidade', 'nome', 'cargo', 'email', 'whatsapp', 'experiencia', 'campanhas_mes', 'verba',
      'redes', 'objetivo', 'interesses', 'gestao_hoje', 'usuarios', 'agencia', 'inicio', 'aceite'],
  },
  suporte: {
    proxima: '/suporte/enviado/', opcoes: OPCOES_SUPORTE,
    obrigatorios: ['uso', 'assunto', 'nome', 'email', 'descricao', 'aceite'],
  },
};

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
  const m = OPCOES_COMERCIAL[campo] || OPCOES_SUPORTE[campo];
  if (Array.isArray(v)) return v.map((x) => (m && m[x]) || x).join(', ');
  return (m && m[v]) || v;
};

function responder(req, res, status, ok, erro, campos, proxima = '/contato/enviado/', numero) {
  const querJson = (req.headers.accept || '').includes('application/json');
  const n = numero != null && /^\d{1,12}$/.test(String(numero)) ? Number(numero) : null;
  if (querJson) return res.status(status).json(ok ? (n != null ? { ok: true, numero: n } : { ok: true }) : campos ? { ok: false, erro, campos } : { ok: false, erro });
  if (ok) { res.setHeader('Location', proxima + (n != null ? `?pedido=${n}` : '')); return res.status(303).end(); }
  res.setHeader('Content-Type', 'text/html; charset=utf-8');
  return res.status(status).send(`<!doctype html><meta charset="utf-8"><title>Não foi possível enviar</title>
<p style="font-family:sans-serif;max-width:560px;margin:60px auto">${esc(erro)}
<br><a href="javascript:history.back()">Voltar ao formulário</a></p>`);
}

function montaLead(d, agora, tipo = 'comercial') {
  const temGclid = !!d.gclid, temFbclid = !!d.fbclid;
  const source = temGclid ? 'google-ads' : temFbclid ? 'meta-ads' : (d.utm_source || 'site');
  const linha = (p, r) => (r ? `${p}: ${r}` : null);
  const umaLinha = (t) => t && t.replace(/\s*\n\s*/g, ' / ');

  const motivos = [];
  if (d.agencia === 'sim') motivos.push('agência');
  if (['20-50k', '50k-mais'].includes(d.verba)) motivos.push('verba alta');
  if (d.inicio === 'agora') motivos.push('começar agora');

  const respostas = tipo === 'suporte' ? [
    'Tipo: CHAMADO DE SUPORTE (não é lead comercial)',
    linha('Usa', rotulo('uso', d.uso)),
    linha('Assunto', rotulo('assunto', d.assunto)),
    linha('E-mail da conta', d.email_conta),
    linha('Rede', rotulo('rede', d.rede)),
    linha('@ na rede', d.arroba),
    linha('Mensagem de erro da rede', d.erro_rede),
    linha('Campanha', d.campanha_nome),
    linha('Etapa', rotulo('etapa', d.etapa)),
    linha('Data da solicitação de saque', d.data_saque),
    linha('Valor', d.valor),
    linha('Aparelho e sistema', d.aparelho),
    linha('Versão do app', d.versao),
    linha('Passos até o erro', umaLinha(d.passos)),
    linha('Link ou @ denunciado', d.alvo),
    linha('Descrição', umaLinha(d.descricao)),
    linha('Consentimento LGPD', d.aceite ? 'Sim' : ''),
  ] : [
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

  const lead = tipo === 'suporte' ? {
    name: corta(d.nome, 200),
    email: d.email ? corta(d.email, 200) : undefined,
    source: corta(source, 120),
    source_form: 'Site-HypeApp',
    notes,
  } : {
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

// Monta o corpo do chamado para a API de suporte (limites da API: name 2-100, subject 3-120, message 10-5000).
function montaChamado(d, base, teste) {
  const r = (campo, v) => (OPCOES_SUPORTE[campo] && OPCOES_SUPORTE[campo][v]) || v || '';
  const linha = (p, v) => (v ? `${p}: ${v}` : null);
  const uso = d.uso === 'painel' ? 'Painel (marca ou agência)' : 'App (creator)';
  let subject = `${r('assunto', d.assunto) || 'Suporte'} · ${uso}`;
  if (d.assunto === 'campanha' && d.campanha_nome) subject += ` · ${d.campanha_nome}`;
  if (teste) subject = `[TESTE] ${subject}`;
  const detalhes = [
    linha('Usa', uso),
    linha('Assunto', r('assunto', d.assunto)),
    linha('E-mail da conta', d.email_conta),
    linha('Rede', r('rede', d.rede)),
    linha('@ na rede', d.arroba),
    linha('Mensagem de erro da rede', d.erro_rede),
    linha('Campanha', d.campanha_nome),
    linha('Etapa', r('etapa', d.etapa)),
    linha('Data da solicitação de saque', d.data_saque),
    linha('Valor', d.valor),
    linha('Aparelho e sistema', d.aparelho),
    linha('Versão do app', d.versao),
    linha('Link ou @ denunciado', d.alvo),
  ].filter(Boolean);
  const blocos = teste ? ['AMBIENTE DE TESTE (teste.hypeapp.com.br): não é um chamado real.', d.descricao] : [d.descricao];
  if (d.passos) blocos.push(`O que fez até o erro aparecer:\n${d.passos}`);
  if (detalhes.length) blocos.push(detalhes.join('\n'));
  const corpo = {
    name: corta(d.nome, 100),
    email: d.email,
    subject: corta(subject, 120),
    message: corta(blocos.join('\n\n'), 5000),
    category: CATEGORIA[d.assunto] || 'other',
  };
  const pag = String(d.pagina || '');
  corpo.page_url = /^https:\/\//.test(pag) ? corta(pag, 500) : `${base}/suporte/`;
  return corpo;
}

// Lê a lista de problemas do 400 sem depender do formato exato: procura os nomes dos campos da API no JSON.
function camposRecusados(j) {
  const txt = JSON.stringify(j || {});
  return Object.keys(CAMPO_API).filter((k) => new RegExp(`"${k}"|\\b${k}\\b`).test(txt)).map((k) => CAMPO_API[k]);
}

// Envia à API de chamados. Devolve { ok, numero } | { status, campos } | { falha } (fora do ar: cai no CRM).
async function enviaChamado(corpo, req) {
  const ctrl = new AbortController();
  const timer = setTimeout(() => ctrl.abort(), TIMEOUT_MS);
  const ip = String(req.headers['x-forwarded-for'] || '').split(',')[0].trim();
  let r;
  try {
    r = await fetch(TICKETS_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Accept: 'application/json', ...(ip ? { 'X-Forwarded-For': ip } : {}) },
      body: JSON.stringify(corpo),
      signal: ctrl.signal,
    });
  } catch (e) {
    const timeout = e && e.name === 'AbortError';
    console.error('[chamado] falha ao chamar a API de chamados:', timeout ? 'timeout de 10 s' : (e && e.message) || 'erro de rede');
    return { falha: true, timeout };
  } finally {
    clearTimeout(timer);
  }
  const j = await r.json().catch(() => ({}));
  if (r.status === 201) {
    const numero = j && j.data && j.data.number;
    return { ok: true, numero: numero != null && /^\d{1,12}$/.test(String(numero)) ? Number(numero) : null };
  }
  if (r.status === 400) {
    const campos = camposRecusados(j);
    console.error('[chamado] API recusou os dados (400), campos:', campos.join(', ') || 'não identificados');
    return { status: 400, campos };
  }
  if (r.status === 429) { console.error('[chamado] API respondeu 429: mais de 5 envios por minuto do mesmo IP.'); return { status: 429 }; }
  console.error(`[chamado] API de chamados respondeu ${r.status}.`);
  return { falha: true };
}

async function handler(req, res) {
  if (req.method !== 'POST') { res.setHeader('Allow', 'POST'); return res.status(405).end(); }

  const d = normaliza(lerCorpo(req));
  const tipo = d['form-name'] === 'suporte' ? 'suporte' : 'comercial';
  const form = FORMS[tipo];
  const resp = (status, ok, erro, campos, numero) => responder(req, res, status, ok, erro, campos, form.proxima, numero);
  if (d['bot-field']) return resp(200, true); // robô: finge que deu certo, não chama o webhook

  // Validação no servidor (espelha a do formulário) e limite de tamanho por campo.
  // Devolve só os nomes dos campos do próprio formulário, nunca detalhes do webhook.
  const vazio = (v) => (Array.isArray(v) ? v.length === 0 : !v);
  const ruins = new Set(form.obrigatorios.filter((k) => vazio(d[k])));
  if (!d.nome) ruins.add('nome');
  if (!d.email && !d.whatsapp) { ruins.add('email'); ruins.add('whatsapp'); }
  if (d.email && !emailOk(d.email)) ruins.add('email');
  if (tipo === 'suporte') { // limites da API de chamados
    if (!d.email) ruins.add('email');
    if (d.nome && d.nome.length < 2) ruins.add('nome');
    if (d.nome && d.nome.length > 100) ruins.add('nome');
    if (d.descricao && d.descricao.length < 10) ruins.add('descricao');
  }
  for (const [k, v] of Object.entries(d)) {
    const lim = LIMITES[k] || LIMITE_PADRAO;
    const partes = Array.isArray(v) ? v : [v];
    if (partes.length > 20 || partes.some((x) => x.length > lim)) ruins.add(k);
  }
  for (const campo of Object.keys(form.opcoes)) {
    const partes = Array.isArray(d[campo]) ? d[campo] : d[campo] ? [d[campo]] : [];
    if (partes.some((x) => !(x in form.opcoes[campo]))) ruins.add(campo);
  }
  if (ruins.size) {
    console.error(`[lead] formulário ${tipo} recusado na validação do site, campos:`, [...ruins].join(', '));
    return resp(400, false, MSG.invalido, [...ruins]);
  }

  const host = String(req.headers['x-forwarded-host'] || req.headers.host || '');
  const teste = /^teste\./.test(host);
  const base = /^(teste|www)\.hypeapp\.com\.br$/.test(host) ? `https://${host}`
    : (process.env.VERCEL_ENV === 'production' ? 'https://www.hypeapp.com.br' : 'https://teste.hypeapp.com.br');

  let aviso = '';
  if (tipo === 'suporte') {
    const c = await enviaChamado(montaChamado(d, base, teste), req);
    if (c.ok) {
      // e-mail de confirmação com o número do pedido (falha no e-mail não afeta o chamado)
      await confirma(tipo, { ...d, pedido: c.numero }, OPCOES_SUPORTE, base);
      return resp(200, true, '', null, c.numero);
    }
    if (c.status === 400) return resp(400, false, MSG.invalido, c.campos.length ? c.campos : undefined);
    if (c.status === 429) return resp(429, false, MSG.limite);
    // API fora do ar: o chamado segue para o CRM, como antes, para não se perder
    aviso = c.timeout
      ? 'ATENÇÃO: a API de chamados não respondeu em 10 s. Confira se o chamado já existe lá antes de abrir de novo.'
      : 'ATENÇÃO: a API de chamados estava indisponível. Abrir o chamado manualmente.';
  }

  const segredo = process.env.PLATAFORMA_WEBHOOK_SECRET;
  if (!segredo) {
    console.error('[lead] PLATAFORMA_WEBHOOK_SECRET não configurada: lead não enviado ao CRM.');
    return resp(503, false, MSG.temporario);
  }

  let corpo = montaLead(d, new Date(), tipo);
  if (aviso) {
    const lead = JSON.parse(corpo);
    lead.notes = (aviso + '\n' + lead.notes).slice(0, 5000);
    corpo = JSON.stringify(lead);
  }
  if (teste) { // enviado pelo endereço de teste da equipe: marca nome e notas
    const lead = JSON.parse(corpo);
    lead.name = ('[TESTE] ' + lead.name).slice(0, 200);
    lead.notes = ('AMBIENTE DE TESTE (teste.hypeapp.com.br): não é um contato real.\n' + lead.notes).slice(0, 5000);
    corpo = JSON.stringify(lead);
  }
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
    return resp(502, false, MSG.temporario);
  } finally {
    clearTimeout(timer);
  }

  if (r.status === 201) {
    // lead gravado: e-mail de confirmação para quem enviou (só com SMTP_USER e SMTP_PASS; falha não afeta o envio)
    await confirma(tipo, d, tipo === 'suporte' ? OPCOES_SUPORTE : OPCOES_COMERCIAL, base);
    return resp(200, true);
  }
  if (r.status === 400) { console.error('[lead] webhook recusou os dados (400).'); return resp(400, false, MSG.invalido); }
  if (r.status === 401) { console.error('[lead] webhook respondeu 401: segredo ausente ou errado. Confira PLATAFORMA_WEBHOOK_SECRET no Vercel.'); return resp(502, false, MSG.temporario); }
  if (r.status === 429) { console.error('[lead] webhook respondeu 429: limite de envios.'); return resp(429, false, MSG.limite); }
  console.error(`[lead] webhook respondeu ${r.status}.`);
  return resp(502, false, MSG.temporario);
}

module.exports = handler;
module.exports.montaLead = montaLead;
