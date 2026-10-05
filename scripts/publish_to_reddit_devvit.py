#!/usr/bin/env python3
"""
Despachador de Ensayos a Reddit vía Servidor Devvit
Envía posts formateados al endpoint Hono de la app Devvit para publicarse en r/NoMoreSmokeCults sin riesgo de baneo en otros subs.
"""

import urllib.request
import urllib.parse
import json
import os
import sys
import re

DEVVIT_SERVER_URL = os.environ.get("DEVVIT_SERVER_URL", "http://localhost:3000/api/publish/submit")
DEFAULT_SUBREDDIT = "NoMoreSmokeCults"

def submit_essay_to_reddit(title, url=None, text=None, subreddit=DEFAULT_SUBREDDIT):
    payload = {
        "title": title,
        "subredditName": subreddit
    }
    if url:
        payload["url"] = url
    if text:
        payload["text"] = text

    print(f"\n[REDDIT DEVVIT] Despachando a r/{subreddit}:")
    print(f"  Title: {title}")
    if url:
        print(f"  URL: {url}")

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        DEVVIT_SERVER_URL,
        data=data,
        headers={"Content-Type": "application/json", "User-Agent": "ClementVanePublisher/1.0"}
    )

    try:
        with urllib.request.urlopen(req) as resp:
            res = json.loads(resp.read().decode("utf-8"))
            if res.get("success"):
                p = res.get("post", {})
                print(f"  --> [ÉXITO] Post Creado: {p.get('permalink') or p.get('url')} (ID: {p.get('id')})")
                return p
            else:
                print(f"  --> [ERROR EN RESPUESTA]: {res}")
                return None
    except Exception as e:
        print(f"  --> [EXCEPCIÓN DE RED]: {e}")
        return None

def main():
    if len(sys.argv) > 1:
        md_file = sys.argv[1]
        with open(md_file, "r", encoding="utf-8") as f:
            content = f.read()

        title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        title = title_match.group(1).strip() if title_match else os.path.basename(md_file)

        # Check if user passed url as second arg
        url = sys.argv[2] if len(sys.argv) > 2 else None
        submit_essay_to_reddit(title=title, url=url, text=content if not url else None)
    else:
        print("Uso: python3 scripts/publish_to_reddit_devvit.py <archivo.md> [url_opcional]")

if __name__ == "__main__":
    main()
