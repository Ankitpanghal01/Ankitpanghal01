#!/usr/bin/env python3
"""Build live GitHub and LeetCode cards. Called by .github/workflows/profile-assets.yml.

    GITHUB_TOKEN=... python .github/scripts/build_stats.py dist
"""
import json
import os
import sys
import time
import urllib.request
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

from theme import AMBER, BG, CYAN, LINE, MONO, MUTED, PANEL, PURPLE, REDUCED_MOTION, SANS, WHITE

GITHUB_USER = "Ankitpanghal01"
LEETCODE_USER = "Ankitpanghal"

# Last verified numbers, shown only when LeetCode cannot be reached during a build.
LEETCODE_FALLBACK = {"All": 302, "Easy": 136, "Medium": 143, "Hard": 23, "as_of": "3 Nov 2026"}

HEAT = ["#161B22", "#3B1D6E", "#6D28D9", PURPLE, CYAN]
LANGUAGE_COLORS = [PURPLE, CYAN, AMBER, "#F472B6", "#34D399", "#60A5FA"]

GITHUB_QUERY = """
query ($login: String!) {
  user(login: $login) {
    repositories(first: 100, ownerAffiliations: OWNER, isFork: false, privacy: PUBLIC) {
      totalCount
      nodes {
        languages(first: 10, orderBy: {field: SIZE, direction: DESC}) {
          edges { size node { name } }
        }
      }
    }
    contributionsCollection {
      contributionCalendar {
        totalContributions
        weeks { contributionDays { date contributionCount } }
      }
    }
  }
}"""

LEETCODE_QUERY = """
query ($username: String!) {
  matchedUser(username: $username) {
    submitStatsGlobal { acSubmissionNum { difficulty count } }
  }
}"""


def post_json(url: str, payload: dict, headers: dict) -> dict:
    body = json.dumps(payload).encode()
    request = urllib.request.Request(
        url, body, {"Content-Type": "application/json", "User-Agent": "profile-assets", **headers}
    )
    for attempt in range(3):
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                return json.load(response)
        except OSError:
            if attempt == 2:
                raise
            time.sleep(4 * (attempt + 1))
    raise RuntimeError("unreachable")


def fetch_github() -> dict:
    token = os.environ["GITHUB_TOKEN"]
    result = post_json(
        "https://api.github.com/graphql",
        {"query": GITHUB_QUERY, "variables": {"login": GITHUB_USER}},
        {"Authorization": f"Bearer {token}"},
    )
    if result.get("errors"):
        raise RuntimeError(result["errors"])
    return result["data"]["user"]


def fetch_leetcode() -> dict:
    try:
        result = post_json(
            "https://leetcode.com/graphql",
            {"query": LEETCODE_QUERY, "variables": {"username": LEETCODE_USER}},
            {"Referer": "https://leetcode.com"},
        )
        rows = result["data"]["matchedUser"]["submitStatsGlobal"]["acSubmissionNum"]
        return {row["difficulty"]: row["count"] for row in rows}
    except (OSError, KeyError, TypeError, ValueError) as error:
        print(f"LeetCode unavailable, using fallback: {error}", file=sys.stderr)
        return LEETCODE_FALLBACK


def calendar_days(user: dict) -> list:
    weeks = user["contributionsCollection"]["contributionCalendar"]["weeks"]
    return [day for week in weeks for day in week["contributionDays"]]


def streaks(days: list, today: date) -> tuple:
    active = {date.fromisoformat(day["date"]) for day in days if day["contributionCount"]}
    longest = run = 0
    for day in sorted(active):
        run = run + 1 if day - timedelta(days=1) in active else 1
        longest = max(longest, run)
    # Today is still in progress, so an empty today does not break the streak.
    cursor = today if today in active else today - timedelta(days=1)
    current = 0
    while cursor in active:
        current += 1
        cursor -= timedelta(days=1)
    return current, longest


def language_shares(user: dict) -> list:
    totals = {}
    for repo in user["repositories"]["nodes"]:
        for edge in repo["languages"]["edges"]:
            totals[edge["node"]["name"]] = totals.get(edge["node"]["name"], 0) + edge["size"]
    grand_total = sum(totals.values()) or 1
    ranked = sorted(totals.items(), key=lambda item: item[1], reverse=True)[:6]
    return [(name, size / grand_total) for name, size in ranked]


def heat_level(count: int, peak: int) -> int:
    if not count:
        return 0
    return min(4, 1 + int(3 * count / max(peak, 1)))


def github_card(user: dict, today: date) -> str:
    days = calendar_days(user)
    current, longest = streaks(days, today)
    total = user["contributionsCollection"]["contributionCalendar"]["totalContributions"]
    active_days = sum(1 for day in days if day["contributionCount"])
    tiles = [
        (f"{total:,}", "contributions", PURPLE),
        (str(active_days), "active days", CYAN),
        (str(current), "current streak", AMBER),
        (str(longest), "longest streak", WHITE),
    ]
    tile_svg = "".join(
        f'<g>'
        f'<rect x="{index * 218.6 + 1:.1f}" y="1" width="202" height="118" rx="12" fill="{PANEL}" stroke="{LINE}" stroke-width="2"/>'
        f'<rect class="r" style="animation-delay:{index * 0.6:.1f}s" x="{index * 218.6 + 1:.1f}" y="1" width="202" height="118" rx="12" fill="none" stroke="{color}" stroke-width="2"/>'
        f'<text x="{index * 218.6 + 102:.1f}" y="60" text-anchor="middle" fill="{color}" class="v">{value}</text>'
        f'<text x="{index * 218.6 + 102:.1f}" y="95" text-anchor="middle" fill="{MUTED}" class="l">{label}</text></g>'
        for index, (value, label, color) in enumerate(tiles)
    )

    peak = max((day["contributionCount"] for day in days), default=0)
    cells = []
    first = date.fromisoformat(days[0]["date"]) if days else today
    offset = (first.weekday() + 1) % 7
    for index, day in enumerate(days):
        slot = index + offset
        column, row = slot // 7, slot % 7
        level = heat_level(day["contributionCount"], peak)
        pulse = ' class="h"' if level else ""
        delay = f' style="animation-delay:{column * 0.07:.2f}s"' if level else ""
        cells.append(
            f'<rect{pulse}{delay} x="{column * 15.9:.1f}" y="{row * 15.9:.1f}" width="13.4" height="13.4" rx="3" fill="{HEAT[level]}"/>'
        )

    languages = language_shares(user)
    x = 0.0
    bars, legend = [], []
    for index, (name, share) in enumerate(languages):
        width = 860 * share
        color = LANGUAGE_COLORS[index]
        bars.append(f'<rect x="{x:.1f}" width="{max(width - 2, 2):.1f}" height="16" fill="{color}"/>')
        x += width
        column, row = index % 3, index // 3
        legend.append(
            f'<circle cx="{column * 287 + 8}" cy="{row * 30 + 8}" r="7" fill="{color}"/>'
            f'<text x="{column * 287 + 24}" y="{row * 30 + 14}" fill="{WHITE}" class="l">{name} '
            f'<tspan fill="{MUTED}">{share * 100:.1f}%</tspan></text>'
        )
    rows = (len(languages) + 2) // 3
    height = 398 + rows * 30 + 26
    stamp = today.strftime("%-d %b %Y")
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 860 {height}" width="860" height="{height}" role="img" aria-label="GitHub activity: {total} contributions and {active_days} active days in the last year, current streak {current}, longest streak {longest}.">
<style>.v{{font:700 44px {MONO}}}.l{{font:18px {SANS}}}.t{{font:700 19px {MONO}}}.s{{font:15px {SANS}}}
.r{{opacity:0;animation:r 2.4s ease-in-out infinite}}@keyframes r{{0%,50%,100%{{opacity:0}}25%{{opacity:1}}}}
.h{{animation:h 4s ease-in-out infinite}}@keyframes h{{0%,100%{{opacity:.72}}50%{{opacity:1}}}}
.g{{animation:g 3.6s ease-in-out infinite}}@keyframes g{{from{{transform:translateX(-160px)}}to{{transform:translateX(900px)}}}}{REDUCED_MOTION}</style>
<defs><linearGradient id="sh"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".5" stop-color="#fff" stop-opacity=".55"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient><clipPath id="c"><rect width="860" height="16" rx="8"/></clipPath></defs>
{tile_svg}
<text y="162" fill="{CYAN}" class="t">last 12 months</text>
<g transform="translate(0 176)">{''.join(cells)}</g>
<text y="326" fill="{CYAN}" class="t">languages in public repos</text>
<g transform="translate(0 342)" clip-path="url(#c)">{''.join(bars)}<rect class="g" x="-120" width="120" height="16" fill="url(#sh)"/></g>
<g transform="translate(0 374)">{''.join(legend)}</g>
<text y="{height - 8}" fill="{MUTED}" class="s">Public GitHub activity · updated {stamp}</text></svg>'''


def leetcode_card(stats: dict, today: date) -> str:
    total = stats["All"]
    radius, circumference = 92, 2 * 3.14159265 * 92
    rows = [("Easy", CYAN), ("Medium", PURPLE), ("Hard", AMBER)]
    peak = max(stats[name] for name, _ in rows) or 1
    start, rings, bars = 0.0, [], []
    for index, (name, color) in enumerate(rows):
        arc = circumference * stats[name] / max(total, 1)
        rings.append(
            f'<circle r="{radius}" fill="none" stroke="{color}" stroke-width="20" '
            f'stroke-dasharray="{arc:.1f} {circumference:.1f}" stroke-dashoffset="{-start:.1f}" transform="rotate(-90)"/>'
        )
        start += arc
        y = index * 72
        width = 480 * stats[name] / peak
        bars.append(
            f'<text y="{y + 22}" fill="{WHITE}" class="l">{name}</text>'
            f'<text x="520" y="{y + 22}" text-anchor="end" fill="{color}" class="n">{stats[name]}</text>'
            f'<rect y="{y + 36}" width="520" height="12" rx="6" fill="{PANEL}"/>'
            f'<rect y="{y + 36}" width="{width:.1f}" height="12" rx="6" fill="{color}"/>'
            f'<g clip-path="url(#b{index})"><rect class="g" style="animation-delay:{index * 0.5:.1f}s" x="-120" y="{y + 36}" width="120" height="12" fill="url(#sh)"/></g>'
            f'<clipPath id="b{index}"><rect y="{y + 36}" width="{width:.1f}" height="12" rx="6"/></clipPath>'
        )
    note = f" · last verified {stats['as_of']}" if "as_of" in stats else f" · updated {today.strftime('%-d %b %Y')}"
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 860 280" width="860" height="280" role="img" aria-label="LeetCode: {total} problems solved. {stats['Easy']} easy, {stats['Medium']} medium, {stats['Hard']} hard.">
<style>.v{{font:700 50px {MONO}}}.l{{font:20px {SANS}}}.n{{font:700 22px {MONO}}}.s{{font:15px {SANS}}}
.o{{animation:o 6s linear infinite}}@keyframes o{{to{{transform:rotate(270deg)}}}}
.g{{animation:g 3.2s ease-in-out infinite}}@keyframes g{{from{{transform:translateX(-160px)}}to{{transform:translateX(700px)}}}}{REDUCED_MOTION}</style>
<defs><linearGradient id="sh"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".5" stop-color="#fff" stop-opacity=".6"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient></defs>
<rect x="1" y="1" width="858" height="278" rx="14" fill="{BG}" stroke="{LINE}" stroke-width="2"/>
<g transform="translate(160 130)"><circle r="{radius}" fill="none" stroke="{PANEL}" stroke-width="20"/>{''.join(rings)}<g transform="rotate(-90)"><circle class="o" r="{radius}" fill="none" stroke="#fff" stroke-opacity=".7" stroke-width="20" stroke-dasharray="14 {circumference:.1f}"/></g>
<text y="12" text-anchor="middle" fill="{WHITE}" class="v">{total}</text><text y="42" text-anchor="middle" fill="{MUTED}" class="l">solved</text></g>
<g transform="translate(300 30)">{''.join(bars)}</g>
<text x="830" y="264" text-anchor="end" fill="{MUTED}" class="s">leetcode.com/u/{LEETCODE_USER}{note}</text></svg>'''


def main() -> None:
    out = Path(sys.argv[1] if len(sys.argv) > 1 else "dist")
    out.mkdir(parents=True, exist_ok=True)
    today = datetime.now(timezone.utc).date()
    (out / "github-stats.svg").write_text(github_card(fetch_github(), today), encoding="utf-8")
    (out / "leetcode.svg").write_text(leetcode_card(fetch_leetcode(), today), encoding="utf-8")


if __name__ == "__main__":
    main()
