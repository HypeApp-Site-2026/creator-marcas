# Site do HypeApp · www.hypeapp.com.br

Site estático publicado no Vercel. A raiz do repositório é o site pronto. O código que gera o site fica em `fonte/` e não vai ao ar.

## Publicar no Vercel (primeira vez)

1. Vercel → **Add New → Project → Import** este repositório.
2. Em **Framework Preset**, escolha **Other**. Deixe Build Command e Output Directory vazios: o `vercel.json` já define tudo.
3. **Environment Variables** (Production):
   - `RESEND_API_KEY`: chave do Resend, para os formulários enviarem e-mail.
   - `FORM_TO` (opcional): destino. O padrão é contato@vocenohype.com.br.
   - `FORM_FROM` (opcional): remetente, depois de verificar o domínio no Resend. Por exemplo, `Site HypeApp <site@hypeapp.com.br>`.
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

`api/contato.js` recebe os formulários "Falar com nosso time" e "Suporte" e envia para contato@vocenohype.com.br pelo Resend:
- valida os campos e o filtro de robôs;
- se a chave não estiver configurada, o site mostra "Não foi possível enviar" com o e-mail de contato.
