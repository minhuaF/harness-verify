import urllib.request
import json
import time

def fetch(url):
    import http.client
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=15) as r:
                return json.loads(r.read())
        except http.client.IncompleteRead as e:
            if e.partial:
                return json.loads(e.partial)
            if attempt == 2:
                raise
            time.sleep(attempt + 1)

if __name__ == "__main__":
    topics = fetch("https://www.v2ex.com/api/topics/hot.json")[:10]
    for i, t in enumerate(topics, 1):
        title = t.get("title", "N/A")
        url = t.get("url", "")
        replies = t.get("replies", 0)
        print(f"{i:2}. [{replies:4}回复] {title}")
        print(f"     {url}")
