#!/usr/bin/env python3
"""visualize.py — Progress visualizer.
Usage:
  python3 visualize.py            # Terminal summary + generate dashboard.html
  python3 visualize.py --watch    # Live terminal (refreshes every 5s)
  python3 visualize.py --terminal # Terminal only, no HTML
"""
import json, os, sys, time, re

LOG_FILE = "results.log"
SPARKS = "▁▂▃▄▅▆▇█"

def parse_log():
    exps = []
    if not os.path.exists(LOG_FILE): return exps
    with open(LOG_FILE) as f:
        for i, line in enumerate(f):
            parts = [p.strip() for p in line.split("|")]
            if len(parts) < 4: continue
            try:
                ts = parts[0]
                sc = float(re.search(r"score=([-\d.]+)", parts[1]).group(1))
                bl = float(re.search(r"baseline=([-\d.]+)", parts[2]).group(1))
                st = "kept" if "KEPT" in parts[3] else "reverted"
                exps.append({"i": i+1, "ts": ts, "score": sc, "baseline": bl, "status": st})
            except: continue
    return exps

def spark(vals, w=50):
    if not vals: return ""
    mn, mx = min(vals), max(vals)
    r = mx - mn or 1
    return "".join(SPARKS[min(int((v-mn)/r*7),7)] for v in vals[-w:])

def terminal(exps):
    if not exps: print("\n  No experiments yet.\n"); return
    scores = [e["score"] for e in exps]
    kept = [e for e in exps if e["status"]=="kept"]
    best = -999999
    bests = []
    for e in exps:
        if e["status"]=="kept": best = e["score"]
        bests.append(best)
    G,R,C,B,D,X = "\033[32m","\033[31m","\033[36m","\033[1m","\033[2m","\033[0m"
    print(f"\n  {B}{C}◉ EVOLUTION ARENA{X}  {D}autoresearch progress{X}")
    print(f"  {D}{'─'*52}{X}\n")
    print(f"  {D}experiments{X}  {B}{len(exps)}{X}    {G}kept {len(kept)}{X}  "
          f"{R}reverted {len(exps)-len(kept)}{X}  {D}({len(kept)/len(exps)*100:.0f}%){X}")
    print(f"  {D}best score{X}   {B}{C}{best:.1f}{X}\n")
    print(f"  {D}all scores{X}   {spark(scores)}")
    print(f"  {G}best ratchet{X}  {spark(bests)}\n")
    print(f"  {D}recent:{X}")
    for e in exps[-8:]:
        d = e["score"]-e["baseline"]; ds = f"{'+' if d>0 else ''}{d:.1f}"
        dc = G if d>0 else R
        mk = f"{G}✓ KEPT{X}    " if e["status"]=="kept" else f"{R}✗ reverted{X}"
        print(f"    {D}#{e['i']:>3}{X}  score={e['score']:>6.1f}  {dc}{ds:>6}{X}  {mk}")
    print()

def gen_html(exps):
    scores = [e["score"] for e in exps]
    best = -999999; bests = []
    for e in exps:
        if e["status"]=="kept": best=e["score"]
        bests.append(best)
    kept = sum(1 for e in exps if e["status"]=="kept")
    cfg = "{}"
    if os.path.exists("config.json"):
        with open("config.json") as f: cfg = f.read()
    return f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>Evolution Arena Dashboard</title>
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700;800&display=swap');
*{{margin:0;padding:0;box-sizing:border-box}}
:root{{--bg:#0d1117;--bg2:#111827;--bd:#1e293b;--tx:#c9d1d9;--dm:#4b5563;--gn:#4ade80;--rd:#f87171;--cy:#38bdf8;--yl:#fbbf24}}
body{{font-family:'JetBrains Mono',monospace;background:var(--bg);color:var(--tx);padding:24px;font-size:13px}}
.hdr{{display:flex;align-items:center;justify-content:space-between;margin-bottom:28px;flex-wrap:wrap;gap:16px}}
.logo{{font-size:28px;color:var(--cy)}}
.title{{font-size:18px;font-weight:800;letter-spacing:.06em;color:#e6edf3}}
.sub{{font-size:11px;color:var(--dm)}}
.stats{{display:flex;gap:16px;flex-wrap:wrap}}
.st{{text-align:center;padding:10px 18px;background:var(--bg2);border:1px solid var(--bd);border-radius:8px}}
.sl{{font-size:9px;color:var(--dm);letter-spacing:.1em;text-transform:uppercase;margin-bottom:2px}}
.sv{{font-size:26px;font-weight:800;color:#e6edf3}}
.sv.g{{color:var(--gn)}}.sv.r{{color:var(--rd)}}.sv.c{{color:var(--cy)}}
.grid{{display:grid;grid-template-columns:1fr 1fr;gap:20px}}
@media(max-width:900px){{.grid{{grid-template-columns:1fr}}}}
.card{{background:var(--bg2);border:1px solid var(--bd);border-radius:8px;padding:20px}}
.ct{{font-size:10px;color:var(--dm);letter-spacing:.1em;text-transform:uppercase;margin-bottom:14px;font-weight:700}}
.full{{grid-column:1/-1}}
canvas{{width:100%!important;height:280px!important}}
.leg{{display:flex;gap:14px;margin-top:8px;font-size:10px;color:var(--dm)}}
.dot{{width:8px;height:8px;border-radius:50%;display:inline-block}}
.dot.g{{background:var(--gn)}}.dot.r{{background:var(--rd)}}
.ls{{width:16px;height:2px;display:inline-block;background:var(--gn);border-radius:1px}}
.el{{max-height:400px;overflow-y:auto}}
.er{{display:flex;align-items:center;gap:10px;padding:6px 0;border-bottom:1px solid var(--bd);font-size:11px}}
.ei{{color:var(--dm);width:30px;text-align:right}}.es{{font-weight:700;width:56px}}
.ed{{width:52px;text-align:right}}
.eb{{padding:2px 8px;border-radius:4px;font-size:10px;font-weight:600}}
.eb.k{{background:#4ade8015;color:var(--gn)}}.eb.v{{background:#f8717115;color:var(--rd)}}
.et{{color:var(--dm);font-size:10px;margin-left:auto}}
.cb{{background:var(--bg);border:1px solid var(--bd);border-radius:6px;padding:14px;font-size:12px;line-height:1.8}}
.ck{{color:var(--cy)}}.cv{{color:var(--yl);font-weight:600}}
.ft{{text-align:center;color:var(--dm);font-size:10px;margin-top:28px;padding-top:14px;border-top:1px solid var(--bd)}}
</style></head><body>
<div class="hdr"><div style="display:flex;align-items:center;gap:12px">
<span class="logo">&#9673;</span><div><div class="title">EVOLUTION ARENA</div><div class="sub">autoresearch dashboard</div></div></div>
<div class="stats">
<div class="st"><div class="sl">Experiments</div><div class="sv">{len(exps)}</div></div>
<div class="st"><div class="sl">Kept</div><div class="sv g">{kept}</div></div>
<div class="st"><div class="sl">Reverted</div><div class="sv r">{len(exps)-kept}</div></div>
<div class="st"><div class="sl">Best Score</div><div class="sv c">{best:.1f}</div></div>
<div class="st"><div class="sl">Keep Rate</div><div class="sv">{kept/max(len(exps),1)*100:.0f}%</div></div>
</div></div>
<div class="grid">
<div class="card full"><div class="ct">Score Ratchet</div><canvas id="c"></canvas>
<div class="leg"><span><span class="dot g"></span> kept</span><span><span class="dot r"></span> reverted</span><span><span class="ls"></span> best</span></div></div>
<div class="card"><div class="ct">Experiment History</div><div class="el" id="el"></div></div>
<div class="card"><div class="ct">Current Best Config</div><div class="cb" id="cb"></div></div>
</div>
<div class="ft">Generated by visualize.py</div>
<script>
const S={json.dumps(scores)},B={json.dumps(bests)},E={json.dumps(exps)},C={cfg};
function draw(){{const c=document.getElementById('c'),x=c.getContext('2d'),d=devicePixelRatio||1,r=c.getBoundingClientRect();
c.width=r.width*d;c.height=280*d;x.scale(d,d);const W=r.width,H=280,p={{t:20,r:20,b:30,l:50}},pW=W-p.l-p.r,pH=H-p.t-p.b;
if(!S.length){{x.fillStyle='#4b5563';x.font='12px JetBrains Mono';x.textAlign='center';x.fillText('No data',W/2,H/2);return}}
const mn=Math.min(...S,...B),mx=Math.max(...S,...B),rn=mx-mn||1,pd=rn*.1;
const X=i=>p.l+(i/Math.max(S.length-1,1))*pW;
const Y=v=>p.t+pH-((v-mn+pd)/(rn+pd*2))*pH;
x.strokeStyle='#1e293b';x.lineWidth=.5;
for(let i=0;i<5;i++){{const y=p.t+(i/4)*pH;x.beginPath();x.moveTo(p.l,y);x.lineTo(W-p.r,y);x.stroke();
x.fillStyle='#4b5563';x.font='9px JetBrains Mono';x.textAlign='right';x.fillText((mx+pd-(i/4)*(rn+pd*2)).toFixed(1),p.l-6,y+3)}}
x.strokeStyle='#ffffff10';x.lineWidth=1;x.beginPath();S.forEach((s,i)=>i?x.lineTo(X(i),Y(s)):x.moveTo(X(i),Y(s)));x.stroke();
x.strokeStyle='#4ade80';x.lineWidth=2;x.beginPath();B.forEach((s,i)=>i?x.lineTo(X(i),Y(s)):x.moveTo(X(i),Y(s)));x.stroke();
E.forEach((e,i)=>{{x.beginPath();x.arc(X(i),Y(e.score),4,0,Math.PI*2);x.fillStyle=e.status==='kept'?'#4ade80':'#f87171';x.fill()}})}}
document.getElementById('el').innerHTML=[...E].reverse().map(e=>{{
const d=e.score-e.baseline,ds=(d>0?'+':'')+d.toFixed(1),dc=d>0?'var(--gn)':'var(--rd)';
return`<div class="er"><span class="ei">#${{e.i}}</span><span class="es">${{e.score.toFixed(1)}}</span><span class="ed" style="color:${{dc}}">${{ds}}</span><span class="eb ${{e.status==='kept'?'k':'v'}}">${{e.status}}</span><span class="et">${{e.ts}}</span></div>`}}).join('');
document.getElementById('cb').innerHTML=Object.entries(C).map(([k,v])=>`<span class="ck">${{k}}</span>: <span class="cv">${{JSON.stringify(v)}}</span>`).join('<br>');
draw();addEventListener('resize',draw);
</script></body></html>"""

def main():
    watch = "--watch" in sys.argv
    tonly = "--terminal" in sys.argv
    if watch:
        print("\033[2J\033[H",end="")
        try:
            while True:
                print("\033[H",end="")
                terminal(parse_log())
                time.sleep(5)
        except KeyboardInterrupt: print("\n  Stopped.\n"); return
    exps = parse_log()
    terminal(exps)
    if not tonly and exps:
        with open("dashboard.html","w") as f: f.write(gen_html(exps))
        print(f"  Dashboard -> dashboard.html")
        print(f"     file://{os.path.abspath('dashboard.html')}\n")

if __name__=="__main__": main()
