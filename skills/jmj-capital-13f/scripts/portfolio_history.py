#!/usr/bin/env python3
"""Immutable local snapshots and precision-preserving portfolio comparisons."""
import argparse, hashlib, json, re
from datetime import datetime
from decimal import Decimal, getcontext
from pathlib import Path
getcontext().prec = 50
D = Decimal

def read(path):
    return json.loads(Path(path).read_text())

def instant(s):
    s = s.replace(' UTC', '+00:00').replace(' ', 'T')
    s = re.sub(r'\.(\d+)', lambda m: '.' + m[1][:6].ljust(6, '0'), s)
    return datetime.fromisoformat(s.replace('Z', '+00:00'))

def validate(s):
    if s.get('schema_version') != 1 or not s.get('complete'):
        raise ValueError('Only complete schema-version-1 snapshots are comparable')
    if not re.fullmatch(r'[A-Za-z0-9_-]+', s['id']):
        raise ValueError('Unsafe snapshot ID')
    if instant(s['captured_end']) < instant(s['captured_start']):
        raise ValueError('Capture times reversed')
    refs = s['scope_refs']
    if len(refs) != len(set(refs)) or set(refs) != {a['account_ref'] for a in s['accounts']}:
        raise ValueError('Account scope does not match captured accounts')
    seen = set()
    for h in s['holdings']:
        token = (h['account_ref'], h['key'])
        if token in seen or h['account_ref'] not in refs:
            raise ValueError('Duplicate holding or unexpected account')
        seen.add(token)
        if h['asset_type'] not in ('equity', 'crypto', 'option'):
            raise ValueError('Unsupported asset type; reconcile before comparison')
        for field in ('quantity', 'price'):
            if not isinstance(h[field], str) or not D(h[field]).is_finite():
                raise ValueError('Use finite decimal strings for quantities and prices')
        if D(h['price']) < 0:
            raise ValueError('Negative quote')
        if h['asset_type'] == 'option':
            if h['position_type'] not in ('long', 'short') or D(h['multiplier']) <= 0 or D(h['quantity']) < 0:
                raise ValueError('Invalid option quantity/type/multiplier')
        instant(h['price_at'])
    return s

def aggregate(s):
    validate(s)
    result = {}
    for h in s['holdings']:
        qty = D(h['quantity'])
        if h['asset_type'] == 'option' and h['position_type'] == 'short':
            qty = -qty
        mult = D(h.get('multiplier', '1'))
        key = h['key']
        if key not in result:
            result[key] = dict(key=key, symbol=h['symbol'], asset_type=h['asset_type'],
                               quantity=D(0), value=D(0), prices=[], sources=set())
            if h['asset_type']=='option':
                result[key]['expiration']=h.get('expiration','')
                result[key]['position_type']=h['position_type']
        row = result[key]
        row['quantity'] += qty
        row['value'] += qty * D(h['price']) * mult
        row['prices'].append((instant(h['price_at']), D(h['price']), h['price_at']))
        row['sources'].add(h['price_source'])
    cash = sum((D(a['portfolio']['cash']) for a in s['accounts']), D(0))
    result['cash:USD'] = dict(key='cash:USD', symbol='Cash', asset_type='cash', quantity=None,
                              value=cash, prices=[], sources=set())
    total = sum((r['value'] for r in result.values()), D(0))
    if total <= 0:
        raise ValueError('Net portfolio value must be positive')
    for r in result.values():
        r['allocation'] = 100 * r['value'] / total
        r['price'] = max(r['prices'])[1] if r['prices'] else None
        r['price_at'] = max(r['prices'])[2] if r['prices'] else None
    broker = sum((D(a['portfolio']['total_value']) for a in s['accounts']), D(0))
    return result, total, 100 * (total - broker) / broker if broker else None

def save(s, history):
    rows, total, gap = aggregate(s)
    s = dict(s)
    s['calculation'] = {'net_value':str(total), 'reconciliation_gap_pct':str(gap),
        'aggregate_holdings':[{k:(str(v) if isinstance(v,D) else v) for k,v in r.items()
                              if k not in ('prices','sources')} for r in rows.values()]}
    history = Path(history); archive = history/'snapshots'; archive.mkdir(parents=True,exist_ok=True)
    content = json.dumps(s,indent=2,sort_keys=True)+'\n'
    target = archive/(s['id']+'.json')
    if target.exists():
        if target.read_text() != content:
            archived = read(target)
            source_now = dict(s); source_now.pop('calculation',None)
            source_old = dict(archived); source_old.pop('calculation',None)
            if source_now != source_old:
                raise ValueError('Snapshot ID already exists with different source content')
            content = target.read_text()
    else:
        with target.open('x') as f:f.write(content)
    pointer = {'snapshot':str(target.relative_to(history)), 'id':s['id'],
               'captured_end':s['captured_end'], 'scope_refs':s['scope_refs'],
               'sha256':hashlib.sha256(content.encode()).hexdigest(), 'role':s.get('role','')}
    old = read(history/'latest.json') if (history/'latest.json').exists() else None
    if old and instant(old['captured_end']) > instant(s['captured_end']):
        raise ValueError('Archived older snapshot; refusing to move forward pointer backward')
    tmp = history/'latest.tmp'; tmp.write_text(json.dumps(pointer,indent=2)+'\n');tmp.replace(history/'latest.json')
    return target

def compare(current, baseline, catalog, threshold=D('.04')):
    now,_,gap = aggregate(current); old,_,_ = aggregate(baseline)
    if set(current['scope_refs']) != set(baseline['scope_refs']):
        raise ValueError('Scope changed: reconcile accounts before comparison')
    if instant(current['captured_end']) < instant(baseline['captured_end']):
        raise ValueError('Current snapshot predates baseline')
    factors={}; flows={}
    for e in current.get('events',[]):
        key=e['key'];factor=D(str(e.get('split_factor','1')))
        if factor <= 0:raise ValueError('Split factor must be positive')
        factors[key]=factors.get(key,D(1))*factor
        flows[key]=flows.get(key,D(0))+D(str(e.get('nontrade_quantity_delta','0')))
    rows=[];excluded=[];exited=[]
    for key in sorted(set(now)|set(old)):
        n=now.get(key);b=old.get(key);model=n or b
        meta=catalog.get(key, {})
        alloc=n['allocation'] if n else D(0);prior=b['allocation'] if b else D(0)
        q=n['quantity'] if n else D(0);bq=b['quantity'] if b else D(0)
        factor=factors.get(key,D(1));normalized=bq*factor if bq is not None else None
        iscash=model['asset_type']=='cash'
        delta=q-normalized if not iscash else None
        pct=100*delta/abs(normalized) if normalized else None
        ret=None;reason='No starting market price'
        if iscash:reason='Not applicable'
        elif n and b and b['price'] and n['price'] and len(b['sources'])==len(n['sources'])==1 and b['sources']==n['sources']:
            ret=100*(n['price']/(b['price']/factor)-1);reason=None
        elif n and b and b['sources']!=n['sources']:reason='Price bases differ'
        status='Cash movement' if iscash else 'New' if not normalized and q else 'No longer held' if not q and normalized else 'Unchanged' if not delta else 'Changed'
        default_display=model['symbol']+' option' if model['asset_type']=='option' else model['symbol']
        default_name=(model.get('position_type','').title()+' option · '+model.get('expiration','')) if model['asset_type']=='option' else model['symbol']
        r={'key':key,'symbol':model['symbol'],'asset_type':model['asset_type'],
           'display':meta.get('display',default_display),'name':meta.get('name',default_name),
           'logo':meta.get('logo',model['symbol']),'badge':meta.get('badge',False),
           'allocation':float(alloc),'baseline':float(prior),'pp':float(alloc-prior),
           'quantity':str(q) if q is not None else None,'baseline_quantity':str(normalized) if normalized is not None else None,
           'quantity_delta':str(delta) if delta is not None else None,
           'position_change_pct':float(pct) if pct is not None else None,
           'position_status':status,'position_cause_verified':bool(current.get('events_complete')),
           'trade_quantity_delta':str(delta-flows.get(key,D(0))) if delta is not None and current.get('events_complete') and current.get('trades_reconciled') else None,
           'price_return_pct':float(ret) if ret is not None else None,'return_reason':reason,
           'price_source':list(model['sources'])[0] if len(model['sources'])==1 else 'Mixed',
           'baseline_price_at':b['price_at'] if b else None,'current_price_at':n['price_at'] if n else None}
        if status=='No longer held' and abs(prior)>=threshold:exited.append(r)
        elif abs(alloc)>=threshold:rows.append(r)
        else:excluded.append(r)
    rows.sort(key=lambda r:r['allocation'],reverse=True)
    dt=instant(current['captured_end']);bd=instant(baseline['captured_end'])
    from zoneinfo import ZoneInfo
    local=dt.astimezone(ZoneInfo(current['timezone']));blocal=bd.astimezone(ZoneInfo(current['timezone']))
    return {'schema_version':1,'current_id':current['id'],'baseline_id':baseline['id'],
            'date':f'{local.month}/{local.day}/{str(local.year)[-2:]}',
            'baseline_label':blocal.strftime('%b %d, %Y'),'current_label':local.strftime('%b %d, %Y'),
            'pullTime':local.strftime('%b %d, %Y %I:%M %p %Z'),'scope':current['scope'],
            'return_period':f'{blocal:%b %d %I:%M %p} → {local:%b %d %I:%M %p %Z}',
            'rows':rows,'excluded':excluded,'exited':exited,'threshold':float(threshold),
            'position_note':'Net quantity changes; causes unverified' if not current.get('events_complete') else 'Net quantity changes; nontrade flows reviewed',
            'reconciliation_gap_pct':float(gap) if gap is not None else None}

def main():
    p=argparse.ArgumentParser();sub=p.add_subparsers(dest='command',required=True)
    a=sub.add_parser('save');a.add_argument('input');a.add_argument('--history',required=True)
    a=sub.add_parser('compare');a.add_argument('current');a.add_argument('baseline');a.add_argument('--catalog',required=True);a.add_argument('--out',required=True);a.add_argument('--threshold',default='.04')
    a=p.parse_args()
    if a.command=='save':print(save(read(a.input),a.history))
    else:
        dataset=compare(read(a.current),read(a.baseline),read(a.catalog),D(a.threshold))
        Path(a.out).parent.mkdir(parents=True,exist_ok=True);Path(a.out).write_text(json.dumps(dataset,indent=2)+'\n')
        print(f"Compared {len(dataset['rows'])} displayed holdings, {len(dataset['excluded'])} excluded")

if __name__=='__main__':main()
