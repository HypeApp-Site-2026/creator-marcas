// E-mails de confirmação para quem enviou um formulário do site (04/11, personalizados em 05/11).
// Enviados pelo SMTP do Purelymail que o backoffice já usa, sem pacotes (TLS direto na porta 465, módulo tls do Node).
//
// Situações (cada uma com assunto, texto, dicas e botão próprios):
//   comercial: marca | agência                       (formulário "Fale com nosso time")
//   suporte:   creator (app) | marca ou agência (painel) × assunto:
//              conta, redes, campanha, pagamento, erro, denuncia, exclusao, outro
// Cada e-mail vai em HTML (com o logo e as cores do HypeApp) e em texto puro, para leitores sem HTML.
// Só fatos já publicados no site (prazos, regras do PIX, horário do suporte); nenhum prazo novo.
//
// Variáveis de ambiente (somente servidor; Vercel → Settings → Environment Variables):
//   SMTP_USER, SMTP_PASS   obrigatórias (sem elas nada é enviado)
//   SMTP_HOST              opcional, padrão smtp.purelymail.com
//   SMTP_PORT              opcional, padrão 465
//   SMTP_FROM              opcional, padrão noreply@hypeapp.com.br
// Regras: login e senha nunca vão para respostas ou logs; o log não leva nome nem e-mail da pessoa;
// uma falha no e-mail nunca derruba o envio do formulário (o lead já foi gravado no CRM).

const tls = require('tls');

const TIMEOUT_MS = 6000;
const CONTATO = 'contato@vocenohype.com.br';
const FONE = '(11) 3834-5221';
const C = { roxo: '#9E2CFA', roxoTx: '#7A12D6', lilas: '#F1EAFB', preto: '#050505', cinza: '#555555', fundo: '#EFEFEF', lima: '#D2F51A' };

const limpa = (s, max = 120) => String(s || '').replace(/[\r\n\t]+/g, ' ').replace(/[<>]/g, '').trim().slice(0, max);
const esc = (s) => String(s || '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;').replace(/'/g, '&#39;');
const emailValido = (e) => /^[^\s@<>"',;:]+@[^\s@<>"',;:]+\.[^\s@<>"',;:]+$/.test(e) && e.length <= 200;
const b64 = (s) => Buffer.from(s, 'utf8').toString('base64');
const enc = (s) => `=?UTF-8?B?${b64(s)}?=`;

// ---------- conteúdo de cada situação ----------
const SEGURANCA = 'O HypeApp nunca pede senha, código de verificação ou chave PIX por mensagem.';
const PRAZO_SUP = 'A primeira resposta chega em até 2 dias úteis, de segunda a sexta, das 10h às 18h.';

// Suporte: o que dizer e que dicas dar em cada assunto, para creators (app) e para marcas (painel).
// Imagem do topo de cada situação (site: /assets/email/*.jpg, 960 x 640, até ~70 KB)
const IMG = {
  app: { conta: 'creator-conta', redes: 'creator-redes', campanha: 'creator-campanha', pagamento: 'creator-pagamento',
         erro: 'creator-erro', denuncia: 'fantasma', exclusao: 'creator-comunidade', outro: 'creator-comunidade' },
  painel: { conta: 'marca-painel', redes: 'marca-resultados', campanha: 'marca-campanha', pagamento: 'marca-resultados',
            erro: 'marca-painel', denuncia: 'fantasma', exclusao: 'marca-painel', outro: 'lead-marca' },
};

const SUP = {
  conta: {
    app: { titulo: 'Vamos resolver o seu acesso', dicas: [
      'Confira se o app está atualizado na App Store ou no Google Play.',
      'Entre com o mesmo e-mail e a mesma senha do cadastro.',
      'Esqueceu a senha? Use "Esqueci a senha" na tela de entrada do app.'] },
    painel: { titulo: 'Vamos resolver o seu acesso ao painel', dicas: [
      'O painel funciona no navegador, em www.hypeapp.com.br/backoffice/.',
      'O acesso de marcas e agências é liberado pelo comercial depois do primeiro contato.',
      'Use o e-mail cadastrado pela sua empresa no painel.'] },
  },
  redes: {
    app: { titulo: 'Vamos ver a conexão da sua rede', dicas: [
      'Confira se o @ informado é o mesmo do perfil que você quer conectar.',
      'Se você informou a mensagem de erro, ela ajuda a equipe a entender o caso mais rápido.'] },
    painel: { titulo: 'Vamos ver a rede social informada', dicas: [
      'Confira se o @ informado está escrito como aparece na rede.'] },
  },
  campanha: {
    app: { titulo: 'Recebemos sua dúvida sobre a campanha', dicas: [
      'No app, cada campanha mostra o próximo passo e o prazo de cada entrega.',
      'Roteiros e conteúdos passam pela aprovação da marca, que aprova ou pede ajuste.'] },
    painel: { titulo: 'Recebemos sua dúvida sobre a campanha', dicas: [
      'No painel, a aba Gerenciamento da campanha reúne roteiros e conteúdos para aprovar.',
      'Em "Precisa da sua ação" ficam as inscrições e tudo o que aguarda a sua decisão.'] },
  },
  pagamento: {
    app: { titulo: 'Recebemos sua dúvida sobre pagamento', dicas: [
      'O valor entra na carteira como "A liberar" e fica disponível 30 dias depois do encerramento da campanha.',
      'O saque via PIX é processado em até 2 horas úteis, sem taxa, a partir de R$ 1,00.',
      'A chave PIX precisa estar no seu nome, com o mesmo CPF da conta.'],
      alerta: 'Nunca envie sua chave PIX ou dados bancários por e-mail ou mensagem.' },
    painel: { titulo: 'Recebemos sua dúvida sobre pagamentos', dicas: [
      'No Financeiro do painel ficam o saldo disponível, o valor reservado, os depósitos e os pagamentos aos creators.',
      'Se um creator não entregar, o valor reservado para aquela participação volta ao saldo da campanha.'] },
  },
  erro: {
    app: { titulo: 'Recebemos o seu relato de erro', dicas: [
      'Atualize o app pela loja: muitas falhas já foram corrigidas nas versões novas.',
      'O aparelho, a versão e os passos que você informou ajudam a equipe a reproduzir o erro.'] },
    painel: { titulo: 'Recebemos o seu relato de erro', dicas: [
      'Recarregue a página e tente de novo em outra aba ou navegador.',
      'Os passos que você descreveu ajudam a equipe a reproduzir o erro.'] },
  },
  denuncia: {
    app: { titulo: 'Recebemos a sua denúncia', dicas: [
      'A comunidade do HypeApp tem tolerância zero a conteúdo censurável e comportamento abusivo.',
      'No app, você também pode denunciar qualquer publicação, comentário ou mensagem e bloquear outro usuário.'] },
    painel: { titulo: 'Recebemos a sua denúncia', dicas: [
      'As denúncias são tratadas conforme as Regras da comunidade do HypeApp.'] },
    link: ['Regras da comunidade', '/regras-da-comunidade/'],
  },
  exclusao: {
    app: { titulo: 'Recebemos o seu pedido de exclusão', dicas: [
      'Veja o que acontece com campanhas em andamento, saldo e dados na página Exclusão de conta.',
      'Se mudar de ideia, abra um novo chamado em hypeapp.com.br/suporte.'] },
    painel: { titulo: 'Recebemos o seu pedido de exclusão', dicas: [
      'Veja o que acontece com campanhas, saldo e dados na página Exclusão de conta.',
      'Se mudar de ideia, abra um novo chamado em hypeapp.com.br/suporte.'] },
    link: ['Exclusão de conta', '/exclusao-de-conta/'],
  },
  outro: {
    app: { titulo: 'Recebemos o seu chamado', dicas: ['Muitas dúvidas já têm resposta nas perguntas frequentes.'] },
    painel: { titulo: 'Recebemos o seu chamado', dicas: ['Muitas dúvidas de marcas já têm resposta nas perguntas frequentes.'] },
  },
};

function situacao(tipo, d, rot) {
  const n0 = limpa(d.nome).split(' ')[0] || '';
  const nome = n0 ? n0.charAt(0).toLocaleUpperCase('pt-BR') + n0.slice(1).toLocaleLowerCase('pt-BR') : '';
  const ola = nome ? `Olá, ${nome}!` : 'Olá!';
  const r = (campo, v) => (rot[campo] && rot[campo][v]) || '';
  if (tipo === 'suporte') {
    const ass = SUP[d.assunto] ? d.assunto : 'outro';
    const quem = d.uso === 'painel' ? 'painel' : 'app';
    const s = SUP[ass][quem];
    const pedido = d.pedido != null && /^\d{1,12}$/.test(String(d.pedido)) ? `#${d.pedido}` : '';
    const resumo = [['Pedido', pedido], ['Assunto', r('assunto', d.assunto)], ['Você usa', quem === 'painel' ? 'O painel (marca ou agência)' : 'O app (creator)']];
    if (ass === 'campanha') resumo.push(['Campanha', limpa(d.campanha_nome, 80)], ['Etapa', r('etapa', d.etapa)]);
    if (ass === 'redes') resumo.push(['Rede', r('rede', d.rede)], ['Perfil', limpa(d.arroba, 60)]);
    if (ass === 'erro') resumo.push(['Aparelho', limpa(d.aparelho, 60)], ['Versão do app', limpa(d.versao, 20)]);
    const link = SUP[ass].link || (quem === 'painel' ? ['Dúvidas de marcas', '/perguntas-frequentes/#marcas'] : ['Perguntas frequentes', '/perguntas-frequentes/#creators']);
    return {
      chave: `suporte-${quem}-${ass}`,
      img: IMG[quem][ass],
      assunto: pedido ? `Pedido ${pedido} · ${s.titulo} · HypeApp` : `${s.titulo} · HypeApp`,
      tag: quem === 'painel' ? 'Suporte · Marcas e agências' : 'Suporte · Creators',
      ola, titulo: s.titulo,
      texto: [`Recebemos o seu chamado${pedido ? ` (pedido ${pedido})` : ''} e ele já está com a nossa equipe de suporte. ${PRAZO_SUP}`],
      resumo: resumo.filter(([, v]) => v),
      dicasTitulo: 'Enquanto isso',
      dicas: s.dicas, alerta: s.alerta || '',
      botao: link,
      fecho: 'Não responda a este e-mail. Para complementar, abra um novo chamado em hypeapp.com.br/suporte.',
    };
  }
  const agencia = d.agencia === 'sim';
  const empresa = limpa(d.empresa, 120);
  const resumo = [['Empresa', empresa], ['Segmento', r('segmento', d.segmento)], ['Objetivo', r('objetivo', d.objetivo)], ['Para quando', r('inicio', d.inicio)]];
  return {
    chave: agencia ? 'lead-agencia' : 'lead-marca',
    img: agencia ? 'lead-agencia' : 'lead-marca',
    assunto: agencia ? 'Recebemos o contato da sua agência · HypeApp' : 'Recebemos o seu contato · HypeApp',
    tag: agencia ? 'Comercial · Agências' : 'Comercial · Marcas',
    ola,
    titulo: agencia ? 'Vamos conversar sobre as marcas que você atende' : 'Vamos conversar sobre a sua marca',
    texto: [
      `Recebemos as suas respostas no formulário "Fale com nosso time". O nosso time comercial retorna em até 2 dias úteis, pelo WhatsApp que você informou.`,
      agencia
        ? 'No HypeApp, cada cliente da agência tem um espaço próprio no painel, com a sua equipe cuidando das campanhas de cada marca.'
        : 'Você pode operar as campanhas pelo painel, no self-service, ou deixar a operação com a Você no Hype, na campanha gerenciada.',
    ],
    resumo: resumo.filter(([, v]) => v),
    dicasTitulo: 'Na conversa com o comercial',
    dicas: [
      'Entendemos os seus objetivos, o público e os formatos de conteúdo.',
      'Apresentamos as duas formas de trabalhar e as condições de acesso ao painel.',
      'Os valores são sob consulta e dependem do escopo, do volume e da forma de trabalho.'],
    alerta: '',
    botao: agencia ? ['Ver o painel para agências', '/marcas/#agencias'] : ['Conhecer o painel das marcas', '/marcas/'],
    fecho: 'Não responda a este e-mail. O nosso time entra em contato com você pelo WhatsApp informado.',
  };
}

// ---------- HTML leve (05/11): uma imagem, texto curto, até 3 dicas e um botão; tabelas e estilos inline ----------
// Menos blocos e menos imagens ajudam a não cair no spam; a versão em texto puro vai junto.
function html(s, base, src = (n, e) => `${base}/assets/email/${n}.${e}`) {
  const p = (t) => `<p style="margin:0 0 14px;font-size:16px;line-height:1.55;color:${C.preto}">${esc(t)}</p>`;
  const dicas = s.dicas.slice(0, 3).map((t) => `<li style="margin:0 0 8px">${esc(t)}</li>`).join('');
  const alerta = s.alerta ? `<p style="margin:0 0 18px;font-size:14px;line-height:1.5;color:${C.preto}"><b>Atenção:</b> ${esc(s.alerta)}</p>` : '';
  return `<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="color-scheme" content="light"><title>${esc(s.assunto)}</title></head>
<body style="margin:0;padding:0;background:#ffffff;font-family:Inter,Helvetica,Arial,sans-serif">
<div style="display:none;max-height:0;overflow:hidden;opacity:0">${esc(s.texto[0])}</div>
<table role="presentation" width="100%" cellpadding="0" cellspacing="0"><tr><td align="center" style="padding:16px 12px">
  <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="max-width:600px">
    <tr><td bgcolor="${C.preto}" style="background:${C.preto};padding:20px 24px;border-radius:20px">
      <img src="${src('logo-hypeapp', 'jpg')}" width="66" height="36" alt="HypeApp" style="display:block;border:0;width:66px;height:36px">
    </td></tr>
    <tr><td style="height:12px;line-height:12px;font-size:0">&nbsp;</td></tr>
    <tr><td style="padding:0;line-height:0">
      <img src="${src(s.img, 'jpg')}" width="600" alt="" style="display:block;width:100%;max-width:600px;height:auto;border:0;border-radius:20px">
    </td></tr>
    <tr><td style="padding:26px 8px 8px">
      <div style="font-size:12px;font-weight:700;color:${C.roxoTx};margin-bottom:10px">${esc(s.tag)}</div>
      <h1 style="margin:0 0 16px;font-size:26px;line-height:1.15;letter-spacing:-.02em;color:${C.preto}">${esc(s.titulo)}</h1>
      ${p(s.ola)}
      ${s.texto.map(p).join('')}
      <div style="font-size:16px;font-weight:700;color:${C.preto};margin:6px 0 8px">${esc(s.dicasTitulo)}</div>
      <ul style="margin:0 0 16px;padding-left:20px;font-size:15px;line-height:1.5;color:${C.preto}">${dicas}</ul>
      ${alerta}
      <table role="presentation" cellpadding="0" cellspacing="0" style="margin:6px 0 22px"><tr><td style="border-radius:999px;background:${C.roxo}">
        <a href="${base}${s.botao[1]}" style="display:inline-block;padding:13px 24px;font-size:15px;font-weight:700;color:#ffffff;text-decoration:none;border-radius:999px">${esc(s.botao[0])}</a>
      </td></tr></table>
      <p style="margin:0 0 24px;font-size:14px;line-height:1.55;color:${C.cinza}">${esc(s.fecho)}</p>
    </td></tr>
    <tr><td style="background:${C.preto};padding:22px 24px;border-radius:20px;font-size:12px;line-height:1.6;color:#BDBDBD">
      ${esc(SEGURANCA)}<br>
      <b style="color:#ffffff">Não responda a este e-mail.</b> Ele é automático e as respostas não são lidas.<br>Você recebeu porque preencheu um formulário em hypeapp.com.br.<br>
      Você no Hype · CNPJ 43.442.408/0001-26 · ${esc(CONTATO)} · <a href="${base}/privacidade/" style="color:#BDBDBD">Privacidade</a>
    </td></tr>
  </table>
</td></tr></table></body></html>`;
}

function texto(s, base) {
  const linhas = [s.ola, '', s.titulo, '', ...s.texto.flatMap((t) => [t, ''])];
  linhas.push(`${s.dicasTitulo}:`, ...s.dicas.slice(0, 3).map((t) => `- ${t}`), '');
  if (s.alerta) linhas.push(`Atenção: ${s.alerta}`, '');
  linhas.push(`${s.botao[0]}: ${base}${s.botao[1]}`, '', s.fecho, '', '--', SEGURANCA,
    'Não responda a este e-mail. Ele é automático e as respostas não são lidas. Você recebeu porque preencheu um formulário em hypeapp.com.br.',
    `Você no Hype · ${CONTATO} · ${FONE}`);
  return linhas.join('\r\n');
}

// ---------- SMTP mínimo ----------
function smtp({ host, port, user, pass, from, to, msg }) {
  return new Promise((resolve, reject) => {
    let buf = '', etapa = 0, feito = false;
    const fim = (err) => { if (feito) return; feito = true; clearTimeout(t); try { sock.end(); } catch (e) {} err ? reject(err) : resolve(); };
    const t = setTimeout(() => fim(new Error('tempo esgotado')), TIMEOUT_MS);
    const sock = tls.connect({ host, port, servername: host }, () => {});
    sock.setEncoding('utf8');
    const passos = [
      [220, () => 'EHLO hypeapp.com.br'],
      [250, () => `AUTH PLAIN ${Buffer.from(`\0${user}\0${pass}`, 'utf8').toString('base64')}`],
      [235, () => `MAIL FROM:<${from}>`],
      [250, () => `RCPT TO:<${to}>`],
      [250, () => 'DATA'],
      [354, () => msg.replace(/\r?\n/g, '\r\n').replace(/^\./gm, '..') + '\r\n.'],
      [250, () => 'QUIT'],
    ];
    sock.on('data', (chunk) => {
      buf += chunk;
      let i;
      while ((i = buf.indexOf('\r\n')) > -1) {
        const linha = buf.slice(0, i); buf = buf.slice(i + 2);
        if (/^\d{3}-/.test(linha)) continue;
        const cod = +linha.slice(0, 3);
        if (etapa >= passos.length) return fim();
        const [espera, prox] = passos[etapa];
        if (cod !== espera) return fim(new Error(`SMTP respondeu ${cod} na etapa ${etapa + 1}`));
        etapa++;
        sock.write(prox() + '\r\n');
        if (etapa === passos.length) return fim();
      }
    });
    sock.on('error', (e) => fim(new Error(`conexão: ${e.code || 'erro'}`)));
    sock.on('end', () => fim(etapa >= passos.length ? null : new Error('conexão encerrada')));
  });
}

const linhas76 = (s) => b64(s).replace(/.{76}/g, '$&\r\n');

function monta(tipo, d, rot, base) {
  const s = situacao(tipo, d, rot);
  return { s, html: html(s, base), texto: texto(s, base) };
}

// base: endereço do site que recebeu o formulário (teste ou www), para o logo e os links.
async function confirma(tipo, d, rot = {}, base = 'https://www.hypeapp.com.br') {
  const user = process.env.SMTP_USER, pass = process.env.SMTP_PASS;
  if (!user || !pass) return false;
  const to = String(d.email || '').trim();
  if (!emailValido(to)) return false;
  const from = process.env.SMTP_FROM || 'noreply@hypeapp.com.br';
  const s = situacao(tipo, d, rot);
  // imagens dentro do próprio e-mail (cid): não dependem do site estar no ar nem do leitor baixar imagens de fora
  // Imagens (05/11): por padrão vão como link para o site (não aparecem como anexo). O endereço das imagens não depende
  // de quem recebeu o formulário: no teste (Preview) usa teste.hypeapp.com.br; em produção, www.hypeapp.com.br.
  // EMAIL_IMAGENS=anexo volta a mandar as imagens dentro do e-mail (cid), que aparecem mesmo sem baixar imagens de fora.
  const anexo = process.env.EMAIL_IMAGENS === 'anexo';
  const imgBase = process.env.EMAIL_IMG_BASE || (process.env.VERCEL_ENV === 'production' ? 'https://www.hypeapp.com.br' : 'https://teste.hypeapp.com.br');
  const IMGS = anexo ? require('./_imagens') : {};
  const usadas = ['logo-hypeapp', s.img].filter((n) => IMGS[n]);
  const h = html(s, base, (n, e) => (IMGS[n] ? `cid:${n}@hypeapp` : `${imgBase}/assets/email/${n}.${e}`));
  const t = texto(s, base);
  const id = () => `${Date.now().toString(36)}${Math.random().toString(36).slice(2)}`;
  const rel = `hh-rel-${id()}`, alt = `hh-alt-${id()}`;
  const partes = [
    `From: HypeApp <${from}>`,
    `To: <${to}>`,
    `Subject: ${enc(s.assunto)}`,
    `Date: ${new Date().toUTCString()}`,
    `Message-ID: <${id()}@hypeapp.com.br>`,
    'X-Auto-Response-Suppress: All',
    'MIME-Version: 1.0',
    'Auto-Submitted: auto-generated',
    `Content-Type: multipart/related; type="multipart/alternative"; boundary="${rel}"`,
    '',
    `--${rel}`,
    `Content-Type: multipart/alternative; boundary="${alt}"`,
    '',
    `--${alt}`,
    'Content-Type: text/plain; charset=UTF-8',
    'Content-Transfer-Encoding: base64',
    '',
    linhas76(t),
    `--${alt}`,
    'Content-Type: text/html; charset=UTF-8',
    'Content-Transfer-Encoding: base64',
    '',
    linhas76(h),
    `--${alt}--`,
  ];
  for (const n of usadas) {
    partes.push(`--${rel}`, `Content-Type: ${IMGS[n].tipo}; name="${n}.${IMGS[n].ext}"`, 'Content-Transfer-Encoding: base64',
      `Content-ID: <${n}@hypeapp>`, `Content-Disposition: inline; filename="${n}.${IMGS[n].ext}"`, '',
      IMGS[n].b64.replace(/.{76}/g, '$&\r\n'));
  }
  partes.push(`--${rel}--`);
  const msg = partes.join('\r\n');
  try {
    await smtp({ host: process.env.SMTP_HOST || 'smtp.purelymail.com', port: +(process.env.SMTP_PORT || 465), user, pass, from, to, msg });
    return true;
  } catch (e) {
    console.error(`[email] confirmação não enviada (${s.chave}): ${e.message}`);
    return false;
  }
}

module.exports = { confirma, monta, situacao, SUP, smtp, enc, emailValido, C };
