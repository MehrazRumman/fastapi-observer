#!/usr/bin/env python3
from __future__ import annotations

import sys
import xml.etree.ElementTree as ET
from pathlib import Path


def pick_color(percent: int) -> str:
    if percent >= 90:
        return "#4c1"  # brightgreen
    if percent >= 80:
        return "#97CA00"  # green
    if percent >= 70:
        return "#a4a61d"  # yellowgreen
    if percent >= 60:
        return "#dfb317"  # yellow
    if percent >= 50:
        return "#fe7d37"  # orange
    return "#e05d44"  # red


def text_width(text: str) -> int:
    # Approximate width for 11px sans-serif shields-style text.
    return max(20, len(text) * 7 + 10)


def make_badge(label: str, value: str, color: str) -> str:
    left = text_width(label)
    right = text_width(value)
    total = left + right
    left_center = left / 2
    right_center = left + right / 2

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{total}" height="20" role="img" aria-label="{label}: {value}">
  <title>{label}: {value}</title>
  <linearGradient id="s" x2="0" y2="100%">
    <stop offset="0" stop-color="#bbb" stop-opacity=".1"/>
    <stop offset="1" stop-opacity=".1"/>
  </linearGradient>
  <mask id="m">
    <rect width="{total}" height="20" rx="3" fill="#fff"/>
  </mask>
  <g mask="url(#m)">
    <rect width="{left}" height="20" fill="#555"/>
    <rect x="{left}" width="{right}" height="20" fill="{color}"/>
    <rect width="{total}" height="20" fill="url(#s)"/>
  </g>
  <g fill="#fff" text-anchor="middle" font-family="DejaVu Sans,Verdana,Geneva,sans-serif" text-rendering="geometricPrecision" font-size="11">
    <text x="{left_center}" y="15" fill="#010101" fill-opacity=".3">{label}</text>
    <text x="{left_center}" y="14">{label}</text>
    <text x="{right_center}" y="15" fill="#010101" fill-opacity=".3">{value}</text>
    <text x="{right_center}" y="14">{value}</text>
  </g>
</svg>
"""


def main() -> int:
    if len(sys.argv) != 3:
        print("Usage: generate_coverage_badge.py <coverage.xml> <output.svg>")
        return 2

    coverage_xml = Path(sys.argv[1])
    output_svg = Path(sys.argv[2])

    tree = ET.parse(coverage_xml)
    root = tree.getroot()
    line_rate = root.attrib.get("line-rate")
    if line_rate is None:
        raise ValueError("coverage.xml missing line-rate attribute")

    percent = round(float(line_rate) * 100)
    badge = make_badge("coverage", f"{percent}%", pick_color(percent))
    output_svg.write_text(badge, encoding="utf-8")
    print(f"Wrote badge: {output_svg} ({percent}%)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
