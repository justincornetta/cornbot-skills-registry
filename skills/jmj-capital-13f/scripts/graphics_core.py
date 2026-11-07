import json, math, base64, html
from pathlib import Path

ROOT=Path(__file__).resolve().parent.parent
GOLD='#e8b153'; WHITE='#f4f1e9'; MUTED='#aeb9c6'
COLORS=['#ff900d','#087653','#465b60','#d29a27','#70469d','#1b76bc','#436a9c','#acb7bd','#b82d30','#627082','#2e89b9','#00a488','#bc7a2d','#8762c2','#78a952','#398259','#59709c','#249fe1','#3266c8']

def text(x,y,s,size=30,color=WHITE,anchor='start',serif=False,weight=400,spacing=None):
    attrs=f' letter-spacing="{spacing}"' if spacing else ''
    return f'<text x="{x}" y="{y}" fill="{color}" font-family="{ "Georgia" if serif else "Arial" }" font-size="{size}" font-weight="{weight}" text-anchor="{anchor}"{attrs}>{html.escape(str(s))}</text>'

def line(x1,y1,x2,y2,color=GOLD,width=1,opacity=1):
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{width}" opacity="{opacity}"/>'

def crown(x,y,s=1):
    return f'<g transform="translate({x} {y}) scale({s})"><path d="M-30 10 L-36 -22 L-15 -8 L0 -38 L15 -8 L36 -22 L30 10 Z" fill="none" stroke="{GOLD}" stroke-width="4" stroke-linejoin="miter"/></g>'

def logo_brand(x,y,scale=1,circle=False):
    out=f'<g transform="translate({x} {y}) scale({scale})">'
    if circle:out+=f'<circle r="110" fill="#071828" stroke="{GOLD}" stroke-width="2"/>'
    out+=crown(0,-32,.38)+line(-88,-30,-26,-30)+line(26,-30,88,-30)
    out+=text(0,10,'JMJ CAPITAL',25,anchor='middle',serif=True,spacing=1.6)
    return out+'</g>'

def start(w,h):
    out=f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{w}" height="{h}" viewBox="0 0 {w} {h}">'
    out+='''<defs><radialGradient id="bg"><stop stop-color="#0b2135"/><stop offset="1" stop-color="#020e1c"/></radialGradient><linearGradient id="gold"><stop stop-color="#ffdc80"/><stop offset="1" stop-color="#bd8534"/></linearGradient><filter id="grain"><feTurbulence type="fractalNoise" baseFrequency=".65" numOctaves="3" stitchTiles="stitch"/><feColorMatrix type="saturate" values="0"/><feComponentTransfer><feFuncA type="linear" slope=".025"/></feComponentTransfer><feBlend in="SourceGraphic" mode="soft-light"/></filter></defs>'''
    out+=f'<rect width="{w}" height="{h}" fill="url(#bg)"/><rect width="{w}" height="{h}" filter="url(#grain)" fill="none"/>'
    for i in range(0,h+600,28):
        out+=f'<path d="M-150 {i} Q{w*.35} {i+300} {w+150} {i-320}" fill="none" stroke="#427083" stroke-width=".7" opacity=".04"/>'
    return out

def logo(row,x,y,w=80,h=76):
    sym=row['symbol'];key=row.get('logo',sym)
    if key=='Cash':
        return f'<g transform="translate({x} {y})"><rect x="6" y="22" width="66" height="37" rx="2" fill="#58915e" stroke="#aaca92" stroke-width="2"/><rect x="2" y="26" width="66" height="37" rx="2" fill="#447a4d" stroke="#c0d8a6" stroke-width="2"/><circle cx="35" cy="44" r="13" fill="#d4e5b5"/>'+text(35,51,'C',19,'#376541',anchor='middle',weight=700)+'</g>'
    f=ROOT/'assets'/'logos'/f'{key}-render.png'
    if not f.exists():f=ROOT/'assets'/'logos'/f'{key}.png'
    if not f.exists():raise ValueError(f'Missing logo {key}')
    # Asset proportions and color are retained; light badges preserve dark wordmarks.
    badge=row.get('badge',key in ['STIM','ETH-ETF','ETHB','HELP','ASST'])
    o=f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12" fill="#f3f2e9"/>' if badge else ''
    pad=5 if badge else 0
    raw=base64.b64encode(f.read_bytes()).decode()
    o+=f'<image x="{x+pad}" y="{y+pad}" width="{w-pad*2}" height="{h-pad*2}" preserveAspectRatio="xMidYMid meet" xlink:href="data:image/png;base64,{raw}"/>'
    return o

def signed(v,unit):
    if f'{abs(v):.2f}'=='0.00':return '0.00'+unit
    return ('+' if v>0 else '−' if v<0 else '')+f'{abs(v):.2f}'+unit

def point(cx,cy,r,a):
    t=math.radians(a);return (cx+r*math.cos(t),cy+r*math.sin(t))

def wedge(cx,cy,ro,ri,a,b,color):
    p1=point(cx,cy,ro,a);p2=point(cx,cy,ro,b);p3=point(cx,cy,ri,b);p4=point(cx,cy,ri,a)
    large=int(b-a>180)
    d=f'M{p1[0]} {p1[1]} A{ro} {ro} 0 {large} 1 {p2[0]} {p2[1]} L{p3[0]} {p3[1]} A{ri} {ri} 0 {large} 0 {p4[0]} {p4[1]} Z'
    return f'<path d="{d}" fill="{color}" stroke="#f2c570" stroke-width="1.8"/>'

def spread(items,lo,hi,gap):
    items.sort(key=lambda t:t['ay'])
    if not items:return
    for i,t in enumerate(items):t['ly']=max(t['ay'],lo if i==0 else items[i-1]['ly']+gap)
    if items[-1]['ly']>hi:
        items[-1]['ly']=hi
        for i in range(len(items)-2,-1,-1):items[i]['ly']=min(items[i]['ly'],items[i+1]['ly']-gap)
