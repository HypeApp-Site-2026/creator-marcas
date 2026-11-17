// Reações dos artigos do blog (Like, Amei, Uau, Genial).
//
// GET  /api/reacoes?slug=<artigo>                → { ok, contagem: { like, amei, uau, genial } }
// POST /api/reacoes  { slug, tipo, anterior }    → { ok, contagem }
//   tipo: reação escolhida agora (ou vazio para tirar a reação)
//   anterior: reação que a pessoa tinha antes neste artigo (o navegador lembra), para trocar sem somar duas vezes
//
// Guarda só contagens por artigo, nenhum dado pessoal. O IP só serve para o limite de cliques por minuto
// (guardado como hash, apagado em 60 s).
//
// Banco: Upstash Redis pela integração do Vercel (Storage → Upstash → conectar ao projeto hype-site).
// Variáveis aceitas: KV_REST_API_URL + KV_REST_API_TOKEN  ou  UPSTASH_REDIS_REST_URL + UPSTASH_REDIS_REST_TOKEN.
// Sem banco configurado, responde 503 e o site esconde as reações.

const crypto = require('crypto');
const SLUGS = new Set(require('./_slugs.json'));
const TIPOS = ['like', 'amei', 'uau', 'genial'];
const HOSTS = /^(www|teste)\.hypeapp\.com\.br$/;
const LIMITE_MIN = 20; // cliques por IP por minuto

const URL_DB = process.env.KV_REST_API_URL || process.env.UPSTASH_REDIS_REST_URL;
const TOKEN_DB = process.env.KV_REST_API_TOKEN || process.env.UPSTASH_REDIS_REST_TOKEN;

async function redis(comandos) {
  const ctrl = new AbortController();
  const t = setTimeout(() => ctrl.abort(), 5000);
  try {
    const r = await fetch(URL_DB.replace(/\/$/, '') + '/pipeline', {
      method: 'POST',
      headers: { Authorization: 'Bearer ' + TOKEN_DB, 'Content-Type': 'application/json' },
      body: JSON.stringify(comandos),
      signal: ctrl.signal,
    });
    if (!r.ok) throw new Error('status ' + r.status);
    return (await r.json()).map((x) => x.result);
  } finally {
    clearTimeout(t);
  }
}

const contagem = (arr) => {
  const o = { like: 0, amei: 0, uau: 0, genial: 0 };
  for (let i = 0; arr && i < arr.length; i += 2) if (TIPOS.includes(arr[i])) o[arr[i]] = Math.max(0, parseInt(arr[i + 1], 10) || 0);
  return o;
};

const ipDoCliente = (req) => String(req.headers['x-real-ip'] || String(req.headers['x-forwarded-for'] || '').split(',')[0]).trim();

module.exports = async function handler(req, res) {
  res.setHeader('Cache-Control', 'no-store');
  res.setHeader('X-Robots-Tag', 'noindex');
  if (!URL_DB || !TOKEN_DB) return res.status(503).json({ ok: false, erro: 'sem-banco' });

  if (req.method === 'GET') {
    const slug = String((req.query && req.query.slug) || '');
    if (!SLUGS.has(slug)) return res.status(404).json({ ok: false, erro: 'artigo' });
    try {
      const [h] = await redis([['HGETALL', 'reacoes:' + slug]]);
      return res.status(200).json({ ok: true, contagem: contagem(h) });
    } catch (e) {
      console.error('[reacoes] leitura falhou:', e && e.name === 'AbortError' ? 'timeout' : (e && e.message) || 'erro');
      return res.status(503).json({ ok: false, erro: 'banco' });
    }
  }

  if (req.method !== 'POST') { res.setHeader('Allow', 'GET, POST'); return res.status(405).end(); }

  // Mesmas defesas do formulário: só das páginas do site, corpo pequeno, JSON
  let origemOk = false;
  try { const h = new URL(String(req.headers.origin || '')).hostname; origemOk = HOSTS.test(h) || (!process.env.VERCEL_ENV && /^(localhost|127\.0\.0\.1)$/.test(h)); } catch (e) {}
  if (!origemOk) return res.status(403).json({ ok: false });
  const tamanho = Number(req.headers['content-length']);
  if (!Number.isFinite(tamanho) || tamanho > 512 || !/^application\/json/i.test(String(req.headers['content-type'] || ''))) return res.status(413).end();

  const b = req.body && typeof req.body === 'object' && !Buffer.isBuffer(req.body) ? req.body : {};
  const slug = typeof b.slug === 'string' ? b.slug : '';
  const tipo = typeof b.tipo === 'string' ? b.tipo : '';
  const anterior = typeof b.anterior === 'string' ? b.anterior : '';
  if (!SLUGS.has(slug) || (tipo && !TIPOS.includes(tipo)) || (anterior && !TIPOS.includes(anterior)) || tipo === anterior) {
    return res.status(400).json({ ok: false });
  }

  const chave = 'reacoes:' + slug;
  const rl = 'reacoes-rl:' + crypto.createHash('sha256').update(ipDoCliente(req) + '|hypeapp-reacoes').digest('hex').slice(0, 32);
  try {
    const [n] = await redis([['INCR', rl], ['EXPIRE', rl, '60', 'NX']]);
    if (n > LIMITE_MIN) return res.status(429).json({ ok: false });
    const cmds = [];
    if (anterior) cmds.push(['HINCRBY', chave, anterior, '-1']);
    if (tipo) cmds.push(['HINCRBY', chave, tipo, '1']);
    cmds.push(['HGETALL', chave]);
    const out = await redis(cmds);
    const c = contagem(out[out.length - 1]);
    // contagem nunca fica negativa (ex.: navegador com memória antiga depois de uma limpeza)
    if (anterior && (parseInt(out[0], 10) || 0) < 0) { await redis([['HSET', chave, anterior, '0']]); c[anterior] = 0; }
    return res.status(200).json({ ok: true, contagem: c });
  } catch (e) {
    console.error('[reacoes] gravação falhou:', e && e.name === 'AbortError' ? 'timeout' : (e && e.message) || 'erro');
    return res.status(503).json({ ok: false });
  }
};
