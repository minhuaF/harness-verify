import subprocess
import sys
import re
from datetime import datetime


def run_analyzer():
    result = subprocess.run(
        [sys.executable, "analyzer.py"],
        capture_output=True,
        text=True,
        cwd="/Users/fengminhua/code/miwa/harness-verify",
    )
    if result.returncode != 0 and not result.stdout.strip():
        raise RuntimeError(f"analyzer.py failed:\n{result.stderr}")
    return result.stdout


def parse_output(text):
    topics = []
    lines = text.strip().split("\n")
    i = 0
    while i < len(lines):
        m = re.match(r"^\s*(\d+)\.\s+\[\s*(\d+)回复\]\s+(.+)$", lines[i])
        if m:
            rank, replies, title = int(m.group(1)), int(m.group(2)), m.group(3).strip()
            summary = ""
            if i + 1 < len(lines):
                sm = re.match(r"^\s*摘要：(.+)$", lines[i + 1])
                if sm:
                    summary = sm.group(1).strip()
                    i += 1
            topics.append({"rank": rank, "replies": replies, "title": title, "summary": summary})
        i += 1
    return topics


def render_html(topics):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cards = ""
    for t in topics:
        bar_width = min(100, t["replies"] // 2 + 10)
        cards += f"""
    <article class="card">
      <div class="rank">#{t['rank']}</div>
      <div class="body">
        <h2>{t['title']}</h2>
        <p class="summary">{t['summary']}</p>
        <div class="meta">
          <span class="badge">{t['replies']} 回复</span>
          <div class="bar-wrap"><div class="bar" style="width:{bar_width}%"></div></div>
        </div>
      </div>
    </article>"""

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>V2EX 热门话题 · {now}</title>
  <style>
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      background: #f0f2f5;
      color: #1a1a2e;
      min-height: 100vh;
    }}
    header {{
      background: linear-gradient(135deg, #c0392b 0%, #e74c3c 100%);
      color: #fff;
      padding: 40px 20px 32px;
      text-align: center;
      box-shadow: 0 2px 12px rgba(0,0,0,0.15);
    }}
    header h1 {{ font-size: 2rem; letter-spacing: 0.05em; }}
    header .sub {{ margin-top: 8px; opacity: 0.8; font-size: 0.875rem; }}
    main {{
      max-width: 860px;
      margin: 36px auto;
      padding: 0 16px;
      display: flex;
      flex-direction: column;
      gap: 14px;
    }}
    .card {{
      background: #fff;
      border-radius: 10px;
      padding: 20px 24px;
      display: flex;
      gap: 20px;
      align-items: flex-start;
      box-shadow: 0 1px 6px rgba(0,0,0,0.07);
      transition: box-shadow 0.2s;
    }}
    .card:hover {{ box-shadow: 0 4px 16px rgba(0,0,0,0.12); }}
    .rank {{
      font-size: 1.75rem;
      font-weight: 800;
      color: #e74c3c;
      min-width: 52px;
      text-align: center;
      line-height: 1;
      padding-top: 4px;
    }}
    .body {{ flex: 1; }}
    .body h2 {{
      font-size: 1.05rem;
      font-weight: 600;
      line-height: 1.5;
      margin-bottom: 8px;
      color: #111;
    }}
    .summary {{
      font-size: 0.9rem;
      color: #555;
      line-height: 1.6;
      margin-bottom: 12px;
    }}
    .meta {{ display: flex; align-items: center; gap: 12px; }}
    .badge {{
      background: #fef0f0;
      color: #c0392b;
      border: 1px solid #f5c6c6;
      border-radius: 20px;
      padding: 2px 10px;
      font-size: 0.78rem;
      white-space: nowrap;
    }}
    .bar-wrap {{
      flex: 1;
      height: 4px;
      background: #f0f0f0;
      border-radius: 2px;
      overflow: hidden;
    }}
    .bar {{
      height: 100%;
      background: linear-gradient(90deg, #e74c3c, #f39c12);
      border-radius: 2px;
    }}
    footer {{
      text-align: center;
      padding: 28px 16px;
      color: #aaa;
      font-size: 0.82rem;
    }}
  </style>
</head>
<body>
  <header>
    <h1>V2EX 热门话题</h1>
    <p class="sub">由 Claude AI 摘要 &nbsp;·&nbsp; 生成于 {now}</p>
  </header>
  <main>{cards}
  </main>
  <footer>数据来源：V2EX API &nbsp;·&nbsp; 摘要模型：claude-sonnet-4-6</footer>
</body>
</html>"""


def fallback_topics():
    sys.path.insert(0, "/Users/fengminhua/code/miwa/harness-verify")
    from fetcher import fetch
    raw = fetch("https://www.v2ex.com/api/topics/hot.json")[:10]
    return [
        {"rank": i, "replies": t.get("replies", 0), "title": t.get("title", ""), "summary": "（AI 摘要暂不可用）"}
        for i, t in enumerate(raw, 1)
    ]


if __name__ == "__main__":
    print("Running analyzer.py ...")
    try:
        raw = run_analyzer()
        print(raw)
        topics = parse_output(raw)
        print(f"Parsed {len(topics)} topics from analyzer output.")
    except Exception as e:
        print(f"analyzer.py unavailable ({e}), falling back to direct fetch ...")
        topics = []

    if len(topics) < 3:
        print("Insufficient topics from analyzer, using fallback fetch ...")
        topics = fallback_topics()
        print(f"Fetched {len(topics)} topics via fallback.")

    html = render_html(topics)
    out = "/Users/fengminhua/code/miwa/harness-verify/index.html"
    with open(out, "w", encoding="utf-8") as f:
        f.write(html)

    size = len(html.encode("utf-8"))
    print(f"index.html written: {size} bytes")
    if size < 3072:
        raise SystemExit(f"FAIL: index.html is only {size} bytes (< 3KB)")
    print("OK: index.html >= 3KB")
