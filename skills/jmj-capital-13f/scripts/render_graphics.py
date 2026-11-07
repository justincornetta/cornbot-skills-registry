#!/usr/bin/env python3
"""Render approved JMJ layouts from a sanitized comparison dataset."""
import json, sys
from pathlib import Path
from graphics_core import text as T, line as L, logo as LOGO, logo_brand as BRAND, signed as SIGNED, start as START, crown, point, wedge, spread, COLORS
G='#e8b153';W='#f4f1e9';M='#aeb9c6';GREEN='#80c2ac';RED='#d99493';SLATE='#6f8499'

def rect(x,y,w,h,fill,stroke='none',rx=12):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}"/>'

def footer(y,w,lines):
    o=L(70,y,w-70,y,width=1.2)
    for i,s in enumerate(lines):o+=T(72,y+43+i*32,s,21,M)
    return o

def comparison(d):
    rows=d['rows'];w=2100;end=502+len(rows)*102
    exits=d.get('exited',[]);fy=end+(100 if exits else 40);h=fy+225
    o=START(w,h)+T(70,64,'ALLOCATION & ASSET PERFORMANCE',20,G,spacing=2.3)
    o+=T(70,148,'JMJ Capital Portfolio',76,serif=True)+T(72,210,'as of '+d['date'],40,serif=True)
    o+=T(72,263,'Portfolio weight, market price return, and net position change—each shown separately.',25,M)
    o+=BRAND(w-150,158,.87,True)+L(70,308,w-70,308,width=1.4)
    o+=rect(72,335,w-142,78,'#102638',rx=10)
    o+=rect(95,365,45,8,SLATE,rx=4)+T(155,379,d['baseline_label']+' allocation',23,M)
    o+=rect(535,365,45,8,'url(#gold)',rx=4)+T(595,379,d['current_label']+' allocation',23,G)
    o+=T(w-100,380,'Price return measures the asset, not your personal P&L',23,M,anchor='end')
    o+=T(72,465,'INVESTMENT',23,G)+T(935,465,'PORTFOLIO WEIGHT',23,G,anchor='middle')
    o+=T(1380,454,'Δ ALLOCATION',23,G,anchor='end')+T(1380,483,'percentage points',18,M,anchor='end')
    o+=T(1690,454,'PRICE RETURN',23,G,anchor='end')+T(1690,483,'over the comparison period',18,M,anchor='end')
    o+=T(2028,454,'NET POSITION CHANGE',23,G,anchor='end')+T(2028,483,'shares / coins / contracts',18,M,anchor='end')
    maxval=max(36,max(abs(r['allocation']) for r in rows),max(abs(r['baseline']) for r in rows))
    for i,r in enumerate(rows):
        y=502+i*102;o+=L(70,y-5,w-70,y-5,'#526a80',1,.3)
        o+=T(105,y+52,i+1,29,G,anchor='middle')+LOGO(r,153,y+13,74,65)
        o+=T(252,y+41,r['display'],30,W,weight=700)+T(252,y+73,r['name'],min(21,330/max(1,len(r['name']))*1.8),M)
        for dy,v,col in [(24,r['baseline'],SLATE),(56,r['allocation'],'url(#gold)')]:
            o+=rect(647,y+dy,475,10,'#172e40',rx=5)
            if v:o+=rect(647,y+dy,max(2,475*abs(v)/maxval),10,col,rx=5)
            o+=T(1210,y+dy+13,f'{v:.2f}%',23,M if dy==24 else G,anchor='end')
        o+=T(1380,y+55,SIGNED(r['pp'],' pp'),29,W,anchor='end')
        ret=r.get('price_return_pct')
        if ret is not None:o+=T(1690,y+55,SIGNED(ret,'%'),32,GREEN if ret>=0 else RED,anchor='end')
        else:
            o+=T(1690,y+38,'—',30,M,anchor='end')
            reason=r.get('return_reason') or 'Unavailable'
            o+=T(1690,y+70,reason,18,M,anchor='end')
        pct=r.get('position_change_pct');status=r.get('position_status','Pending')
        label=SIGNED(pct,'%') if pct is not None else status
        o+=rect(1835,y+28,193,42,'#152b3d',stroke='#2d465a',rx=21)
        o+=T(1931,y+57,label,21,GREEN if pct is not None and pct>0 else RED if pct is not None and pct<0 else M,anchor='middle')
    if exits:
        if len(exits)>5:raise ValueError('Adapt the exited-holdings panel for more than five exits')
        o+=T(72,end+48,'NO LONGER HELD',21,G,spacing=1)
        labels='  ·  '.join(f"{r['display']} {r['baseline']:.2f}% → 0.00%" for r in exits)
        o+=T(385,end+48,labels,25,W)+T(2028,end+48,'Causes unverified',21,M,anchor='end')
    o+=footer(fy,w,[
        'Source: '+d.get('sources','Robinhood MCP (holdings and timestamped market quotes).'),
        'Price return: '+d['return_period']+'; excludes distributions and staking income.',
        'Full-period asset performance, regardless of when you traded. Cash: not applicable.',
        d['scope']+f"; below {d['threshold']:.2f}% omitted; "+d.get('position_note','Position quantities unverified')+'.',
        'pp = percentage points. Net quantity changes can include trades, transfers and rewards; unchanged does not mean no trades.'
    ])
    return o+'</svg>'

def donut(d):
    positive=[r for r in d['rows'] if r['allocation']>0]
    negatives=[r for r in d['rows']+d.get('excluded',[]) if r['allocation']<0]
    if len(positive)>22:raise ValueError('Adapt donut callout strips for more than 22 positive labels')
    if not positive:raise ValueError('No positive material holdings')
    geometry_total=sum(r['allocation'] for r in d['rows']+d.get('excluded',[]) if r['allocation']>0) if negatives else 100
    w=h=1800;o=START(w,h)
    o+=L(285,87,828,87,width=1.4)+L(972,87,1515,87,width=1.4)+crown(900,82,.7)
    o+=T(900,194,'JMJ Capital 13F',96,anchor='middle',serif=True)+T(900,262,'as of '+d['date'],46,anchor='middle',serif=True)
    o+=L(285,298,1515,298,width=1.4)
    cx=920;cy=1060;ro=530;ri=245;a=-90;labels=[]
    for i,r in enumerate(positive):
        b=a+r['allocation']/geometry_total*360;o+=wedge(cx,cy,ro,ri,a,b,COLORS[i%len(COLORS)])
        mid=(a+b)/2;ax,ay=point(cx,cy,ro-7,mid);ex,ey=point(cx,cy,ro+24,mid)
        labels.append(dict(row=r,ax=ax,ay=ay,ex=ex,ey=ey,left=ax<cx));a=b
    if a<270-1e-9:o+=wedge(cx,cy,ro,ri,a,270,'#223849')
    top=labels[10:];left=labels[2:10];right=labels[:2]
    for t in left:t['left']=True
    for t in right:t['left']=False
    spread(left,565,1450,114);spread(right,760,1490,100)
    gap=min(148,1185/max(1,len(top)-1))
    for i,t in enumerate(top):
        x=435+i*gap
        o+=LOGO(t['row'],x-37,344,74,57)+T(x,433,t['row']['display'],27,anchor='middle',weight=700)
        o+=T(x,470,f"{t['row']['allocation']:.2f}%",29,G,anchor='middle')
        o+=f'<polyline points="{t["ax"]},{t["ay"]} {t["ex"]},{t["ey"]} {x},493 {x},482" fill="none" stroke="{W}" stroke-width="1.4"/><circle cx="{t["ax"]}" cy="{t["ay"]}" r="4" fill="{W}"/>'
    for t in left+right:
        y=t['ly'];endx=320 if t['left'] else 1525;x=55 if t['left'] else 1548
        o+=f'<polyline points="{t["ax"]},{t["ay"]} {t["ex"]},{t["ey"]} {endx},{y} {endx-24 if t["left"] else endx+12},{y}" fill="none" stroke="{W}" stroke-width="1.4"/><circle cx="{t["ax"]}" cy="{t["ay"]}" r="5" fill="{W}"/>'
        o+=LOGO(t['row'],x,y-42,76,72)+T(x+91,y-10,t['row']['display'],31,weight=700)+T(x+91,y+31,f"{t['row']['allocation']:.2f}%",36,G)
    o+=BRAND(cx,cy+5,2.2)+T(cx,cy+90,'POSITIVE-ASSET COMPOSITION' if negatives else 'PORTFOLIO ALLOCATION',18,G,anchor='middle',spacing=2)
    o+=L(230,1620,1570,1620,width=1.2)+T(900,1665,f"{len(d['rows'])} DISPLAYED HOLDINGS",29,G,anchor='middle',spacing=2)
    o+=T(900,1700,d['pullTime']+' • '+d['scope'],20,M,anchor='middle')
    if negatives:
        named=[r for r in negatives if abs(r['allocation'])>=d['threshold']]
        disclosure='; '.join(f"{r['display']} {r['allocation']:.2f}%" for r in named)
        if len(disclosure)>75:raise ValueError('Adapt the negative-exposure panel for more holdings')
        o+=T(900,1732,disclosure+'. Labels use net weights; arcs scale positive assets.',20,M,anchor='middle')
    else:o+=T(900,1732,f"Below {d['threshold']:.2f}% omitted from labels; denominator includes every position.",20,M,anchor='middle')
    o+=T(900,1765,d.get('sources','Robinhood MCP • No monetary amounts • Net cash'),20,M,anchor='middle')
    return o+'</svg>'

def main():
    if len(sys.argv)!=3:raise SystemExit('Usage: render_graphics.py DATASET OUTPUT_DIRECTORY')
    d=json.loads(Path(sys.argv[1]).read_text());out=Path(sys.argv[2]);out.mkdir(parents=True,exist_ok=True)
    allrows=d['rows']+d.get('excluded',[])
    if abs(sum(r['allocation'] for r in allrows)-100)>1e-6:raise ValueError('Allocations must reconcile to 100% including signed exposures')
    for r in d['rows']:
        if abs(r['pp']-(r['allocation']-r['baseline']))>1e-8:raise ValueError('Allocation change mismatch')
    for name,fn in [('jmj-capital-donut',donut),('jmj-capital-comparison',comparison)]:
        s=fn(d)
        if '$' in s:raise ValueError('Unexpected currency symbol')
        (out/(name+'.svg')).write_text(s)
    (out/'chart-data.json').write_text(json.dumps(d,indent=2))
    print('Rendered both approved-style SVGs.')

if __name__=='__main__':main()
