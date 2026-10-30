# -*- coding: utf-8 -*-
# Fonte única para a matriz, o sitemap.xml e o llms.txt.
BASE = "https://www.hypeapp.com.br"

# xml: "Sim" entra no sitemap.xml do lançamento | "Depois" entra quando publicada | "Não" fica fora
# pub: situação de publicação no lançamento
# Campos: url, pagina, publico, secao, prioridade, condicao, pub, robots, xml, title, desc, h1, pergunta, img, schema, obs
R = []
def add(url, pagina, publico, secao, prio, cond, pub, robots, xml, title, desc, h1, pergunta="", img="og/padrao.jpg", schema="—", obs=""):
    R.append(dict(url=url, pagina=pagina, publico=publico, secao=secao, prio=prio, cond=cond, pub=pub,
                  robots=robots, xml=xml, title=title, desc=desc, h1=h1, pergunta=pergunta, img=img, schema=schema, obs=obs))

IDX, NOI = "index, follow", "noindex, follow"
SIM_LANC = "Sim"
JUR = "Sim, após revisão jurídica"
VAL = "Se o recurso for validado"

# ---------- Páginas principais ----------
add("/", "Início", "Todos", "Páginas principais", "P0", "", SIM_LANC, IDX, "Sim",
    "HypeApp: campanhas entre creators e marcas",
    "Plataforma da Você no Hype que conecta creators e marcas: campanhas, convites, entregas, aprovações e pagamentos em um só lugar.",
    "O app de quem cria conteúdo. O painel de quem contrata.", "O que é o HypeApp?", "og/inicio.jpg", "Organization, WebSite")
add("/criadores/", "Para creators", "Creators", "Páginas principais", "P0", "", SIM_LANC, IDX, "Sim",
    "Para criadores e influenciadores | HypeApp",
    "Encontre campanhas de marcas no seu nicho, receba convites, entregue pelo app e acompanhe seus pagamentos na carteira do HypeApp.",
    "O app completo para quem cria conteúdo.", "Como conseguir campanhas com marcas?", "og/para-criadores.jpg")
add("/marcas/", "Para marcas e agências", "Marcas e agências", "Páginas principais", "P0", "", SIM_LANC, IDX, "Sim",
    "Para marcas e agências: campanhas com creators | HypeApp",
    "Encontre creators, aprove conteúdos e acompanhe resultados de várias marcas no mesmo painel. Opere sozinho ou com a Você no Hype.",
    "Campanhas com creators do jeito que sua equipe preferir.", "Como contratar creators para uma campanha?", "og/para-marcas.jpg")
add("/como-funciona/", "Como funciona", "Todos", "Páginas principais", "P0", "", SIM_LANC, IDX, "Sim",
    "Como funciona: creators e marcas | HypeApp",
    "O passo a passo para creators e para marcas: inscrição, seleção, convite, entrega, aprovação e pagamento.",
    "Como funciona o HypeApp", "Como funciona o HypeApp?", "og/como-funciona.jpg")
add("/funcionalidades/", "Funcionalidades", "Todos", "Páginas principais", "P0", "", SIM_LANC, IDX, "Sim",
    "Funcionalidades para creators e marcas | HypeApp",
    "Campanhas, convites, entregas, aprovações, carteira e métricas: conheça os recursos do app do creator e do painel das marcas.",
    "Funcionalidades", "O que dá para fazer no HypeApp?", "og/funcionalidades.jpg",
    obs="Descrever só recursos validados para o lançamento.")
add("/sobre/", "Sobre", "Todos", "Páginas principais", "P0", "", SIM_LANC, IDX, "Sim",
    "Sobre o HypeApp, da Você no Hype",
    "O HypeApp é a plataforma da Você no Hype para campanhas entre creators e marcas. Conheça quem opera o produto e os canais oficiais.",
    "Sobre o HypeApp", "Quem está por trás do HypeApp?", "og/sobre.jpg", "Organization (AboutPage)",
    "Mesma definição usada no Início, no rodapé e no llms.txt.")
add("/contato/", "Contato", "Todos", "Páginas principais", "P0", "", SIM_LANC, IDX, "Sim",
    "Contato | HypeApp",
    "Fale com o comercial, envie uma proposta de parceria, peça ajuda ao suporte ou faça uma solicitação sobre seus dados.",
    "Fale com o HypeApp", "Como falar com o HypeApp?", schema="ContactPage")
add("/perguntas-frequentes/", "Perguntas frequentes", "Todos", "Páginas principais", "P0", "", SIM_LANC, IDX, "Sim",
    "Perguntas frequentes | HypeApp",
    "Respostas rápidas sobre cadastro, campanhas, pagamentos, valores para marcas e segurança no HypeApp.",
    "Perguntas frequentes", "Dúvidas comuns sobre o HypeApp", obs="Sem marcação FAQPage, conforme a regra do sitemap.")
add("/mapa-do-site/", "Mapa do site", "Todos", "Páginas principais", "P0", "", SIM_LANC, IDX, "Sim",
    "Mapa do site | HypeApp",
    "Todas as páginas públicas do site do HypeApp, organizadas por seção.",
    "Mapa do site")
add("/nova-versao/", "Contas existentes (nome em revisão)", "Creators", "Páginas principais", "P0", "G", "Depois, conforme decisão", IDX, "Sim",
    "Nova versão do HypeApp: o que muda",
    "Já usava o HypeApp? Veja como atualizar, entrar com a mesma conta e o que acontece com campanhas, saldo e perfil.",
    "A nova versão do HypeApp", "Preciso me cadastrar de novo na nova versão?", "og/nova-versao.jpg", "—",
    "Não usar \"nova versão\" nem \"beta\" nas mensagens principais até haver decisão (ordem de 26/10). URL e textos serão revistos.")
add("/comunidade/", "Comunidade", "Creators", "Páginas principais", "P0", "G", VAL, IDX, "Depois",
    "Comunidade de creators | HypeApp",
    "Feed, grupos e lives para creators do HypeApp. Veja como participar e as regras da comunidade.",
    "Comunidade HypeApp", "Como participar da comunidade?", "og/comunidade.jpg")

# ---------- Captação e contato ----------
add("/interesse/", "Registrar interesse", "Todos", "Captação e contato", "P0", "", SIM_LANC, IDX, "Sim",
    "Registrar interesse no HypeApp",
    "Creator ou marca? Escolha seu perfil e registre seu interesse no relançamento do HypeApp. O registro não cria conta.",
    "Registre seu interesse", "Como entrar na lista do HypeApp?", "og/interesse.jpg",
    obs="Suspenso (ordem de 26/10): creators vão direto ao app e marcas usam /contato/marcas/. Textos com \"lista\" e \"relançamento\" serão revistos se a página voltar.")
add("/interesse/criadores/", "Formulário de creator", "Creators", "Captação e contato", "P0", "", SIM_LANC, NOI, "Não",
    "Interesse de creator | HypeApp",
    "Formulário de interesse para creators no relançamento do HypeApp.",
    "Quero participar como creator", obs="Suspenso (ordem de 26/10): creators vão direto ao app. Fica fora do lançamento até haver decisão.")
add("/interesse/confirmado/", "Interesse confirmado", "Creators", "Captação e contato", "P0", "", SIM_LANC, NOI, "Não",
    "Interesse registrado | HypeApp",
    "Seu interesse no HypeApp foi registrado.",
    "Recebemos seu interesse", obs="Suspenso junto com /interesse/ (ordem de 26/10).")
add("/contato/marcas/", "Falar com o comercial", "Marcas", "Captação e contato", "P0", "", SIM_LANC, NOI, "Não",
    "Falar com o comercial | HypeApp",
    "Conte sua campanha e o comercial do HypeApp responde com uma proposta.",
    "Fale com o comercial", obs="Formulário de interesse para marcas, com perguntas de qualificação. Mantido como CTA principal de /marcas/ (ordem de 26/10).")
add("/contato/parcerias/", "Parcerias e imprensa", "Todos", "Captação e contato", "P0", "", SIM_LANC, NOI, "Não",
    "Parcerias e imprensa | HypeApp",
    "Propostas de parceria, imprensa e eventos com o HypeApp.",
    "Parcerias e imprensa")
add("/contato/enviado/", "Mensagem recebida", "Todos", "Captação e contato", "P0", "", SIM_LANC, NOI, "Não",
    "Mensagem recebida | HypeApp",
    "Sua mensagem foi enviada ao HypeApp.",
    "Recebemos sua mensagem")
add("/preferencias-de-comunicacao/", "Preferências de comunicação", "Todos", "Captação e contato", "P0", "G", "Sim, se o envio de e-mails começar no lançamento", NOI, "Não",
    "Preferências de comunicação | HypeApp",
    "Escolha quais comunicações do HypeApp você quer receber.",
    "Suas preferências de comunicação", obs="Acesso por token. Cabeçalho Referrer-Policy: no-referrer.")

# ---------- App e acesso ----------
add("/baixar/", "Baixar o app", "Creators", "App e acesso", "P0", "G", "Sim", IDX, "Sim",
    "Baixar o HypeApp para iPhone e Android",
    "Baixe o HypeApp na App Store ou no Google Play. No computador, use o QR code para abrir a loja no celular.",
    "Baixe o HypeApp", "Como baixar o HypeApp?", "og/baixar.jpg", "MobileApplication, só com dados confirmados",
    "Caminho principal de creators (ordem de 26/10): os dois botões levam direto às lojas. Pedir a troca do nome da ficha no Google Play, que ainda diz \"V2 - Beta\".")
add("/app", "Link curto para as lojas", "Creators", "App e acesso", "P0", "G", "Sim", "Não se aplica (redirecionamento 302)", "Não",
    "—", "—", "—", obs="iPhone → App Store; Android → Google Play; outros → /baixar/.")
add("/entrar/", "Entrar", "Todos", "App e acesso", "P0", "", SIM_LANC, NOI, "Não",
    "Entrar no HypeApp",
    "Entre no app do creator ou no painel das marcas.",
    "Entrar como")

# ---------- Ajuda e suporte ----------
add("/ajuda/", "Central de ajuda", "Todos", "Ajuda e suporte", "P0", "", SIM_LANC, IDX, "Sim",
    "Central de ajuda | HypeApp",
    "Tire dúvidas sobre conta, redes sociais, campanhas, entregas, carteira e painel das marcas. Busque ou fale com o suporte.",
    "Como podemos ajudar?", "Onde tirar dúvidas sobre o HypeApp?", "og/ajuda.jpg")
add("/ajuda/busca/?q=", "Busca da ajuda", "Todos", "Ajuda e suporte", "P0", "", SIM_LANC, NOI, "Não",
    "Busca: {termo} | Ajuda HypeApp", "—", "Resultados para \"{termo}\"",
    obs="Não bloquear no robots.txt. Medir buscas sem resultado.")
add("/suporte/", "Suporte", "Todos", "Ajuda e suporte", "P0", "", SIM_LANC, IDX, "Sim",
    "Suporte: abra um chamado | HypeApp",
    "Abra um chamado com o suporte do HypeApp, informe o assunto e acompanhe o atendimento pelo número de protocolo.",
    "Fale com o suporte", "Como falar com o suporte do HypeApp?", schema="—")
add("/suporte/enviado/", "Chamado aberto", "Todos", "Ajuda e suporte", "P0", "", SIM_LANC, NOI, "Não",
    "Chamado aberto | HypeApp",
    "Seu chamado foi aberto no suporte do HypeApp.",
    "Chamado aberto", obs="Mostra protocolo e prazo aprovado.")

HELP = [
 ("primeiros-passos", "Primeiros passos", "Creators", "", "Primeiros passos | Ajuda HypeApp",
  "Como criar sua conta, completar o perfil e entender o que esperar do cadastro no HypeApp.", [
  ("o-que-e-o-hypeapp", "", "O que é o HypeApp? | Ajuda HypeApp",
   "O HypeApp conecta creators e marcas em campanhas, do convite ao pagamento. Entenda quem pode usar e quem opera a plataforma.", "O que é o HypeApp?"),
  ("quem-pode-participar", "G", "Quem pode participar do HypeApp? | Ajuda HypeApp",
   "Idade mínima e critérios para se cadastrar como creator no HypeApp.", "Quem pode participar do HypeApp?"),
  ("criar-conta-de-criador", "G", "Como criar sua conta de creator | Ajuda HypeApp",
   "Passo a passo para baixar o app, criar a conta, confirmar o e-mail e entrar no HypeApp.", "Como criar uma conta no HypeApp?"),
  ("completar-perfil", "G", "Como completar seu perfil | Ajuda HypeApp",
   "Quais dados o app pede no perfil de creator e por que o perfil completo ajuda na seleção.", "Como completar o perfil?"),
  ("cadastro-garante-campanhas", "", "O cadastro garante campanhas? | Ajuda HypeApp",
   "Não. Cada campanha tem critérios próprios e a seleção é feita pela marca ou pela curadoria. Veja como aumentar suas chances.", "O cadastro garante campanhas?"),
  ("atualizar-o-aplicativo", "G", "Como atualizar o app do HypeApp | Ajuda HypeApp",
   "Como atualizar o HypeApp no iPhone e no Android e o que fazer se a atualização não aparecer.", "Como atualizar o HypeApp?")]),
 ("conta-e-acesso", "Conta e acesso", "Todos", "G", "Conta e acesso | Ajuda HypeApp",
  "Entrar, recuperar senha, códigos de confirmação, telefone e permissões do app.", [
  ("entrar-e-recuperar-senha", "G", "Como entrar e recuperar a senha | Ajuda HypeApp",
   "Entre no app ou no painel com seu e-mail e recupere a senha se esquecer. App e painel têm acessos separados.", "Como recuperar a senha?"),
  ("codigo-de-confirmacao-nao-chegou", "G", "Código de confirmação não chegou | Ajuda HypeApp",
   "O que fazer quando o código de confirmação por e-mail, WhatsApp ou SMS não chega.", "O código de confirmação não chegou. E agora?"),
  ("confirmar-telefone", "G", "Como confirmar seu telefone | Ajuda HypeApp",
   "Por que o HypeApp pede a confirmação do telefone e como fazer, inclusive para liberar saques.", "Por que preciso confirmar o telefone?"),
  ("permissoes-do-aplicativo", "G", "Permissões do app | Ajuda HypeApp",
   "Para que o HypeApp usa câmera, fotos, notificações e localização e como mudar essas permissões.", "Para que o app pede permissões?")]),
 ("perfil-e-redes", "Perfil e redes", "Creators", "G", "Perfil e redes sociais | Ajuda HypeApp",
  "Conectar Instagram, TikTok e YouTube, métricas do perfil e valores por conteúdo.", [
  ("conectar-instagram", "G", "Como conectar o Instagram | Ajuda HypeApp",
   "Passo a passo para conectar sua conta do Instagram ao HypeApp e verificar o perfil.", "Como conectar o Instagram ao HypeApp?"),
  ("conectar-tiktok", "G", "Como conectar o TikTok | Ajuda HypeApp",
   "Passo a passo para autorizar sua conta do TikTok no HypeApp e voltar ao app.", "Como conectar o TikTok?"),
  ("conectar-youtube", "G", "Como conectar o YouTube | Ajuda HypeApp",
   "Como autorizar o canal certo do YouTube no HypeApp.", "Como conectar o YouTube?"),
  ("redes-nao-conectam", "G", "Minha rede social não conecta | Ajuda HypeApp",
   "Falhas comuns ao conectar redes no HypeApp e o que enviar ao suporte se o problema continuar.", "Por que minha rede não conecta?"),
  ("atualizacao-das-metricas", "G", "Como as métricas são atualizadas | Ajuda HypeApp",
   "De onde vêm as métricas do seu perfil no HypeApp e com que frequência são atualizadas.", "Quando as métricas atualizam?")]),
 ("campanhas-e-convites", "Campanhas e convites", "Creators", "G", "Campanhas e convites | Ajuda HypeApp",
  "Encontrar campanhas, se inscrever, critérios de seleção e convites das marcas.", [
  ("encontrar-e-filtrar-campanhas", "G", "Como encontrar campanhas | Ajuda HypeApp",
   "Use a busca e os filtros por nicho e formato para achar campanhas abertas no HypeApp.", "Como encontrar campanhas?"),
  ("inscrever-se-em-campanha", "G", "Como se inscrever em uma campanha | Ajuda HypeApp",
   "Passo a passo para se inscrever, escolher o perfil e enviar proposta quando a campanha pedir.", "Como me inscrever em uma campanha?"),
  ("criterios-de-selecao", "G", "Como funciona a seleção de creators | Ajuda HypeApp",
   "Requisitos, curadoria e motivos que podem impedir sua participação em uma campanha.", "Como os creators são selecionados?"),
  ("acompanhar-inscricao", "G", "Como acompanhar sua inscrição | Ajuda HypeApp",
   "O que significa cada status da inscrição: enviada, em análise, selecionada ou recusada.", "Como acompanhar minha inscrição?"),
  ("aceitar-ou-recusar-convite", "G", "Como aceitar ou recusar um convite | Ajuda HypeApp",
   "Veja as condições do convite, aceite ou recuse no app e saiba o que acontece se ele expirar.", "Como aceitar um convite?"),
  ("tipos-de-oportunidade", "G", "Paga, permuta e recebidos: tipos de campanha | Ajuda HypeApp",
   "Diferenças entre campanha paga, permuta, recebidos e campanhas por desempenho no HypeApp.", "Qual a diferença entre permuta e recebido?")]),
 ("entregas-e-aprovacoes", "Entregas e aprovações", "Creators", "G", "Entregas e aprovações | Ajuda HypeApp",
  "Briefing, contrato, roteiro, conteúdo, ajustes e registro da publicação.", [
  ("briefing-e-regras", "G", "Onde ver o briefing da campanha | Ajuda HypeApp",
   "Onde encontrar objetivo, arquivos, fases, direitos de uso e exigências de cada campanha.", "Onde vejo o briefing?"),
  ("contrato-digital", "G", "Como assinar o contrato da campanha | Ajuda HypeApp",
   "Como o contrato chega por e-mail, como assinar e onde acompanhar o status no app.", "Como assinar o contrato?"),
  ("enviar-roteiro", "G", "Como enviar o roteiro | Ajuda HypeApp",
   "Envie o roteiro pelo app, acompanhe a aprovação e mande uma nova versão se a marca pedir ajustes.", "Como enviar o roteiro?"),
  ("enviar-conteudo", "G", "Como enviar o conteúdo para aprovação | Ajuda HypeApp",
   "Formatos aceitos, limites de arquivo e como acompanhar a aprovação do conteúdo.", "Como enviar o conteúdo?"),
  ("corrigir-uma-entrega", "G", "Como corrigir uma entrega | Ajuda HypeApp",
   "Veja o pedido de ajuste da marca, reenvie o conteúdo e acompanhe a aprovação final.", "A marca pediu ajuste. E agora?"),
  ("registrar-publicacao", "G", "Como registrar a publicação | Ajuda HypeApp",
   "Envie o link do post publicado para concluir a etapa da campanha.", "Como registrar a publicação?"),
  ("receber-produtos", "G", "Como receber produtos de uma campanha | Ajuda HypeApp",
   "Como funciona o envio de produtos em permuta e como confirmar o recebimento no app.", "Como recebo os produtos?")]),
 ("carteira-e-pagamentos", "Carteira e pagamentos", "Creators", "G", "Carteira e pagamentos | Ajuda HypeApp",
  "Saldos, liberação de pagamentos, saque via PIX e documentos fiscais.", [
  ("entender-os-saldos", "G", "Saldo em campanha, a liberar e disponível | Ajuda HypeApp",
   "O que significa cada saldo da carteira do HypeApp e quando o valor fica disponível para saque.", "O que significa cada saldo?"),
  ("quando-o-pagamento-e-liberado", "G", "Quando o pagamento é liberado? | Ajuda HypeApp",
   "Condições e prazo para o valor de uma campanha ser liberado na carteira do HypeApp.", "Quando recebo o pagamento?"),
  ("solicitar-saque-pix", "G", "Como sacar via PIX | Ajuda HypeApp",
   "Passo a passo para solicitar o saque do saldo disponível para sua chave PIX.", "Como sacar o dinheiro?"),
  ("saque-pendente-ou-com-erro", "G", "Saque pendente ou com erro | Ajuda HypeApp",
   "Como acompanhar um saque que não caiu e quando acionar o suporte.", "Meu saque não caiu. O que fazer?"),
  ("documentos-fiscais-e-recebimentos", "G", "Documentos fiscais e recebimentos | Ajuda HypeApp",
   "Quais documentos são pedidos antes do pagamento, conforme a campanha e seu cadastro como pessoa física ou jurídica.", "Preciso emitir nota fiscal?")]),
 ("comunidade-e-pontos", "Comunidade e pontos", "Creators", "G", "Comunidade e pontos | Ajuda HypeApp",
  "Feed, grupos, lives, Hype Points e como denunciar ou bloquear.", [
  ("publicar-e-interagir", "G", "Como publicar na comunidade | Ajuda HypeApp",
   "Publique, comente e exclua suas publicações no feed da comunidade do HypeApp.", "Como publicar na comunidade?"),
  ("participar-de-grupos", "G", "Como participar de grupos | Ajuda HypeApp",
   "Como entrar e sair de grupos e quais são os grupos oficiais do HypeApp.", "Como entrar em um grupo?"),
  ("assistir-lives", "G", "Como assistir às lives | Ajuda HypeApp",
   "Agenda, lives ao vivo, gravações e o que fazer se o vídeo não carregar.", "Como assistir às lives?"),
  ("hype-points-e-niveis", "G", "Hype Points e níveis | Ajuda HypeApp",
   "Como você ganha Hype Points, como funcionam os níveis e por que pontos não são saldo.", "O que são Hype Points?"),
  ("denunciar-e-bloquear", "G", "Como denunciar ou bloquear | Ajuda HypeApp",
   "Denuncie publicações ou perfis, bloqueie usuários e saiba como a moderação responde.", "Como denunciar um perfil?")]),
 ("marcas-e-agencias", "Marcas e agências", "Marcas", "G", "Ajuda para marcas e agências | HypeApp",
  "Acesso ao painel, campanhas, creators, aprovações, contratos, pagamentos, resultados e equipe.", [
  ("criar-conta-e-workspace", "G", "Como acessar o painel de marcas | Ajuda HypeApp",
   "Como o acesso ao painel é liberado depois do contato com o comercial e como configurar o workspace.", "Como acessar o painel?"),
  ("criar-e-publicar-campanha", "G", "Como criar e publicar uma campanha | Ajuda HypeApp",
   "Briefing, público, remuneração, materiais e fases: o passo a passo no painel do HypeApp.", "Como criar uma campanha?"),
  ("encontrar-criadores-e-criar-listas", "G", "Como encontrar creators e montar listas | Ajuda HypeApp",
   "Use filtros de rede, nicho e alcance e organize creators em listas por campanha.", "Como encontrar creators?"),
  ("selecionar-e-convidar-criadores", "G", "Como selecionar e convidar creators | Ajuda HypeApp",
   "Pré-selecione creators, envie convites e negocie as condições pelo painel.", "Como convidar creators?"),
  ("aprovar-roteiros-e-conteudos", "G", "Como aprovar roteiros e conteúdos | Ajuda HypeApp",
   "Revise, peça ajustes e aprove roteiros e conteúdos antes da publicação.", "Como aprovar um conteúdo?"),
  ("contratos-da-campanha", "G", "Contratos da campanha | Ajuda HypeApp",
   "Como os contratos são enviados e assinados e onde acompanhar o status no painel.", "Como funcionam os contratos?"),
  ("saldo-depositos-e-pagamentos", "G", "Saldo, depósitos e pagamentos | Ajuda HypeApp",
   "Depósito via PIX, reservas, pagamentos a creators, taxas, devoluções e documentos fiscais.", "Como pagar os creators?"),
  ("acompanhar-resultados", "G", "Como acompanhar os resultados | Ajuda HypeApp",
   "Indicadores disponíveis no painel para cada campanha e como lê-los.", "Como ver os resultados da campanha?"),
  ("equipe-e-permissoes", "G", "Equipe e permissões no painel | Ajuda HypeApp",
   "Convide membros da equipe e defina o que cada papel pode fazer no painel.", "Como adicionar minha equipe?")]),
 ("problemas-e-seguranca", "Problemas e segurança", "Todos", "", "Problemas e segurança | Ajuda HypeApp",
  "Reportar erros, app lento e como reconhecer os canais oficiais do HypeApp.", [
  ("reportar-um-erro", "", "Como reportar um erro | Ajuda HypeApp",
   "O que incluir no chamado para o suporte resolver mais rápido: versão, aparelho, passos e imagem.", "Como reportar um erro?"),
  ("aplicativo-lento-ou-indisponivel", "G", "App lento ou fora do ar | Ajuda HypeApp",
   "Verificações rápidas e onde ver se há instabilidade no HypeApp.", "O app está fora do ar?"),
  ("identificar-canais-oficiais", "", "Canais oficiais do HypeApp | Ajuda HypeApp",
   "Como reconhecer o app, o site e os contatos verdadeiros do HypeApp e evitar golpes e falsas cobranças.", "Como saber se um contato é do HypeApp?")]),
]
for slug, nome, publico, cg, ctitle, cdesc, arts in HELP:
    cat_ok = cg == ""
    add(f"/ajuda/{slug}/", nome, publico, "Ajuda e suporte", "P0", cg, SIM_LANC if cat_ok else VAL, IDX, "Sim" if cat_ok else "Depois",
        ctitle, cdesc, nome, schema="BreadcrumbList",
        obs="Categoria publicada só com artigos prontos.")
    for a, g, t, d, q in arts:
        ok = g == ""
        add(f"/ajuda/{slug}/{a}/", t.split(" | ")[0], publico, "Ajuda e suporte", "P0", g, SIM_LANC if ok else VAL, IDX,
            "Sim" if ok else "Depois", t, d, t.split(" | ")[0],
            q, "og/ajuda.jpg", "Article, BreadcrumbList",
            "" if ok else "Escrever e publicar depois da homologação do recurso.")

# ---------- Conteúdo ----------
add("/blog/", "Blog", "Todos", "Blog e atualizações", "P0", "", "Sim, com os primeiros artigos publicados", IDX, "Sim",
    "Blog do HypeApp: carreira e marketing de influência",
    "Artigos sobre carreira de creator, campanhas, UGC, precificação e marketing de influência, escritos pela equipe da Você no Hype.",
    "Blog do HypeApp", img="og/blog.jpg", schema="Blog",
    obs="Se não houver artigos no lançamento, a página fica em rascunho e sai do sitemap.xml e do menu.")
for slug, nome, desc in [
    ("carreira-do-criador", "Carreira de creator", "Como profissionalizar o perfil, conseguir parcerias e crescer como creator."),
    ("campanhas-e-parcerias", "Campanhas e parcerias", "Como funcionam campanhas pagas, permutas e parcerias entre creators e marcas."),
    ("conteudo-e-ugc", "Conteúdo e UGC", "Formatos, roteiros e boas práticas de conteúdo e UGC para campanhas."),
    ("gestao-e-precificacao", "Gestão e precificação", "Como precificar conteúdo, organizar entregas e cuidar da parte financeira."),
    ("marketing-de-influencia", "Marketing de influência", "Estratégia, seleção de creators e métricas de marketing de influência para marcas.")]:
    add(f"/blog/categoria/{slug}/", nome, "Todos", "Blog e atualizações", "P0", "G", "Quando tiver artigos", IDX, "Depois",
        f"{nome} | Blog HypeApp", desc, nome, schema="CollectionPage, BreadcrumbList")
add("/atualizacoes/", "Atualizações", "Todos", "Blog e atualizações", "P0", "", "Sim, com a nota do relançamento", IDX, "Sim",
    "Atualizações do HypeApp",
    "Novidades e mudanças do app e do painel do HypeApp, com data e disponibilidade por plataforma.",
    "Atualizações", img="og/atualizacoes.jpg")

# ---------- Legal ----------
for url, nome, title, desc, h1 in [
    ("/privacidade/", "Privacidade", "Política de privacidade | HypeApp",
     "Como a Você no Hype trata dados pessoais no site e no app do HypeApp, os direitos dos titulares e o contato do encarregado.", "Política de privacidade"),
    ("/termos/", "Termos", "Termos de uso | HypeApp",
     "Regras de uso do site e do app do HypeApp para creators, marcas e agências.", "Termos de uso"),
    ("/cookies/", "Cookies", "Política de cookies | HypeApp",
     "Quais cookies e tecnologias o site do HypeApp usa, para quê e como mudar suas preferências.", "Política de cookies"),
    ("/direitos-sobre-dados/", "Direitos sobre dados", "Direitos sobre seus dados | HypeApp",
     "Peça acesso, correção, exclusão ou outras informações sobre seus dados pessoais no HypeApp.", "Direitos sobre seus dados"),
    ("/exclusao-de-conta/", "Exclusão de conta", "Como excluir sua conta | HypeApp",
     "Passo a passo para excluir sua conta no app do HypeApp ou pedir a exclusão sem login, com prazos e o que é mantido.", "Como excluir sua conta"),
    ("/regras-da-comunidade/", "Regras da comunidade", "Regras da comunidade | HypeApp",
     "Conduta esperada no HypeApp, como denunciar e o que acontece em caso de violação.", "Regras da comunidade")]:
    add(url, nome, "Todos", "Confiança e privacidade", "P0", "G", JUR, IDX, "Sim", title, desc, h1,
        obs="Bloqueia o lançamento: o site não coleta dados nos formulários sem estas páginas no ar.")
add("/legal/", "Documentos legais", "Todos", "Confiança e privacidade", "P0", "", "Sim", IDX, "Sim",
    "Documentos legais | HypeApp",
    "Política de privacidade, termos de uso, cookies, encarregado de dados e exclusão de conta do HypeApp em um só lugar.",
    "Documentos legais")
add("/direitos-sobre-dados/confirmacao/", "Solicitação recebida", "Todos", "Confiança e privacidade", "P0", "G", JUR, NOI, "Não",
    "Solicitação recebida | HypeApp", "Sua solicitação sobre dados pessoais foi recebida.", "Solicitação recebida")

# ---------- Modelos de rota ----------
TEMPLATES = [
 ("/blog/{slug}/", "Artigo do blog", "{Título do artigo} | Blog HypeApp", "Resumo do artigo em até 155 caracteres, com a resposta principal.", IDX, "Sim, quando publicado", "Própria", "Article, BreadcrumbList", "og/blog/{slug}.jpg (1200×630)", "Autoria real, data de publicação e de revisão visíveis."),
 ("/blog/pagina/{n}/", "Blog, página n", "Blog do HypeApp · página {n}", "Mesma descrição do /blog/ com \"página {n}\".", IDX, "Não", "Própria (nunca a página 1)", "—", "og/blog.jpg", "/blog/pagina/1/ redireciona para /blog/. Página além do total responde 404."),
 ("/blog/categoria/{slug}/pagina/{n}/", "Categoria, página n", "{Categoria} · página {n} | Blog HypeApp", "Descrição da categoria com \"página {n}\".", IDX, "Não", "Própria", "—", "og/blog.jpg", "Mesma regra da paginação do blog."),
 ("/blog/busca/?q=", "Busca do blog", "Busca: {termo} | Blog HypeApp", "—", NOI, "Não", "Nenhuma", "—", "og/padrao.jpg", "Não bloquear no robots.txt."),
 ("/autores/{slug}/", "Autor", "{Nome do autor} | HypeApp", "Bio curta: função e experiência com o tema.", IDX, "Sim, com o primeiro artigo do autor", "Própria", "Person (ProfilePage)", "Foto do autor", "Publicar junto com o primeiro artigo."),
 ("/atualizacoes/{slug}/", "Nota de versão", "{Título da nota} | Atualizações HypeApp", "O que mudou, para quem e quando.", IDX, "Sim, quando publicada", "Própria", "Article, BreadcrumbList", "og/atualizacoes.jpg", "Data e plataforma (iPhone, Android, painel) visíveis."),
 ("/cases/{slug}/", "Case", "{Marca}: {resultado} | Cases HypeApp", "Contexto, o que foi feito e o resultado com metodologia.", IDX, "Sim, quando publicado (P1)", "Própria", "Article, BreadcrumbList", "og/cases/{slug}.jpg", "Só com autorização de marca e creator."),
 ("app.hypeapp.com.br/u/{username}", "Perfil público do creator", "{Nome} (@{username}) | HypeApp", "Nicho e redes do creator.", NOI, "Não (sitemap próprio no futuro)", "Própria", "—", "Imagem gerada do perfil (1200×630)", "Noindex por padrão. Metadados sociais obrigatórios mesmo com noindex."),
 ("app.hypeapp.com.br/campaigns/{id}/invite", "Convite de campanha", "Convite: {campanha} | HypeApp", "{Marca} convidou você para a campanha {campanha}.", NOI, "Não", "Própria", "—", "Imagem gerada da campanha (1200×630)", "Prévia no WhatsApp e redes depende das tags no HTML do servidor."),
]

# ---------- Regras ----------
RULES = [
 ("Domínio canônico", "https://www.hypeapp.com.br", "hypeapp.com.br e http:// redirecionam (301) para https://www."),
 ("Formato de URL", "Minúsculas, sem acento, hífen entre palavras, barra final", "Uma intenção, uma URL. Sem datas nem IDs."),
 ("Title", "Até cerca de 60 caracteres", "Termina em \" | HypeApp\" (ajuda: \" | Ajuda HypeApp\"; blog: \" | Blog HypeApp\"). O Início leva a marca no começo."),
 ("Meta description", "Até cerca de 155 caracteres", "Responde à pergunta da página na primeira frase. Sem promessas de recursos não validados."),
 ("H1", "Um por página", "Pode ser diferente do title; deve casar com a pergunta principal."),
 ("Canonical", "Própria, absoluta, sem parâmetros", "UTMs e ?origem= apontam para a URL limpa. Paginação nunca aponta para a página 1."),
 ("Meta robots", "index, follow ou noindex, follow", "Páginas com noindex continuam liberadas no robots.txt."),
 ("Open Graph", "og:title, og:description, og:image, og:url, og:type, og:locale=pt_BR", "Renderizadas no HTML do servidor, não por JavaScript."),
 ("Imagem social", "1200×630 px, JPG ou PNG, até 1 MB", "Uma por página principal; demais usam og/padrao.jpg."),
 ("Twitter/X", "twitter:card = summary_large_image", "Repete título, descrição e imagem do Open Graph."),
 ("Idioma", "<html lang=\"pt-BR\">", "Sem hreflang até existir outra língua."),
 ("Ícones", "favicon.ico, favicon.svg, apple-touch-icon.png 180×180, site.webmanifest", "Ver lista de materiais (item 17 da revisão)."),
 ("Dados estruturados", "JSON-LD", "Organization com sameAs no Início e em Sobre; BreadcrumbList em rotas com 2+ níveis; Article na ajuda e no blog; MobileApplication só com dados confirmados. Sem FAQPage, avaliações ou preços."),
 ("sitemap.xml", "Só URLs canônicas, publicadas e com resposta 200", "lastmod gerado pelo CMS quando o conteúdo muda de verdade. Sem changefreq e priority."),
 ("Página retirada", "301 com substituto, 410 sem substituto", "Sai do sitemap.xml e dos links internos no mesmo deploy."),
]

ORG_JSONLD = """{
  "@context": "https://schema.org",
  "@type": "Organization",
  "name": "HypeApp",
  "url": "https://www.hypeapp.com.br/",
  "logo": "https://www.hypeapp.com.br/assets/logo-hypeapp.svg",
  "description": "Plataforma da Você no Hype que conecta creators e marcas em campanhas de marketing de influência.",
  "parentOrganization": {
    "@type": "Organization",
    "name": "Você no Hype Marketing e Entretenimento LTDA"
  },
  "sameAs": [
    "https://www.instagram.com/hypeappbrasil/",
    "https://www.youtube.com/@hypeappbrasil",
    "https://www.linkedin.com/company/hypeappbrasil/",
    "https://apps.apple.com/br/app/hype-app-influenciadores/id6778357608",
    "https://play.google.com/store/apps/details?id=br.com.hypeapp.v2"
  ]
}"""
