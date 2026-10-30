# HypeApp · passagem do site v6 (consolidada, 29/10/2026)

Esta versão junta a passagem v6 do outro chat (respostas do Lucas de 29/10) com o que foi feito no chat da prévia EQG9J7. Substitui a v5 como ponto de partida.

## 1. Atenção: havia dois códigos em paralelo

Dois chats trabalharam no site a partir da mesma v4, cada um com seu zip e sua prévia.

- **Este código (hypeapp-site-v6.zip):**
  - prévia https://claude.ai/artifact/EQG9J7hyMVMHBMXzTGPVXZ;
  - tem tudo da lista da seção 3;
  - tem as decisões de 29/10 aplicadas a partir da descrição da passagem v6.
- **Código do outro chat (hypeapp-site.zip de 29/10, 10h32):**
  - prévia LL9EANC3…, que não abre nesta conta;
  - não foi recebido aqui.
  - O que ele tem: o menu com cartão roxo, a revisão de copy de 27/10 e o banco de perguntas.

**Daqui em diante, usar um código só.** Recomendação: seguir com este, que é o mais completo em design e técnica, e comparar uma vez os textos com o zip das 10h32, que traz a redação exata.

## 2. Como retomar

1. Abra um chat novo dentro do Project HypeApp.
2. Anexe o **hypeapp-site-v6.zip**.
3. Peça para ler esta passagem e descompactar o zip antes de mexer no site.
4. Dependências do build: `pip install qrcode pillow playwright markdown opencv-python`.
5. Ordem de cada mudança:
   1. seo/data.py
   2. seo/build.py
   3. site/build.py e site/build.py --web
   4. publicar a prévia no mesmo link
   5. atualizar o resumo de SEO no Project

## 3. O que este código tem (feito entre 27 e 29/10)

**Técnico**
- **Formulários:** os do comercial e do suporte enviam de verdade pelo Netlify Forms, com filtro de robôs. Ainda falta ativar as notificações no Netlify.
- **Fonte:** a Inter fica no próprio site, sem Google Fonts.
- **Ícones e imagens sociais:** favicon, ícone da Apple, manifest e 6 imagens de compartilhamento (make_media.py).
- **Netlify:**
  - _redirects com o domínio canônico, as rotas suspensas e 301 de URLs comuns (/termos-de-uso, /faq…);
  - _headers com CSP e cache.
  - Falta incluir as URLs do site antigo quando houver o inventário.
- **Checagem de lançamento:** `build.py --web` lista os textos entre colchetes que ainda estão no site.
- **Simulador de iPhone:** só na prévia (/iphone/), com SE, 16 e 16 Pro Max.

**Início**
- **Hero:**
  - título em caixa alta, peso 800;
  - subtítulo "O app de gestão de carreira para creators e a plataforma de gestão de campanhas para marcas.";
  - sem o bloco de números;
  - ilustração animada (assets/hero) com telas reais trocando a cada 2,5 s.
- **Como funciona:**
  - abas Creators e Marcas;
  - 4 clipes de 4 s para creators (make_comofunciona.py) e 4 ilustrações para marcas;
  - carrossel com o card ativo roxo e bento build ao aparecer.
- **Gestão da carreira:** quadro preto com mosaico de 4 blocos (celular Início, Recebimentos, Próxima entrega e personagem) e bento build.
- **Blog:**
  - seção depois do FAQ, página /blog/ e modelo de artigo, com os artigos em content/blog/*.md (ver LEIA-ME);
  - sem artigo publicado: mostra "Novos conteúdos em breve." e esconde os links;
  - os três exemplos de layout aparecem só na prévia.

**Creators**
- **Como se candidatar:** process draw horizontal num quadro preto, com 5 etapas e telas reais. A seção fica fixa enquanto a rolagem avança.

**Marcas**
- **Cursor tour:** no painel animado e nas 19 telas das vitrines.
- **Barras de navegador:** sem [endereço do painel]. O endereço aparece sozinho quando for preenchido em `CFG['painel']`.
- **CTA final:** "Marque uma demonstração e veja como fica a sua gestão de marketing.", com botão maior.

**Site todo**
- **Botões:** os CTAs "Falar com o comercial" agora dizem "Falar com nosso time".
- **Menu "Para marcas":** usa a ilustração do monitor com o painel.

## 4. Decisões de 29/10 aplicadas aqui

| Decisão | Como ficou |
|---|---|
| Gratuito para creators | "Grátis para iPhone e Android" em /criadores/ e /baixar/. FAQ: sem mensalidade e sem taxa sobre o valor recebido |
| 18+ sem mínimo de seguidores | Em /criadores/, /baixar/, /entrar/ e FAQ |
| Contas antigas | "Entre com o mesmo e-mail e a mesma senha" em /baixar/ e FAQ |
| Comercial em até 1 dia útil | /contato/marcas/ e /contato/enviado/ |
| Suporte em até 2 dias úteis | /suporte/ e /suporte/enviado/ |
| Recebidos e permuta | FAQ novo: o mural de cada campanha informa se o produto fica ou volta |
| Uso de imagem | FAQ novo: depende do contrato entre creator e marca |
| Creator não entrega | FAQ novo para marcas: o valor volta ao saldo da campanha |
| Métricas | Vêm direto das redes. A lista final continua entre colchetes |
| Hype Points fora do site | Saiu a tela app-C2 da vitrine "Organização" e a menção a pontos nos grupos |
| Mínimo por campanha | Continua "Valores sob consulta" |
| E-mail único (30/10) | contato@vocenohype.com.br em suporte, parcerias, privacidade, encarregado e exclusão de conta, inclusive nos textos legais |

**Ainda em confirmação com a operação:** liberação do pagamento, regras do saque e nota fiscal (PF/MEI). Os textos atuais ficam como estão.

**Hype Points no texto legal:** a política de privacidade cita Hype Points. Texto legal só muda com o jurídico.

**Mockups:** os textos de exemplo entre colchetes foram trocados por dados fictícios no padrão do app: @bianca.alves, @dudalima, @rafacosta, @ninarocha, Brisa de Verão, Café Brasa, Run Club SP e 10/11.

## 5. Ainda entre colchetes (13, todos dependem da equipe)

- **Painel:** endereço do painel (/entrar/).
- **Marcas:** critérios de curadoria, regras de acesso por marca, lista final de indicadores e as faixas 1 a 3 de investimento.
- **Creators e app:** prazos de pagamento, regras da comunidade e versão mínima do Android.
- **Suporte:** protocolo do chamado (tirar a linha se não houver).
- **Cookies:** inventário real e preferências.

## 6. Regras (sem mudança)

- **Vocabulário:** "creators" na interface; "influenciadores" só em SEO; "mural da campanha"; "painel"; "HypeApp".
- **Mensagens proibidas:** "lista de espera", "acesso antecipado", "nova versão em beta". Hype Points também ficam fora.
- **Telas proibidas:** app C1, C4 e G8 e as telas de administração.
- **Painel:** as capturas ainda mostram "Admin da plataforma" e precisam ser exportadas de novo.
- **site.js:** só em ASCII.
- **Textos legais:** não editar sem o jurídico.
- **Placeholders:** não inventar números, prazos ou regras.
- **Netlify:** só publicar com autorização do Lucas.

## 7. Prazos

Congelamento em 04/11. Site no ar em 05/11. Feriado em 02/11.
