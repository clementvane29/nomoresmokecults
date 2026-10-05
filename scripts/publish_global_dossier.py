#!/usr/bin/env python3
"""
Publicador de Dossiers Globales — Clement Vane
Publica ensayos del Roster Global en Substack y despacha el anuncio a Twitter (@clementvane) vía Buffer GraphQL API.
"""

import urllib.request
import urllib.parse
import json
import re
import os
import sys

# Configuración Substack
PUB_ID = 11501196
USER_ID = 556516389

COOKIES = {
    'substack.sid': 's%3AfgvtSnIdm3_yMNrM6IjWOb7UT8u2weGs.YeXU0WROLYVmMtNTU9ONCjo81JtjA7nTCLSp3qIq%2F08',
    'substack.lli': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOjU1NjUxNjM4OSwiaWF0IjoxNzkxMTM1MDM0LCJleHAiOjE3OTM3MjcwMzQsImF1ZCI6Imxpa2VseS1sb2dnZWQtaW4ifQ.kXzSRKrodRsRVPLvyoOS1XNz175VSZ7WPn3BFBtiHBk'
}
COOKIE_HEADER = '; '.join([f'{k}={v}' for k, v in COOKIES.items()])

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Cookie': COOKIE_HEADER,
    'Content-Type': 'application/json',
    'Origin': 'https://clementvane.substack.com',
    'Referer': 'https://clementvane.substack.com/publish/post'
}

# Configuración Buffer
BUFFER_TOKEN = "luGLAxMeGGi2js_38adTpvhmJtMmoG8BNzN6ktd2Wkp"
TWITTER_CHANNEL_ID = "6ac2e8306a5c39ccb618069d" # @clementvane
GRAPHQL_URL = "https://api.buffer.com/graphql"

def get_live_posts():
    req = urllib.request.Request('https://clementvane.substack.com/api/v1/posts?limit=50', headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            return [p.get('title', '').strip().lower() for p in data]
    except Exception as e:
        print("[!] Error fetching live posts:", e)
        return []

def parse_markdown_to_prosemirror(md_text):
    nodes = []
    lines = md_text.strip().split('\n')
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue
        if line.startswith('# '):
            nodes.append({"type": "heading", "attrs": {"level": 1}, "content": [{"type": "text", "text": line[2:].strip()}]})
        elif line.startswith('## '):
            nodes.append({"type": "heading", "attrs": {"level": 2}, "content": [{"type": "text", "text": line[3:].strip()}]})
        elif line.startswith('### '):
            nodes.append({"type": "heading", "attrs": {"level": 3}, "content": [{"type": "text", "text": line[4:].strip()}]})
        elif line.startswith('> '):
            quote_text = line[2:].strip()
            if quote_text.startswith('*') and quote_text.endswith('*'):
                quote_text = quote_text[1:-1]
            nodes.append({
                "type": "blockquote",
                "content": [{"type": "paragraph", "content": [{"type": "text", "text": quote_text, "marks": [{"type": "italic"}]}]}]
            })
        elif line in ('---', '***', '___'):
            nodes.append({"type": "horizontal_rule"})
        elif line.startswith('* ') or line.startswith('- '):
            # Simple bullet point list item
            bullet_text = line[2:].strip()
            nodes.append({
                "type": "paragraph",
                "content": [{"type": "text", "text": "• " + bullet_text}]
            })
        else:
            nodes.append({"type": "paragraph", "content": [{"type": "text", "text": line}]})
        i += 1
    return {"type": "doc", "content": nodes}

def publish_to_substack(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    title = title_match.group(1).strip() if title_match else os.path.basename(filepath)

    live_titles = get_live_posts()
    normalized_title = title.lower()
    for lt in live_titles:
        if normalized_title in lt or lt in normalized_title:
            print(f"[SKIP] Already published on Substack: {title}")
            return None

    print(f"\n[SUBSTACK] Creating Draft for: {title}")
    subtitle_match = re.search(r'\*\*By Clement Vane\*\*\s*\n\*(.+?)\*', content)
    subtitle = subtitle_match.group(1).strip() if subtitle_match else "By Clement Vane"

    doc_json = parse_markdown_to_prosemirror(content)

    draft_payload = {
        "publication_id": PUB_ID,
        "title": title,
        "draft_title": title,
        "subtitle": subtitle,
        "draft_subtitle": subtitle,
        "draft_bylines": [{"id": USER_ID, "is_guest": False}],
        "draft_body": json.dumps(doc_json),
        "type": "newsletter"
    }

    req = urllib.request.Request(
        'https://clementvane.substack.com/api/v1/drafts',
        data=json.dumps(draft_payload).encode('utf-8'),
        headers=HEADERS,
        method='POST'
    )

    try:
        with urllib.request.urlopen(req) as resp:
            draft_res = json.loads(resp.read().decode('utf-8'))
            draft_id = draft_res.get('id')
            print(f"[SUBSTACK] Draft created with ID: {draft_id}")
    except Exception as e:
        print(f"[SUBSTACK ERROR] Failed creating draft: {e}")
        return None

    req_pub = urllib.request.Request(
        f'https://clementvane.substack.com/api/v1/drafts/{draft_id}/publish',
        data=json.dumps({"send": False, "share_on_facebook": False}).encode('utf-8'),
        headers=HEADERS,
        method='POST'
    )

    try:
        with urllib.request.urlopen(req_pub) as resp:
            pub_res = json.loads(resp.read().decode('utf-8'))
            url = f"https://clementvane.substack.com/p/{pub_res.get('slug')}"
            print(f"[SUBSTACK LIVE] Published: {url}")
            return url
    except Exception as e:
        print(f"[SUBSTACK ERROR] Failed publishing: {e}")
        return None

def publish_to_buffer(text, mode="shareNow"):
    escaped_text = json.dumps(text)
    query = f"""
    mutation {{
      createPost(input: {{
        channelId: "{TWITTER_CHANNEL_ID}"
        text: {escaped_text}
        mode: {mode}
        schedulingType: automatic
        needsApproval: false
        assets: []
      }}) {{
        __typename
        ... on PostActionSuccess {{
          post {{
            id
            status
            text
          }}
        }}
        ... on UnexpectedError {{
          message
        }}
        ... on InvalidInputError {{
          message
        }}
        ... on LimitReachedError {{
          message
        }}
        ... on UnauthorizedError {{
          message
        }}
      }}
    }}
    """
    req = urllib.request.Request(
        GRAPHQL_URL,
        headers={
            "Authorization": f"Bearer {BUFFER_TOKEN}",
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0"
        },
        data=json.dumps({"query": query}).encode("utf-8")
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))

def main():
    filepath = "/home/juan/Datos/Datos Juan/ProyectosSoftware/NoMoreSmokeCults/investigations/global_dossiers/01_The_Architecture_of_Modern_Eco_Cults.md"
    url = publish_to_substack(filepath)
    if not url:
        url = "https://clementvane.substack.com/p/the-architecture-of-modern-eco-cults"

    tweet_text = (
        "🚨 NEW: The Architecture of Modern Eco-Cults\n\n"
        "How Post-Doom Prophets, Neo-Shamans, and Green Grifters Weaponize Planetary Crisis.\n\n"
        "A forensic taxonomy by Clement Vane:\n"
        f"{url}\n\n"
        "#Ecology #PostDoom #Climate"
    )

    print("\n[BUFFER] Despachando a Twitter (@clementvane)...")
    try:
        res = publish_to_buffer(tweet_text, mode="shareNow")
        post_data = res.get("data", {}).get("createPost", {})
        typename = post_data.get("__typename")
        if typename == "PostActionSuccess":
            p = post_data.get("post", {})
            print(f"--> [BUFFER SUCCESS] Tweet publicado en vivo (ID: {p.get('id')}, Status: {p.get('status')})")
        else:
            print(f"--> [BUFFER ERROR]: {post_data}")
    except Exception as e:
        print(f"--> [BUFFER EXCEPTION]: {e}")

if __name__ == "__main__":
    main()
