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
const esc = (s) => String(s || '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
const emailValido = (e) => /^[^\s@<>"',;:]+@[^\s@<>"',;:]+\.[^\s@<>"',;:]+$/.test(e) && e.length <= 200;
const b64 = (s) => Buffer.from(s, 'utf8').toString('base64');
const enc = (s) => `=?UTF-8?B?${b64(s)}?=`;

// ---------- conteúdo de cada situação ----------
const SEGURANCA = 'O HypeApp nunca pede senha, código de verificação ou chave PIX por mensagem.';
const PRAZO_SUP = 'A primeira resposta chega em até 2 dias úteis, de segunda a sexta, das 10h às 18h, no e-mail que você informou.';

// Suporte: o que dizer e que dicas dar em cada assunto, para creators (app) e para marcas (painel).
const SUP = {
  conta: {
    app: { titulo: 'Vamos resolver o seu acesso', dicas: [
      'Confira se o app está atualizado na App Store ou no Google Play.',
      'Entre com o mesmo e-mail e a mesma senha do cadastro.',
      'Esqueceu a senha? Use "Esqueci a senha" na tela de entrada do app.'] },
    painel: { titulo: 'Vamos resolver o seu acesso ao painel', dicas: [
      'O painel funciona no navegador, em www.hypeapp.com.br/backoffice/sign-in.',
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
      'Se mudar de ideia, escreva para o suporte pelo e-mail informado logo abaixo.'] },
    painel: { titulo: 'Recebemos o seu pedido de exclusão', dicas: [
      'Veja o que acontece com campanhas, saldo e dados na página Exclusão de conta.',
      'Se mudar de ideia, escreva para o suporte pelo e-mail informado logo abaixo.'] },
    link: ['Exclusão de conta', '/exclusao-de-conta/'],
  },
  outro: {
    app: { titulo: 'Recebemos o seu chamado', dicas: ['Muitas dúvidas já têm resposta nas perguntas frequentes.'] },
    painel: { titulo: 'Recebemos o seu chamado', dicas: ['Muitas dúvidas de marcas já têm resposta nas perguntas frequentes.'] },
  },
};

function situacao(tipo, d, rot) {
  const nome = limpa(d.nome).split(' ')[0] || '';
  const ola = nome ? `Olá, ${nome}!` : 'Olá!';
  const r = (campo, v) => (rot[campo] && rot[campo][v]) || '';
  if (tipo === 'suporte') {
    const ass = SUP[d.assunto] ? d.assunto : 'outro';
    const quem = d.uso === 'painel' ? 'painel' : 'app';
    const s = SUP[ass][quem];
    const resumo = [['Assunto', r('assunto', d.assunto)], ['Você usa', quem === 'painel' ? 'O painel (marca ou agência)' : 'O app (creator)']];
    if (ass === 'campanha') resumo.push(['Campanha', limpa(d.campanha_nome, 80)], ['Etapa', r('etapa', d.etapa)]);
    if (ass === 'redes') resumo.push(['Rede', r('rede', d.rede)], ['Perfil', limpa(d.arroba, 60)]);
    if (ass === 'erro') resumo.push(['Aparelho', limpa(d.aparelho, 60)], ['Versão do app', limpa(d.versao, 20)]);
    const link = SUP[ass].link || (quem === 'painel' ? ['Dúvidas de marcas', '/perguntas-frequentes/#marcas'] : ['Perguntas frequentes', '/perguntas-frequentes/#creators']);
    return {
      chave: `suporte-${quem}-${ass}`,
      assunto: `${s.titulo} · HypeApp`,
      tag: quem === 'painel' ? 'Suporte · Marcas e agências' : 'Suporte · Creators',
      ola, titulo: s.titulo,
      texto: [`Recebemos o seu chamado e ele já está com a nossa equipe de suporte. ${PRAZO_SUP}`],
      resumo: resumo.filter(([, v]) => v),
      dicasTitulo: 'Enquanto isso',
      dicas: s.dicas, alerta: s.alerta || '',
      botao: link,
      fecho: `Precisa complementar? Escreva para ${CONTATO} citando este chamado.`,
    };
  }
  const agencia = d.agencia === 'sim';
  const empresa = limpa(d.empresa, 120);
  const resumo = [['Empresa', empresa], ['Segmento', r('segmento', d.segmento)], ['Objetivo', r('objetivo', d.objetivo)], ['Para quando', r('inicio', d.inicio)]];
  return {
    chave: agencia ? 'lead-agencia' : 'lead-marca',
    assunto: agencia ? 'Recebemos o contato da sua agência · HypeApp' : 'Recebemos o seu contato · HypeApp',
    tag: agencia ? 'Comercial · Agências' : 'Comercial · Marcas',
    ola,
    titulo: agencia ? 'Vamos conversar sobre as marcas que você atende' : `Vamos conversar sobre a ${empresa || 'sua marca'}`,
    texto: [
      `Recebemos as suas respostas no formulário "Fale com nosso time". O nosso time comercial retorna em até 2 dias úteis, pelo e-mail ou WhatsApp que você informou.`,
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
    fecho: `Quer adiantar alguma informação? Escreva para ${CONTATO}.`,
  };
}

// ---------- HTML (tabelas e estilos inline, para funcionar nos leitores de e-mail) ----------
function html(s, base) {
  const p = (t) => `<p style="margin:0 0 14px;font-size:16px;line-height:1.55;color:${C.preto}">${esc(t)}</p>`;
  const resumo = s.resumo.length ? `
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:${C.fundo};border-radius:14px;margin:6px 0 22px">
      <tr><td style="padding:16px 18px">
        <div style="font-size:12px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:${C.cinza};margin-bottom:8px">Você nos contou</div>
        ${s.resumo.map(([k, v]) => `<div style="font-size:14px;line-height:1.6;color:${C.preto}"><span style="color:${C.cinza}">${esc(k)}:</span> <b>${esc(v)}</b></div>`).join('')}
      </td></tr></table>` : '';
  const dicas = s.dicas.map((t) => `
      <tr><td valign="top" width="26" style="padding:0 0 10px"><div style="width:18px;height:18px;border-radius:9px;background:${C.roxo};color:#fff;font-size:12px;line-height:18px;text-align:center;font-weight:700">&#10003;</div></td>
          <td style="padding:0 0 10px;font-size:15px;line-height:1.5;color:${C.preto}">${esc(t)}</td></tr>`).join('');
  const alerta = s.alerta ? `<div style="margin:4px 0 18px;padding:12px 14px;border-radius:12px;background:#FFF6CC;font-size:14px;line-height:1.5;color:${C.preto}"><b>Atenção:</b> ${esc(s.alerta)}</div>` : '';
  return `<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="color-scheme" content="light"><title>${esc(s.assunto)}</title></head>
<body style="margin:0;padding:0;background:${C.fundo};font-family:Inter,Helvetica,Arial,sans-serif">
<div style="display:none;max-height:0;overflow:hidden;opacity:0">${esc(s.texto[0])}</div>
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:${C.fundo}"><tr><td align="center" style="padding:24px 12px">
  <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="max-width:600px">
    <tr><td style="background:${C.preto};border-radius:24px 24px 0 0;padding:26px 28px">
      <img src="${base}/assets/email/logo-branco.png" width="81" height="44" alt="HypeApp" style="display:block;border:0;height:44px;width:auto">
    </td></tr>
    <tr><td style="background:${C.roxo};height:6px;line-height:6px;font-size:0">&nbsp;</td></tr>
    <tr><td style="background:#ffffff;padding:30px 28px 10px;border-radius:0 0 24px 24px">
      <div style="display:inline-block;font-size:12px;font-weight:700;color:${C.roxoTx};background:${C.lilas};border-radius:999px;padding:6px 12px;margin-bottom:16px">${esc(s.tag)}</div>
      <h1 style="margin:0 0 16px;font-size:26px;line-height:1.15;letter-spacing:-.02em;color:${C.preto}">${esc(s.titulo)}</h1>
      ${p(s.ola)}
      ${s.texto.map(p).join('')}
      ${resumo}
      <div style="font-size:17px;font-weight:700;color:${C.preto};margin:0 0 12px">${esc(s.dicasTitulo)}</div>
      <table role="presentation" cellpadding="0" cellspacing="0" style="margin:0 0 8px">${dicas}</table>
      ${alerta}
      <table role="presentation" cellpadding="0" cellspacing="0" style="margin:8px 0 24px"><tr><td style="border-radius:999px;background:${C.preto}">
        <a href="${base}${s.botao[1]}" style="display:inline-block;padding:14px 24px;font-size:15px;font-weight:700;color:#ffffff;text-decoration:none;border-radius:999px">${esc(s.botao[0])} &rarr;</a>
      </td></tr></table>
      <p style="margin:0 0 22px;font-size:14px;line-height:1.55;color:${C.cinza}">${esc(s.fecho)}</p>
    </td></tr>
    <tr><td style="padding:22px 28px 8px;font-size:12px;line-height:1.6;color:${C.cinza}">
      <b style="color:${C.preto}">${esc(SEGURANCA)}</b><br>
      Este é um e-mail automático, enviado porque você preencheu um formulário em hypeapp.com.br. Respostas a este endereço não são lidas.<br>
      Você no Hype Marketing e Entretenimento LTDA · CNPJ 43.442.408/0001-26 · ${esc(CONTATO)} · ${esc(FONE)}<br>
      <a href="${base}/privacidade/" style="color:${C.cinza}">Política de Privacidade</a>
    </td></tr>
  </table>
</td></tr></table></body></html>`;
}

function texto(s, base) {
  const linhas = [s.ola, '', s.titulo, '', ...s.texto.flatMap((t) => [t, ''])];
  if (s.resumo.length) linhas.push('Você nos contou:', ...s.resumo.map(([k, v]) => `- ${k}: ${v}`), '');
  linhas.push(`${s.dicasTitulo}:`, ...s.dicas.map((t) => `- ${t}`), '');
  if (s.alerta) linhas.push(`Atenção: ${s.alerta}`, '');
  linhas.push(`${s.botao[0]}: ${base}${s.botao[1]}`, '', s.fecho, '', '--', SEGURANCA,
    'Este é um e-mail automático, enviado porque você preencheu um formulário em hypeapp.com.br. Respostas a este endereço não são lidas.',
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
  const { s, html: h, texto: t } = monta(tipo, d, rot, base);
  const fronteira = `hh-${Date.now().toString(36)}-${Math.random().toString(36).slice(2)}`;
  const msg = [
    `From: HypeApp <${from}>`,
    `To: <${to}>`,
    `Subject: ${enc(s.assunto)}`,
    `Date: ${new Date().toUTCString()}`,
    `Message-ID: <${Date.now().toString(36)}.${Math.random().toString(36).slice(2)}@hypeapp.com.br>`,
    'MIME-Version: 1.0',
    'Auto-Submitted: auto-generated',
    `Content-Type: multipart/alternative; boundary="${fronteira}"`,
    '',
    `--${fronteira}`,
    'Content-Type: text/plain; charset=UTF-8',
    'Content-Transfer-Encoding: base64',
    '',
    linhas76(t),
    `--${fronteira}`,
    'Content-Type: text/html; charset=UTF-8',
    'Content-Transfer-Encoding: base64',
    '',
    linhas76(h),
    `--${fronteira}--`,
  ].join('\r\n');
  try {
    await smtp({ host: process.env.SMTP_HOST || 'smtp.purelymail.com', port: +(process.env.SMTP_PORT || 465), user, pass, from, to, msg });
    return true;
  } catch (e) {
    console.error(`[email] confirmação não enviada (${s.chave}): ${e.message}`);
    return false;
  }
}

module.exports = { confirma, monta, situacao, SUP };
