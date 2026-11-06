# Relatório semanal do HypeApp

Toda segunda às 08h07 (Brasília), o workflow **Relatório semanal (coleta)** junta os dados do GA4 e do Search Console da última semana fechada (segunda a domingo) e das 4 anteriores. Às 09h, o agente de análise lê esses dados, compara com a semana anterior e a média de 4 semanas, confere os gatilhos de alerta da rotina e publica o relatório.

## Configuração (uma vez)

1. **Google Cloud:** num projeto do Google Cloud, ative a *Google Analytics Data API* e a *Google Search Console API*. Crie uma conta de serviço (sem papéis no projeto) e gere uma chave JSON.
2. **GA4:** em Administrador → Gerenciamento de acesso à propriedade, adicione o e-mail da conta de serviço como **Leitor**. Anote o **ID da propriedade** (número, em Administrador → Detalhes da propriedade).
3. **Search Console:** em Configurações → Usuários e permissões, adicione o e-mail da conta de serviço com permissão **Restrita**. Anote a propriedade: `sc-domain:hypeapp.com.br` (domínio) ou `https://www.hypeapp.com.br/` (prefixo de URL).
4. **GitHub:** no repositório, em Settings → Secrets and variables → Actions:
   - *Secrets* → `GA_SA_JSON`: cole o conteúdo inteiro da chave JSON;
   - *Variables* → `GA4_PROPERTY_ID` e `GSC_SITE`.
5. Teste em Actions → Relatório semanal (coleta) → Run workflow. O artefato `dados-semana` deve sair sem avisos em `erros`.

A chave fica só no GitHub. Ela nunca vai para o código, o chat ou os logs.

## O que vem automático e o que é manual

- **Automático (GA4 e Search Console):** usuários, sessões, canais, campanhas (UTM), eventos de conversão, páginas, cliques e impressões na busca, consultas e páginas da busca.
- **Manual por enquanto:** instalações (Play Console e App Store Connect), cadastros concluídos (backoffice), leads qualificados (CRM) e chamados (backoffice). O relatório deixa esses campos marcados para preencher.
- **Dimensões personalizadas:** CTAs por página, lojas por página e erros de formulário só aparecem depois de criadas no GA4 (veja a página Medição HypeApp).
