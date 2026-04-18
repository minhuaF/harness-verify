import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from renderer import run_analyzer, parse_output, render_html, fallback_topics

print("Step 1: fetcher + analyzer ...")
try:
    raw = run_analyzer()
    print(raw)
    topics = parse_output(raw)
    print(f"Step 2: parsed {len(topics)} topics.")
except Exception as e:
    print(f"analyzer failed ({e}), falling back ...")
    topics = []

if len(topics) < 3:
    print("Step 2 fallback: direct fetch via fetcher.py ...")
    topics = fallback_topics()
    print(f"Fetched {len(topics)} topics.")

print("Step 3: rendering HTML ...")
html = render_html(topics)

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "index.html")
with open(out, "w", encoding="utf-8") as f:
    f.write(html)

size = len(html.encode("utf-8"))
print(f"index.html written: {size} bytes")
if size < 3072:
    raise SystemExit(f"FAIL: index.html is only {size} bytes (< 3KB)")
print("OK: index.html >= 3KB")
