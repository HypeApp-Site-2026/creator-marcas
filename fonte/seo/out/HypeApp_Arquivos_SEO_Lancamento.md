# HypeApp: arquivos técnicos do lançamento (v4, 26/10/2026)

Lançamento enxuto: 12 URLs no sitemap.xml e no llms.txt, mais 5 páginas de apoio fora do XML (/contato/marcas/, /contato/enviado/, /suporte/enviado/, /entrar/, /app). As demais páginas do mapa entram conforme a necessidade.

URLs dos públicos: /criadores/ e /marcas/ (marcas, empresas e agências; seção /marcas/#agencias).

Ordem de 26/10:
- Creators: o caminho principal é o acesso ao app (/baixar/, botão "Baixar o app"). /interesse/, /interesse/criadores/ e /interesse/confirmado/ saíram do lançamento e ficam suspensos.
- Marcas: o formulário de interesse continua em /contato/marcas/ ("Falar com o comercial").
- "Lista de espera", "acesso antecipado" e "nova versão em beta" ficam fora das mensagens principais até existir uma decisão sobre esse formato. /nova-versao/ continua fora do lançamento, com nome em revisão.

Redes oficiais (27/10): Instagram, YouTube e LinkedIn @hypeappbrasil, no sameAs do Organization e no llms.txt.

Regra de sincronia: toda URL nasce ou muda primeiro na matriz de metadados (HypeApp_Matriz_de_Metadados.xlsx). O sitemap.xml e o llms.txt são gerados a partir dela. Depois, atualizar o mapa visual e o canvas de design.

## robots.txt (produção)

```
# robots.txt · https://www.hypeapp.com.br
# Versão 1 · 26/10/2026
#
# Regra do site: nada é bloqueado em produção.
# Páginas de formulário, confirmação e busca usam a meta tag noindex
# e precisam continuar liberadas para que os buscadores leiam essa tag.
# Prévia e homologação ficam em outros endereços, com login e robots.txt próprio.

User-agent: *
Allow: /

# Buscadores e assistentes de IA (busca e respostas) estão liberados pela regra acima,
# entre eles Googlebot, Bingbot, OAI-SearchBot, ChatGPT-User, Claude-SearchBot,
# Claude-User e PerplexityBot.
#
# Treinamento de modelos: também liberado pela regra acima.
# Para não permitir treinamento, retire o "#" das linhas abaixo.
# Isso não afeta a presença nas buscas e respostas de IA.
#
# User-agent: GPTBot
# Disallow: /
#
# User-agent: ClaudeBot
# Disallow: /
#
# User-agent: Google-Extended
# Disallow: /
#
# User-agent: CCBot
# Disallow: /

Sitemap: https://www.hypeapp.com.br/sitemap.xml
```

## robots.txt (prévia e homologação)

```
# robots.txt · ambientes de prévia e homologação do site HypeApp
# Use este arquivo SOMENTE fora de produção. Estes ambientes também precisam de login.
User-agent: *
Disallow: /
```

## sitemap.xml

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!-- sitemap.xml do lançamento · www.hypeapp.com.br · gerado em 26/10/2026 a partir da matriz de metadados.
     Só URLs canônicas, publicadas e com resposta 200. O CMS deve acrescentar <lastmod> quando o conteúdo mudar de verdade.
     Lançamento enxuto: só URLs essenciais. As demais entram conforme a necessidade, sempre a partir da matriz.
     Páginas marcadas "Depois" na matriz entram aqui quando forem publicadas. -->
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <!-- Páginas principais -->
  <url><loc>https://www.hypeapp.com.br/</loc></url>
  <url><loc>https://www.hypeapp.com.br/criadores/</loc></url>
  <url><loc>https://www.hypeapp.com.br/marcas/</loc></url>
  <url><loc>https://www.hypeapp.com.br/sobre/</loc></url>
  <url><loc>https://www.hypeapp.com.br/contato/</loc></url>
  <url><loc>https://www.hypeapp.com.br/perguntas-frequentes/</loc></url>
  <!-- App e acesso -->
  <url><loc>https://www.hypeapp.com.br/baixar/</loc></url>
  <!-- Ajuda e suporte -->
  <url><loc>https://www.hypeapp.com.br/suporte/</loc></url>
  <!-- Confiança e privacidade -->
  <url><loc>https://www.hypeapp.com.br/privacidade/</loc></url>
  <url><loc>https://www.hypeapp.com.br/termos/</loc></url>
  <url><loc>https://www.hypeapp.com.br/cookies/</loc></url>
  <url><loc>https://www.hypeapp.com.br/exclusao-de-conta/</loc></url>
</urlset>
```

## llms.txt

```markdown
# HypeApp

> O HypeApp é a plataforma da Você no Hype que conecta creators e marcas em campanhas de marketing de influência, do convite ao pagamento. Creators usam o app no celular (iPhone e Android); marcas e agências usam o painel na web.

Informações oficiais:

- Nome do produto: HypeApp.
- Desenvolvido e operado por: Você no Hype Marketing e Entretenimento LTDA.
- Site oficial: https://www.hypeapp.com.br/
- App para iPhone: https://apps.apple.com/br/app/hype-app-influenciadores/id6778357608
- App para Android: https://play.google.com/store/apps/details?id=br.com.hypeapp.v2
- Instagram: https://www.instagram.com/hypeappbrasil/
- YouTube: https://www.youtube.com/@hypeappbrasil
- LinkedIn: https://www.linkedin.com/company/hypeappbrasil/
- Para marcas e agências, os valores são sob consulta com o comercial.
- Creators baixam o app e criam a conta por ele. Ter conta não garante participação em campanhas.
- Cada campanha tem critérios próprios; a seleção é feita pela marca ou pela curadoria.

## Sobre o HypeApp

- [Início](https://www.hypeapp.com.br/): o que é o HypeApp e para quem é.
- [Sobre](https://www.hypeapp.com.br/sobre/): quem opera o produto, relação com a Você no Hype e canais oficiais.
- [Perguntas frequentes](https://www.hypeapp.com.br/perguntas-frequentes/): respostas curtas sobre cadastro, campanhas, pagamentos, valores para marcas e segurança.

## Para creators

- [Para criadores](https://www.hypeapp.com.br/criadores/): como criadores e influenciadores participam de campanhas com marcas pelo app.
- [Baixar o app](https://www.hypeapp.com.br/baixar/): links oficiais da App Store e do Google Play e orientação para quem já tem conta.

## Para marcas e agências

- [Para marcas e agências](https://www.hypeapp.com.br/marcas/): como marcas, empresas e agências encontram creators e acompanham campanhas no painel; formas de trabalhar self-service e gerenciada.
- [Contato](https://www.hypeapp.com.br/contato/): formulário de interesse para marcas e agências, parcerias e privacidade.

## Ajuda e confiança

- [Suporte](https://www.hypeapp.com.br/suporte/): como abrir um chamado.
- [Política de privacidade](https://www.hypeapp.com.br/privacidade/): tratamento de dados, encarregado e direitos dos titulares.
- [Termos de uso](https://www.hypeapp.com.br/termos/)
- [Exclusão de conta](https://www.hypeapp.com.br/exclusao-de-conta/): como excluir a conta do app.
```
