// Valida a estrutura de indexação do site gerado (repo) simulando as regras do vercel.json
const fs=require('fs'),path=require('path');
const ROOT=process.argv[2]; const BASE='https://www.hypeapp.com.br';
const {getTransformedRoutes}=require('@vercel/routing-utils');
const cfg=JSON.parse(fs.readFileSync(path.join(ROOT,'vercel.json'),'utf8'));
const {routes}=getTransformedRoutes({trailingSlash:cfg.trailingSlash,redirects:cfg.redirects,rewrites:cfg.rewrites,headers:cfg.headers});
const exists=p=>{const f=path.join(ROOT,p.replace(/^\//,''));return fs.existsSync(f)&&fs.statSync(f).isFile()};
const fileFor=p=>{ if(p.endsWith('/')) return exists(p+'index.html')?p+'index.html':null; return exists(p)?p:(exists(p+'/index.html')?p+'/index.html':null)};
function route(host,p){ // segue redirecionamentos; devolve {final, hops, status}
  let hops=[];
  for(let i=0;i<6;i++){
    let hit=null;
    for(const r of routes){ if(!r.src||r.handle||!r.headers||!r.headers.Location) continue;
      if(r.has&&!r.has.every(h=>h.type!=='host'||h.value===host)) continue;
      if(r.missing&&r.missing.some(h=>h.type==='host'&&h.value===host)) continue;
      const m=new RegExp(r.src).exec(p); if(!m) continue;
      let loc=r.headers.Location; m.slice(1).forEach((g,j)=>{loc=loc.split('$'+(j+1)).join(g||'')}); if(m.groups) for(const k in m.groups) loc=loc.split('$'+k).join(m.groups[k]||'');
      hit={loc,status:r.status}; break; }
    if(!hit) return {final:p,host,hops,file:fileFor(p.split('#')[0])};
    hops.push(hit.status+' '+hit.loc);
    if(hit.loc.startsWith('http')){const u=new URL(hit.loc);host=u.host;p=u.pathname+(u.hash||'');} else p=hit.loc;
  }
  return {final:p,host,hops,file:null,loop:true};
}
const pages={};
(function walk(d){for(const f of fs.readdirSync(d)){const p=path.join(d,f);if(f==='fonte'||f==='.git'||f==='node_modules')continue;
  if(fs.statSync(p).isDirectory())walk(p);else if(f.endsWith('.html')){const rel='/'+path.relative(ROOT,p).replace(/\\/g,'/');pages[rel]=fs.readFileSync(p,'utf8');}}})(ROOT);
const urlOf=f=>f==='/index.html'?'/':f.endsWith('/index.html')?f.slice(0,-10):f;
const prob=[],ok=[];
// endereços só do ambiente de teste (artigos em revisão): redirecionam no www de propósito
const soTeste=(cfg.redirects||[]).filter(r=>(r.missing||[]).some(h=>h.type==='host'&&/^teste\./.test(h.value))).map(r=>new RegExp('^'+r.source+'$'));
const ehTeste=u=>soTeste.some(re=>re.test(u));
const meta=(t,re)=>{const m=re.exec(t);return m?m[1]:null};
const idx=new Set();
for(const [f,t] of Object.entries(pages)){
  const u=urlOf(f); if(u==='/404.html'||ehTeste(u)) continue;
  const rob=meta(t,/<meta name="robots" content="([^"]*)"/), can=meta(t,/<link rel="canonical" href="([^"]*)"/);
  if(!rob) prob.push(`${u}: sem meta robots`);
  if(rob&&!rob.includes('noindex')) idx.add(u);
  if(rob&&!rob.includes('noindex')){
    if(!can) prob.push(`${u}: indexável sem canonical`);
    else if(can!==BASE+u) prob.push(`${u}: canonical ${can} difere da própria URL`);
  } else if(can&&can!==BASE+u) prob.push(`${u}: noindex com canonical apontando para outra URL (${can})`);
  // links internos
  for(const m of t.matchAll(/href="(\/[^"]*)"/g)){
    let h=m[1]; if(h.startsWith('//'))continue; const clean=h.split('#')[0].split('?')[0]||'/';
    if(ehTeste(clean)) continue;
    const r=route('www.hypeapp.com.br',clean);
    if(r.hops.length) prob.push(`${u}: link ${h} redireciona (${r.hops.join(' → ')})`);
    else if(!r.file && !clean.startsWith('/backoffice') && !clean.startsWith('/api/')) prob.push(`${u}: link quebrado ${h}`);
  }
}
// sitemap
const sm=fs.readFileSync(path.join(ROOT,'sitemap.xml'),'utf8'); const locs=[...sm.matchAll(/<loc>([^<]+)<\/loc>/g)].map(x=>x[1]);
const lm=[...sm.matchAll(/<url><loc>[^<]+<\/loc>(<lastmod>\d{4}-\d{2}-\d{2}<\/lastmod>)?<\/url>/g)].length;
if(lm!==locs.length) prob.push('sitemap: entrada sem lastmod ou fora do formato');
const dup=locs.filter((x,i)=>locs.indexOf(x)!==i); if(dup.length) prob.push('sitemap: URLs duplicadas '+dup);
for(const l of locs){ if(!l.startsWith(BASE+'/')){prob.push('sitemap: fora do domínio canônico '+l);continue}
  const u=l.slice(BASE.length); const r=route('www.hypeapp.com.br',u);
  if(r.hops.length) prob.push(`sitemap: ${u} redireciona`); else if(!r.file) prob.push(`sitemap: ${u} não existe`);
  else if(!idx.has(u)) prob.push(`sitemap: ${u} está como noindex`); }
for(const u of idx) if(!locs.includes(BASE+u)) prob.push(`indexável fora do sitemap: ${u}`);
// robots
const rb=fs.readFileSync(path.join(ROOT,'robots.txt'),'utf8');
if(!/^Sitemap: https:\/\/www\.hypeapp\.com\.br\/sitemap\.xml$/m.test(rb)) prob.push('robots: sem a linha Sitemap absoluta');
const dis=[...rb.matchAll(/^Disallow:\s*(\S+)/gm)].map(x=>x[1]); for(const d of dis) for(const u of idx) if(u.startsWith(d)) prob.push(`robots bloqueia página indexável ${u}`);
// domínio, barra final e endereços antigos
const testes=[['hypeapp.com.br','/marcas/'],['www.hypeapp.com.br','/marcas'],['www.hypeapp.com.br','/marcas/index.html'],['www.hypeapp.com.br','/index.html'],
 ['www.hypeapp.com.br','/politica-de-privacidade'],['www.hypeapp.com.br','/termos-de-uso/'],['www.hypeapp.com.br','/faq'],['assets.hypeapp.com.br','/'],['assets.hypeapp.com.br','/politica-de-privacidade'],['teste.hypeapp.com.br','/robots.txt'],['www.hypeapp.com.br','/robots.txt'],['www.hypeapp.com.br','/blog/index.html'],['www.hypeapp.com.br','/blog/'],['teste.hypeapp.com.br','/blog/']];
const out=testes.map(([h,p])=>{const r=route(h,p);return `${h}${p} → ${r.hops.length?r.hops.join(' → '):'200'}${r.file||r.hops.length?'':' (sem arquivo)'}`});
console.log('PÁGINAS indexáveis:',idx.size,'| no sitemap:',locs.length);
console.log('PROBLEMAS ('+prob.length+'):'); [...new Set(prob)].forEach(p=>console.log('  - '+p));
console.log('ROTAS:'); out.forEach(o=>console.log('  '+o));
