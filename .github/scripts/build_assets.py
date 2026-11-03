#!/usr/bin/env python3
"""Regenerate the hand-designed SVGs in assets/. Run after editing the text below.

    python .github/scripts/build_assets.py
"""
from pathlib import Path
from xml.sax.saxutils import escape

from theme import BG, CYAN, LINE, MONO, MUTED, PANEL, PURPLE, REDUCED_MOTION, WHITE, AMBER

ASSETS = Path(__file__).resolve().parents[2] / "assets"

TERMINAL = [
    ("whoami", "Ankit Kumar · B.Tech CSE (AI/ML) at LPU · Batch of 2027"),
    ("cat focus.txt", "DSA in C++ · ML in Python · DevOps · security basics"),
    ("./prepare --placements 2027", "Solving problems, building projects, improving daily."),
]

SYSPULSE_NODES = [
    ("app/", "dashboard UI"),
    ("Dockerfile", "nginx image"),
    ("Jenkinsfile", "CI/CD stages"),
    ("k8s/", "deploy + HPA"),
    ("prometheus/", "alerts, Grafana"),
]


def terminal() -> str:
    width, row, top, cycle = 860, 44, 84, 16.0
    body, style = [], []
    clock = 0.9
    for index, (command, output) in enumerate(TERMINAL):
        cmd_y = top + index * row * 2
        out_y = cmd_y + row - 8
        typing = len(command) * 0.055
        start, end = clock / cycle * 100, (clock + typing) / cycle * 100
        shown = (clock + typing + 0.25) / cycle * 100
        # The loop starts on the finished screen, so a frozen first frame still reads.
        style.append(
            f"@keyframes t{index}{{0%,3%{{transform:translateX(780px)}}3.1%,{start:.2f}%{{transform:translateX(0)}}"
            f"{end:.2f}%,100%{{transform:translateX(780px)}}}}"
            f".t{index}{{animation:t{index} {cycle}s steps({len(command)},end) infinite}}"
            f"@keyframes o{index}{{0%,3%{{opacity:1}}3.5%,{end:.2f}%{{opacity:0}}{shown:.2f}%,100%{{opacity:1}}}}"
            f".o{index}{{animation:o{index} {cycle}s ease infinite}}"
        )
        body.append(
            f'<text x="34" y="{cmd_y}" fill="{CYAN}">$</text>'
            f'<text x="60" y="{cmd_y}" fill="{WHITE}">{escape(command)}</text>'
            f'<g clip-path="url(#w)"><rect class="t{index}" x="56" y="{cmd_y - 22}" width="790" height="30" fill="{BG}"/></g>'
            f'<text class="o{index}" x="60" y="{out_y}" fill="{MUTED}" font-size="19">{escape(output)}</text>'
        )
        clock += typing + 1.3
    height = top + len(TERMINAL) * row * 2 - 18
    dots = "".join(
        f'<circle cx="{30 + i * 22}" cy="24" r="7" fill="{color}"/>'
        for i, color in enumerate((PURPLE, CYAN, AMBER))
    )
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" role="img" aria-label="Terminal introduction: Ankit Kumar, B.Tech CSE AI/ML at LPU, Batch of 2027.">
<style>text{{font:20px {MONO}}}{''.join(style)}
.b{{animation:b 1.1s steps(1) infinite}}@keyframes b{{50%{{opacity:0}}}}{REDUCED_MOTION}</style>
<defs><clipPath id="w"><rect x="4" y="50" width="{width - 8}" height="{height - 54}"/></clipPath></defs>
<rect x="1" y="1" width="{width - 2}" height="{height - 2}" rx="14" fill="{BG}" stroke="{LINE}" stroke-width="2"/>
<path d="M1 48H{width - 1}" stroke="{LINE}" stroke-width="2"/>{dots}
<text x="{width / 2}" y="31" fill="{MUTED}" text-anchor="middle" font-size="16">ankit@profile: ~</text>
{''.join(body)}</svg>'''


def divider() -> str:
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 860 10" width="860" height="10" role="presentation">
<style>.p{{animation:p 5s linear infinite}}@keyframes p{{from{{transform:translateX(-260px)}}to{{transform:translateX(860px)}}}}{REDUCED_MOTION}</style>
<defs><linearGradient id="g"><stop offset="0" stop-color="{PURPLE}" stop-opacity="0"/><stop offset=".5" stop-color="{CYAN}"/><stop offset="1" stop-color="{PURPLE}" stop-opacity="0"/></linearGradient></defs>
<rect y="4" width="860" height="2" fill="{LINE}"/><rect class="p" y="3" width="260" height="4" rx="2" fill="url(#g)"/></svg>'''


def syspulse() -> str:
    node_w, gap, y = 157, 18.5, 26
    nodes = []
    for index, (path, label) in enumerate(SYSPULSE_NODES):
        x = index * (node_w + gap)
        delay = index * 0.5
        nodes.append(
            f'<rect x="{x + 1}" y="{y}" width="{node_w}" height="104" rx="12" fill="{PANEL}" stroke="{LINE}" stroke-width="2"/>'
            f'<rect class="n" style="animation-delay:{delay}s" x="{x + 1}" y="{y}" width="{node_w}" height="104" rx="12" fill="none" stroke="{CYAN}" stroke-width="2"/>'
            f'<text x="{x + 1 + node_w / 2}" y="{y + 46}" text-anchor="middle" fill="{WHITE}" font-size="19" font-weight="700">{path}</text>'
            f'<text x="{x + 1 + node_w / 2}" y="{y + 76}" text-anchor="middle" fill="{MUTED}" font-size="16">{label}</text>'
        )
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 860 280" width="860" height="280" role="img" aria-label="SysPulse repository layout: app, Dockerfile, Jenkinsfile, Kubernetes manifests and monitoring config, on Terraform infrastructure for AWS VPC, EKS and ECR.">
<style>text{{font-family:{MONO}}}
.f{{stroke-dasharray:14 16;animation:f 1.3s linear infinite}}@keyframes f{{to{{stroke-dashoffset:-30}}}}
.n{{opacity:0;animation:n 2.5s ease-in-out infinite}}@keyframes n{{0%,40%,100%{{opacity:0}}18%{{opacity:1}}}}{REDUCED_MOTION}</style>
<path class="f" d="M12 78H848" stroke="{CYAN}" stroke-width="3" fill="none"/>
<path class="f" d="M430 196V134" stroke="{PURPLE}" stroke-width="3" fill="none"/>
{''.join(nodes)}
<rect x="1" y="196" width="858" height="74" rx="12" fill="{PANEL}" stroke="{PURPLE}" stroke-width="2"/>
<text x="430" y="227" text-anchor="middle" fill="{WHITE}" font-size="19" font-weight="700">terraform/</text>
<text x="430" y="254" text-anchor="middle" fill="{MUTED}" font-size="16">AWS VPC · EKS · ECR · kube-prometheus-stack</text></svg>'''


if __name__ == "__main__":
    (ASSETS / "terminal.svg").write_text(terminal(), encoding="utf-8")
    (ASSETS / "divider.svg").write_text(divider(), encoding="utf-8")
    (ASSETS / "syspulse.svg").write_text(syspulse(), encoding="utf-8")
