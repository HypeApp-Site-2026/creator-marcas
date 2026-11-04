# Artigos do blog

Cada artigo é um arquivo `.md` nesta pasta. O nome do arquivo é o endereço: `meu-artigo.md` vira `/blog/meu-artigo/`.

```
---
titulo: Como transformar seu perfil em uma vitrine para marcas
categoria: Carreira            # Carreira, Parcerias, Conteúdo, Mercado...
data: 2026-11-10               # data de publicação (AAAA-MM-DD)
status: publicado              # publicado | revisao | rascunho | exemplo
capa: meu-artigo.webp          # arquivo em site/assets/blog/ (1600×1000, proporção 16:10)
capa_alt: Creator segurando o celular, com cartões de perfil e métricas ao redor
resumo: Uma frase com a resposta principal do artigo (vira a descrição de SEO).
autor: Nome Sobrenome          # opcional; só preencha com a autoria real
---

Texto do artigo em Markdown: parágrafos, ## subtítulos, listas, **negrito**, [links](https://...).
```

- **publicado**: entra no site, no sitemap e no carrossel da Início, do mais recente para o mais antigo (até 6).
- **revisao**: aparece na prévia e só no teste.hypeapp.com.br, com o aviso "em revisão" e sem indexação. No www os endereços voltam para a Início e o artigo fica fora do sitemap, do RSS e do llms-full.txt. Para publicar: troque para publicado e preencha a data.
- **rascunho**: não aparece em lugar nenhum.
- **exemplo**: aparece só na prévia, com o selo "Exemplo de layout". Nunca vai para a versão --web.
- O tempo de leitura é calculado do texto (200 palavras por minuto). Não escreva o tempo à mão.
- Enquanto não houver artigo publicado, a Início mostra "Novos conteúdos em breve." e o link do blog some da seção e do rodapé.
