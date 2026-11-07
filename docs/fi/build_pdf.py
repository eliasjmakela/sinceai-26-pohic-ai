"""Builds doc/OpenWeight.html; render to PDF with headless Brave."""
cf  = [-1.37,-1.05,-0.52,0.24,0.66,1.01,1.35,1.69,2.03,2.38]
cum = [-1.37,-2.43,-2.94,-2.71,-2.05,-1.04,0.31,2.00,4.03,6.41]
W,H,L,T,B = 640,230,40,14,30
lo,hi = -3.5,7.0
y = lambda v: T + (hi-v)/(hi-lo)*(H-T-B)
bw = (W-L-10)/10
svg = [f'<svg viewBox="0 0 {W} {H}" class="chart" role="img" aria-label="Kassavirta ja kertymä">']
for g in (-2,0,2,4,6):
    svg.append(f'<line x1="{L}" x2="{W-6}" y1="{y(g):.1f}" y2="{y(g):.1f}" class="{"axis" if g==0 else "grid"}"/>'
               f'<text x="{L-6}" y="{y(g)+4:.1f}" class="tick" text-anchor="end">{g}</text>')
for i,v in enumerate(cf):
    x = L + i*bw + bw*0.22
    y1, y2 = (y(v), y(0)) if v>=0 else (y(0), y(v))
    svg.append(f'<rect x="{x:.1f}" y="{y1:.1f}" width="{bw*0.56:.1f}" height="{y2-y1:.1f}" class="{"pos" if v>=0 else "neg"}" rx="2"/>')
    svg.append(f'<text x="{L+i*bw+bw/2:.1f}" y="{H-10}" class="tick" text-anchor="middle">v{i+1}</text>')
pts = " ".join(f"{L+i*bw+bw/2:.1f},{y(v):.1f}" for i,v in enumerate(cum))
svg.append(f'<polyline points="{pts}" class="line"/>')
for i,v in enumerate(cum):
    svg.append(f'<circle cx="{L+i*bw+bw/2:.1f}" cy="{y(v):.1f}" r="3" class="dot"/>')
svg.append(f'<text x="{L+9*bw+bw/2-4:.1f}" y="{y(6.41)-8:.1f}" class="lbl" text-anchor="end">kertymä +6,4 M€</text>')
svg.append(f'<text x="{L+2*bw+bw/2:.1f}" y="{y(-2.94)+16:.1f}" class="lbl" text-anchor="middle">syvin −2,9 M€</text>')
svg.append('</svg>')
chart = "\n".join(svg)

html = open(__file__.replace("build_pdf.py","template.html"), encoding="utf-8").read().replace("{{CHART}}", chart)
open(__file__.replace("build_pdf.py","OpenWeight.html"),"w",encoding="utf-8").write(html)
print("ok")
