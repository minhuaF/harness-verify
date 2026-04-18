import os
import time
from dotenv import load_dotenv
from anthropic import Anthropic, InternalServerError
from fetcher import fetch

load_dotenv()

import httpx

client = Anthropic(
    api_key=os.getenv("ANTHROPIC_API_KEY"),
    base_url=os.getenv("ANTHROPIC_BASE_URL"),
    http_client=httpx.Client(proxy=None, trust_env=False),
)

topics = fetch("https://www.v2ex.com/api/topics/hot.json")[:10]

for i, t in enumerate(topics, 1):
    title = t.get("title", "N/A")
    replies = t.get("replies", 0)

    for attempt in range(3):
        try:
            message = client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=100,
                messages=[{"role": "user", "content": f"用一句中文摘要这条新闻标题，不超过20字：{title}"}],
            )
            break
        except httpx.HTTPError:
            if attempt == 2:
                raise
            time.sleep(5 * (attempt + 1))
        except InternalServerError:
            if attempt == 2:
                raise
            time.sleep(5 * (attempt + 1))

    summary = next(b.text for b in message.content if b.type == "text")
    print(f"{i:2}. [{replies:4}回复] {title}")
    print(f"     摘要：{summary}")
    print()
