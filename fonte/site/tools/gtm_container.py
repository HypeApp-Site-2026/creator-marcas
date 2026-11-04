"""Gera o contêiner do Google Tag Manager do site HypeApp para importar (Admin > Importar contêiner).

Uso:  python3 tools/gtm_container.py [G-XXXXXXXXXX]
Saída: tools/gtm-container-hypeapp.json

O que vai no contêiner:
- Google tag do GA4 em todas as páginas (o site só carrega o GTM depois do aceite de cookies de medição);
- traffic_type=internal no teste.hypeapp.com.br e em localhost (o filtro de tráfego interno do GA4 descarta);
- eventos do dataLayer do site.js: generate_lead, support_request, app_store_click, painel_click;
- todas as tags exigem analytics_storage concedido (Consent Mode v2).
Sem tags de HTML personalizado nem variáveis de JavaScript personalizado: a CSP do site não permite.
"""
import json, os, re, sys
from datetime import datetime, timezone

GA = sys.argv[1] if len(sys.argv) > 1 else 'G-XXXXXXXXXX'
if not re.fullmatch(r'G-[A-Z0-9]{6,12}', GA):
    raise SystemExit('Use o ID de medição do GA4 no formato G-XXXXXXXXXX')

ACC, CON = '0', '0'
ALL_PAGES = '2147479553'
ids = iter(range(1, 1000))


def base(kind, name, **kw):
    d = {'accountId': ACC, 'containerId': CON, kind: str(next(ids)), 'name': name}
    d.update(kw)
    return d


def tpl(k, v):
    return {'type': 'TEMPLATE', 'key': k, 'value': v}


def tabela(pares):
    return {'type': 'LIST', 'key': None, 'list': [{'type': 'MAP', 'map': [tpl('parameter', p), tpl('parameterValue', v)]} for p, v in pares]}


CONSENT = {'consentStatus': 'NEEDED', 'consentType': {'type': 'LIST', 'list': [{'type': 'TEMPLATE', 'value': 'analytics_storage'}]}}

# ---------- variáveis ----------
variaveis = [base('variableId', 'GA4 - ID', type='c', parameter=[tpl('value', GA)])]
DLV = ['ambiente', 'form_name', 'lead_tipo', 'lead_verba', 'lead_inicio', 'support_uso', 'support_assunto', 'store', 'link_local', 'painel_destino']
for n in DLV:
    variaveis.append(base('variableId', f'DLV - {n}', type='v', parameter=[
        {'type': 'INTEGER', 'key': 'dataLayerVersion', 'value': '2'},
        {'type': 'BOOLEAN', 'key': 'setDefaultValue', 'value': 'false'},
        tpl('name', n)]))
variaveis.append(base('variableId', 'GA4 - traffic_type', type='smm', parameter=[
    {'type': 'BOOLEAN', 'key': 'setDefaultValue', 'value': 'false'},
    tpl('input', '{{DLV - ambiente}}'),
    {'type': 'LIST', 'key': 'map', 'list': [{'type': 'MAP', 'map': [tpl('key', k), tpl('value', 'internal')]} for k in ('teste', 'local')]}]))

# ---------- acionadores ----------
EVENTOS = {
    'generate_lead': ['form_name', 'lead_tipo', 'lead_verba', 'lead_inicio'],
    'support_request': ['form_name', 'support_uso', 'support_assunto'],
    'app_store_click': ['store', 'link_local'],
    'painel_click': ['painel_destino', 'link_local'],
}
acionadores, gatilho = [], {}
for ev in EVENTOS:
    t = base('triggerId', f'Evento - {ev}', type='CUSTOM_EVENT', customEventFilter=[{
        'type': 'EQUALS', 'parameter': [tpl('arg0', '{{_event}}'), tpl('arg1', ev)]}])
    acionadores.append(t)
    gatilho[ev] = t['triggerId']

# ---------- tags ----------
cfg = tabela([('traffic_type', '{{GA4 - traffic_type}}')])
cfg['key'] = 'configSettingsTable'
tags = [base('tagId', 'GA4 - Google tag', type='googtag', parameter=[tpl('tagId', '{{GA4 - ID}}'), cfg],
             firingTriggerId=[ALL_PAGES], tagFiringOption='ONCE_PER_EVENT', consentSettings=CONSENT)]
for ev, params in EVENTOS.items():
    tab = tabela([(p, '{{DLV - ' + p + '}}') for p in params] + [('traffic_type', '{{GA4 - traffic_type}}')])
    tab['key'] = 'eventSettingsTable'
    tags.append(base('tagId', f'GA4 - {ev}', type='gaawe', parameter=[
        {'type': 'BOOLEAN', 'key': 'sendEcommerceData', 'value': 'false'},
        tpl('eventName', ev), tpl('measurementIdOverride', '{{GA4 - ID}}'), tab],
        firingTriggerId=[gatilho[ev]], tagFiringOption='ONCE_PER_EVENT', consentSettings=CONSENT))

out = {
    'exportFormatVersion': 2,
    'exportTime': datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S'),
    'containerVersion': {
        'path': f'accounts/{ACC}/containers/{CON}/versions/0',
        'accountId': ACC, 'containerId': CON, 'containerVersionId': '0',
        'container': {'path': f'accounts/{ACC}/containers/{CON}', 'accountId': ACC, 'containerId': CON,
                      'name': 'HypeApp site', 'publicId': 'GTM-XXXXXXX', 'usageContext': ['WEB']},
        'tag': tags, 'trigger': acionadores, 'variable': variaveis,
        'builtInVariable': [{'accountId': ACC, 'containerId': CON, 'type': t, 'name': n} for t, n in
                            [('PAGE_URL', 'Page URL'), ('PAGE_HOSTNAME', 'Page Hostname'), ('PAGE_PATH', 'Page Path'),
                             ('REFERRER', 'Referrer'), ('EVENT', 'Event')]],
    },
}
dest = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'gtm-container-hypeapp.json')
json.dump(out, open(dest, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print('ok', dest, f'({len(tags)} tags, {len(acionadores)} acionadores, {len(variaveis)} variáveis)')
