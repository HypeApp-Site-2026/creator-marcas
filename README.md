# Site do HypeApp · www.hypeapp.com.br

Site estático publicado no Vercel. A raiz do repositório é o site pronto. O código que gera o site fica em `fonte/` e não vai ao ar.

## Publicar no Vercel (primeira vez)

1. Vercel → **Add New → Project → Import** este repositório.
2. Em **Framework Preset**, escolha **Other**. Deixe Build Command e Output Directory vazios: o `vercel.json` já define tudo.
3. **Environment Variables** (Production):
   - `PLATAFORMA_WEBHOOK_SECRET` (**obrigatória**): segredo do webhook do CRM Comercial da plataforma Você no Hype. Sem ela, o formulário "Fale com nosso time" não cria leads e o visitante vê "Não foi possível enviar agora".
4. **Deploy**. Confira o endereço `*.vercel.app` antes de ligar o domínio.

## Ligar o domínio

1. No projeto: **Settings → Domains → Add** `www.hypeapp.com.br` e `hypeapp.com.br`. Marque `hypeapp.com.br` para **redirecionar (308) para www**.
2. No provedor do DNS do domínio, crie os registros que o Vercel mostrar:
   - `www` → **CNAME** para o valor que o Vercel indicar, em geral `cname.vercel-dns.com`;
   - `@` (raiz) → **A** para o IP que o Vercel indicar, em geral `76.76.21.21`.
3. Aguarde o certificado HTTPS (alguns minutos, até algumas horas pela propagação do DNS).

Atenção: trocar o DNS tira do ar o site atual de hypeapp.com.br. Antes de trocar, confira se algo mais usa esse domínio:
- e-mail (registros MX), que não deve ser mexido;
- links que as lojas usam;
- `api-v2.hypeapp.com.br`, que é outro subdomínio e não muda.

## Atualizar o site

Na pasta `fonte/site`, rode:

```
python3 ../seo/build.py && python3 build.py --web && python3 make_vercel.py ../..
```

Depois faça commit e push. O Vercel publica sozinho.

## Formulários

### "Fale com nosso time" (marcas e agências) → CRM Comercial

`api/lead.js` recebe o formulário de `/contato/marcas/` e cria um lead no CRM Comercial da plataforma Você no Hype:
- chama `POST https://plataforma.vocenohype.com.br/api/public/leads` só pelo servidor, com o cabeçalho `X-Webhook-Secret`;
- o navegador recebe só "ok" ou uma mensagem genérica de erro.

**Variável obrigatória: `PLATAFORMA_WEBHOOK_SECRET`.** Cadastre em Vercel → projeto `hype-site` → **Settings → Environment Variables**:
- marque como **Sensitive** e o ambiente **Production**;
- depois faça **Redeploy** para valer.

Regras:
- nunca coloque o valor no código, no git, em `.env` commitado ou em mensagens. `.env` e `.env.*` estão no `.gitignore`;
- se a variável faltar, o log da função mostra `[lead] PLATAFORMA_WEBHOOK_SECRET não configurada` e o visitante vê uma mensagem genérica;
- campo escondido anti-robô preenchido: responde "ok" e não chama o webhook;
- sem nome, ou sem e-mail e sem telefone: não chama o webhook;
- timeout de 10 s;
- nunca reenvia sozinho após erro, porque o webhook não deduplica.

Mapeamento:
- **Campos diretos:** nome → `name`, e-mail → `email`, WhatsApp → `phone`, empresa → `company`, cargo → `role`, segmento → `industry`, verba → `monthly_budget`, "para quando precisa começar" → `urgency`, "já trabalha com influenciadores" → `agency_experience`.
- **Em `notes`, no formato "Pergunta: resposta", uma por linha:**
  - o restante das respostas;
  - a fila (prioritária quando é agência, tem verba a partir de R$ 20 mil ou quer começar agora);
  - a página de origem, a primeira página da visita e o referrer;
  - as UTMs, o gclid/fbclid e a data/hora ISO.
- **`source`:**
  - gclid → `google-ads`;
  - fbclid → `meta-ads`;
  - senão `utm_source`;
  - senão `site`.
- **`source_form`:** sempre `Site-HypeApp`.

### Suporte → API de chamados do HypeApp (06/11)

O formulário de `/suporte/` vai para o `api/lead.js`, que abre o chamado em `POST https://api-v2.hypeapp.com.br/api/public/support/tickets` (troque com a variável `SUPPORT_TICKETS_URL`, se precisar). A chamada sai do servidor do Vercel, então a CSP do site não muda.

- **Campos enviados:** `name` (Nome, 2 a 100), `email`, `subject` (assunto + "App (creator)" ou "Painel (marca ou agência)", e o nome da campanha quando houver, até 120), `message` (a descrição, os passos do erro e os detalhes do assunto, até 5000), `category` e `page_url` (a página de onde veio o envio).
- **category por assunto:** Conta e acesso, Excluir minha conta e Redes sociais → `account`; Campanha ou entrega → `campaign`; Pagamento ou saque → `billing`; Erro no app → `bug`; Denúncia e Outro → `other`. Ajuste em `CATEGORIA` no `lead.js`.
- **Armadilha de robôs:** o campo escondido do formulário (`bot-field`) é conferido antes; se vier preenchido, o site responde "ok" e não chama a API. O `website` não é enviado.
- **Sucesso (201):** o visitante vai para `/suporte/enviado/?pedido=1042` e vê "Pedido #1042 enviado". O número também vai no assunto e no corpo do e-mail de confirmação.
- **400:** o site marca os campos recusados (nome, e-mail, assunto ou descrição). **429:** "Muitos envios em pouco tempo".
- **Limite por IP:** como a chamada sai do servidor, todos os envios chegam à API com IPs do Vercel. O `lead.js` manda o IP do visitante em `X-Forwarded-For`; a API precisa usar esse cabeçalho no limite de 5 por minuto (vindo só do Vercel), senão o limite vale para o site inteiro.
- **API fora do ar (5xx, erro de rede ou 10 s sem resposta):** o chamado vai para o CRM Comercial pelo webhook antigo, com um aviso no começo das notas, para não se perder. Nesse caso não há número de pedido.
- **Envios pelo teste.hypeapp.com.br** chegam com `[TESTE]` no assunto e o aviso "AMBIENTE DE TESTE" no começo da mensagem.

O Resend não é mais usado: `api/contato.js` foi removido e a variável `RESEND_API_KEY` pode ser apagada do Vercel.

## SEO, IAs e buscadores

Gerados a cada `build.py --web`:
- **`sitemap.xml`:** com `<lastmod>`. A data muda só quando o conteúdo da página muda, conforme o registro em `fonte/site/datas.json`.
- **`llms.txt` e `llms-full.txt`:** o texto completo das páginas públicas, sem as telas de demonstração.
- **`/.well-known/security.txt`:** contato para avisos de segurança. Vale por um ano a partir de cada publicação.
- **Dados estruturados (JSON-LD):**
  - Organization com razão social, CNPJ, endereço e contatos;
  - WebSite;
  - MobileApplication com os links das lojas;
  - Service (self-service e gerenciada) em /marcas/;
  - FAQPage em /perguntas-frequentes/;
  - datePublished e dateModified em todas as páginas. Nos documentos legais vale a data escrita no próprio texto.
- **E-mails:** as páginas saem com `<!--email_off-->`, para o Cloudflare não esconder os endereços.
- **IndexNow:**
  - a chave fica na raiz, em `<chave>.txt`;
  - para avisar os buscadores, vá no GitHub em **Actions → Avisar buscadores (IndexNow) → Run workflow**;
  - rode só com o site novo no ar.
- **Blog:** o feed RSS (`/blog/feed.xml`) aparece quando houver artigo publicado.
- **Trava de publicação:** `make_vercel.py` se recusa a montar a versão de produção se houver texto entre colchetes ou aviso de rascunho.

## Validar a indexação antes de publicar

```
npm i --no-save @vercel/routing-utils
node fonte/site/tools/valida_indexacao.js .
```

O script confere, simulando as regras do `vercel.json`:
- canonical de cada página indexável igual à própria URL;
- sitemap só com páginas indexáveis, existentes e sem redirecionamento, e nenhuma indexável fora dele;
- links internos sem quebra e sem passar por redirecionamento;
- robots.txt com a linha do sitemap e sem bloquear páginas indexáveis;
- redirecionamentos do domínio, da barra final, de `index.html`, dos endereços antigos, do `assets` e do endereço de teste.

O resultado esperado é "PROBLEMAS (0)".

## Medição: Google Tag Manager e GA4

- **Ligar:** em `site/build.py`, preencha `CFG['gtm']` com o ID do contêiner (GTM-XXXXXXX), ou rode o build com `HH_GTM=GTM-XXXXXXX`. Vazio = nenhum script de análise e nenhum aviso de cookies.
- **Com o ID preenchido, o build:**
  - mostra o aviso de cookies (Aceitar, Recusar, Personalizar) e o link "Preferências de cookies" no rodapé;
  - libera os domínios do Google na CSP;
  - troca o texto da página /cookies/ pela versão com Google Analytics (rascunho, aguarda o jurídico).
- **Consent Mode v2, modo básico:** tudo começa negado e o GTM só é carregado depois do aceite. Os pedidos de publicidade ficam sempre negados (não há ferramenta de anúncio). A escolha fica 12 meses no navegador (`hh_cookies`). Se a pessoa recusar depois de aceitar, o site apaga os cookies `_ga`.
- **Eventos no dataLayer (site.js), sem dados pessoais:**

  | Evento | Parâmetros |
  |---|---|
  | `generate_lead` | form_name, lead_tipo (marca/agencia), lead_verba, lead_inicio |
  | `support_request` | form_name, support_uso, support_assunto |
  | `app_store_click` | store (app_store/google_play), link_local |
  | `painel_click` | painel_destino (cadastro/entrar), link_local |

  - `generate_lead` e `support_request` disparam na página de confirmação e só depois que o servidor aceitou o envio. Não duplicam se a página for recarregada.
  - Todas as páginas recebem `ambiente` (producao/teste/local).
- **Contêiner pronto:** `site/tools/gtm-container-hypeapp.json`, gerado por `python3 tools/gtm_container.py G-XXXXXXXXXX`. Importe em Admin › Importar contêiner.
  - Ele tem a Google tag e as 4 tags de evento.
  - Marca `traffic_type=internal` no teste e em localhost.
- **Microsoft Clarity** (projeto `z8cuz3l4nn`, em `CFG['clarity']`):
  - é carregado direto pelo site.js, fora do GTM, e só depois do aceite de medição;
  - recebe `consentv2` e a tag `ambiente` (producao/teste) para filtrar as gravações;
  - os dois formulários têm `data-clarity-mask="true"`, então nada do que é digitado aparece nas gravações;
  - se a pessoa revogar o aceite, o site apaga `_clck` e `_clsk`.
- **Não crie no GTM** tags de HTML personalizado nem variáveis de JavaScript personalizado: a CSP bloqueia. Para outra ferramenta (Google Ads, Meta), use os modelos da galeria e libere o domínio dela na CSP (`csp_ga()` no build.py).

## E-mail de confirmação após o formulário (04/11, personalizado em 05/11)

Depois de gravar o lead no CRM (resposta 201 do webhook), `api/lead.js` chama `api/_email.js`, que manda um e-mail
para quem preencheu o formulário, pelo SMTP do Purelymail (o mesmo do backoffice).

- **Remetente:** `HypeApp <noreply@hypeapp.com.br>`, com aviso de "Não responda a este e-mail" (o retorno é pelo WhatsApp ou dentro do app; os chamados vão para uma aba de suporte no backoffice).
- **18 situações:** lead de marca ou de agência ("Fale com nosso time") e suporte de creator (app) ou de marca (painel)
  para cada assunto (conta, redes, campanha, pagamento, erro, denúncia, exclusão, outro). Textos, dicas, botão e imagem
  de cada uma ficam em `SUP`, `IMG` e `situacao()` no `_email.js`. Só fatos publicados no site (prazo de 2 dias úteis,
  horário do suporte, regras do PIX).
- **Formato:** HTML leve (logo, uma imagem, texto curto, até 3 dicas, um botão) + texto puro. O logo e a imagem vão
  anexados no próprio e-mail (`cid:`), a partir de `site/assets/email/`; o `make_vercel.py` gera `api/_imagens.js`.
- **Variáveis:** `SMTP_USER` e `SMTP_PASS` (obrigatórias, Production e Preview); opcionais `SMTP_HOST`
  (padrão `smtp.purelymail.com`), `SMTP_PORT` (`465`), `SMTP_FROM` (`noreply@hypeapp.com.br`).
- **Falhas:** se o e-mail falhar, o lead continua gravado e o visitante vê a confirmação normal; o log mostra só
  `[email] confirmação não enviada (situação): motivo`, sem senha, nome ou e-mail. Tempo máximo da função: 30 s.
- **Entregabilidade:** o domínio `hypeapp.com.br` precisa de SPF, DKIM e DMARC válidos para o Purelymail
  (confira em "Mostrar original" no Gmail: SPF, DKIM e DMARC devem aparecer como PASS).
