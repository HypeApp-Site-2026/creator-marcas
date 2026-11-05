// E-mail de confirmação para quem enviou o formulário (04/11), pelo SMTP do Purelymail que o backoffice já usa.
// Sem pacotes: SMTP com TLS direto na porta 465 (módulo tls do Node).
//
// Variáveis de ambiente (somente servidor; Vercel → Settings → Environment Variables):
//   SMTP_USER   login do SMTP (obrigatória)
//   SMTP_PASS   senha do SMTP (obrigatória)
//   SMTP_HOST   opcional, padrão smtp.purelymail.com
//   SMTP_PORT   opcional, padrão 465
//   SMTP_FROM   opcional, padrão noreply@hypeapp.com.br
// Sem SMTP_USER ou SMTP_PASS, não envia nada (o formulário segue funcionando).
//
// Regras: o login e a senha nunca vão para respostas ou logs; o log não leva o e-mail nem o nome da pessoa;
// uma falha no e-mail nunca derruba o envio do formulário (o lead já foi gravado no CRM).

const tls = require('tls');

const TIMEOUT_MS = 6000;
const SITE = 'https://www.hypeapp.com.br';

const limpa = (s, max = 120) => String(s || '').replace(/[\r\n\t]+/g, ' ').replace(/[<>]/g, '').trim().slice(0, max);
const emailValido = (e) => /^[^\s@<>"',;:]+@[^\s@<>"',;:]+\.[^\s@<>"',;:]+$/.test(e) && e.length <= 200;
const b64 = (s) => Buffer.from(s, 'utf8').toString('base64');
const assunto = (s) => `=?UTF-8?B?${b64(s)}?=`;

function textos(tipo, d, rotulos) {
  const nome = limpa(d.nome).split(' ')[0] || '';
  const ola = nome ? `Olá, ${nome}!` : 'Olá!';
  const rodape = [
    '',
    'Este é um e-mail automático, enviado porque você preencheu um formulário em hypeapp.com.br. Não é preciso responder.',
    'O HypeApp nunca pede senha, código de verificação ou chave PIX por mensagem.',
    '',
    'HypeApp · Você no Hype',
    SITE,
  ];
  if (tipo === 'suporte') {
    const ass = rotulos.assunto && rotulos.assunto[d.assunto];
    return {
      assunto: 'Recebemos seu chamado · HypeApp',
      corpo: [ola, '',
        `Recebemos o seu chamado${ass ? ` sobre "${ass}"` : ''}. O suporte responde pelo e-mail que você informou, de segunda a sexta, das 10h às 18h.`,
        '',
        `Enquanto isso, muitas dúvidas já têm resposta nas perguntas frequentes: ${SITE}/perguntas-frequentes/`,
        ...rodape].join('\r\n'),
    };
  }
  const empresa = limpa(d.empresa, 120);
  return {
    assunto: 'Recebemos seu pedido · HypeApp',
    corpo: [ola, '',
      `Recebemos o seu pedido pelo formulário "Fale com nosso time"${empresa ? `, com as informações da ${empresa}` : ''}. Nosso time comercial vai analisar e entrar em contato pelo e-mail ou WhatsApp que você informou.`,
      '',
      `Enquanto isso, veja como funciona o painel das marcas: ${SITE}/marcas/`,
      ...rodape].join('\r\n'),
  };
}

// Conversa SMTP mínima: lê a resposta (inclusive multilinha) e confere o código esperado.
function smtp({ host, port, user, pass, from, to, msg }) {
  return new Promise((resolve, reject) => {
    let buf = '', etapa = 0, feito = false;
    const fim = (err) => { if (feito) return; feito = true; clearTimeout(t); try { sock.end(); } catch (e) {} err ? reject(err) : resolve(); };
    const t = setTimeout(() => fim(new Error('tempo esgotado')), TIMEOUT_MS);
    const sock = tls.connect({ host, port, servername: host }, () => {});
    sock.setEncoding('utf8');
    const passos = [
      [220, () => `EHLO hypeapp.com.br`],
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
        if (/^\d{3}-/.test(linha)) continue;           // resposta multilinha: espera a última
        const cod = +linha.slice(0, 3);
        if (etapa >= passos.length) return fim();
        const [espera, prox] = passos[etapa];
        if (cod !== espera) return fim(new Error(`SMTP respondeu ${cod} na etapa ${etapa + 1}`));
        etapa++;
        sock.write(prox() + '\r\n');
        if (etapa === passos.length) return fim();     // QUIT enviado: mensagem aceita
      }
    });
    sock.on('error', (e) => fim(new Error(`conexão: ${e.code || 'erro'}`)));
    sock.on('end', () => fim(etapa >= passos.length ? null : new Error('conexão encerrada')));
  });
}

async function confirma(tipo, d, rotulos = {}) {
  const user = process.env.SMTP_USER, pass = process.env.SMTP_PASS;
  if (!user || !pass) return false;
  const to = String(d.email || '').trim();
  if (!emailValido(to)) return false;
  const from = process.env.SMTP_FROM || 'noreply@hypeapp.com.br';
  const { assunto: a, corpo } = textos(tipo, d, rotulos);
  const id = `<${Date.now().toString(36)}.${Math.random().toString(36).slice(2)}@hypeapp.com.br>`;
  const msg = [
    `From: HypeApp <${from}>`,
    `To: <${to}>`,
    `Subject: ${assunto(a)}`,
    `Date: ${new Date().toUTCString()}`,
    `Message-ID: ${id}`,
    'MIME-Version: 1.0',
    'Content-Type: text/plain; charset=UTF-8',
    'Content-Transfer-Encoding: base64',
    'Auto-Submitted: auto-generated',
    '',
    b64(corpo).replace(/.{76}/g, '$&\r\n'),
  ].join('\r\n');
  try {
    await smtp({ host: process.env.SMTP_HOST || 'smtp.purelymail.com', port: +(process.env.SMTP_PORT || 465), user, pass, from, to, msg });
    return true;
  } catch (e) {
    console.error(`[email] confirmação não enviada (${tipo}): ${e.message}`);
    return false;
  }
}

module.exports = { confirma, textos };
