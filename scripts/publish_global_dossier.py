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

# Cargar .env si existe
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
if os.path.exists(env_path):
    with open(env_path) as f:
        for line in f:
            if '=' in line and not line.strip().startswith('#'):
                k, v = line.strip().split('=', 1)
                os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))

# Configuración Substack
PUB_ID = 11501196
USER_ID = 556516389

COOKIES = {
    'substack.sid': os.getenv('SUBSTACK_SID', ''),
    'substack.lli': os.getenv('SUBSTACK_LLI', '')
}
COOKIE_HEADER = '; '.join([f'{k}={v}' for k, v in COOKIES.items() if v])

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Cookie': COOKIE_HEADER,
    'Content-Type': 'application/json',
    'Origin': 'https://clementvane.substack.com',
    'Referer': 'https://clementvane.substack.com/publish/post'
}

# Configuración Buffer
BUFFER_TOKEN = os.getenv("BUFFER_TOKEN", "")
TWITTER_CHANNEL_ID = os.getenv("BUFFER_TWITTER_CHANNEL_ID", "6ac2e8306a5c39ccb618069d") # @clementvane
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

def publish_single_dossier(filepath, tweet_summary=""):
    url = publish_to_substack(filepath)
    if not url:
        print(f"[SKIP/EXISTING] No new post published for {os.path.basename(filepath)}")
        return

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    raw_title = title_match.group(1).strip() if title_match else os.path.basename(filepath)

    # Clean short title for Twitter
    short_title = raw_title.split(':')[0]

    tweet_text = (
        f"🚨 NEW: {short_title}\n\n"
        f"{tweet_summary if tweet_summary else 'Forensic investigation & political ecology by Clement Vane:'}\n"
        f"{url}\n\n"
        "#Ecology #RegenerativeAg #Climate"
    )

    if len(tweet_text) > 280:
        tweet_text = f"🚨 NEW: {short_title}\n\n{url}\n\n#Ecology #Climate"

    print(f"\n[BUFFER] Despachando a Twitter (@clementvane)... (Len: {len(tweet_text)})")
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

def main():
    if len(sys.argv) > 1:
        target_path = sys.argv[1]
        publish_single_dossier(target_path)
    else:
        dossier_dir = "/home/juan/Datos/Datos Juan/ProyectosSoftware/NoMoreSmokeCults/investigations/global_dossiers"
        files = sorted([os.path.join(dossier_dir, f) for f in os.listdir(dossier_dir) if f.endswith(".md")])
        for fp in files:
            publish_single_dossier(fp)

if __name__ == "__main__":
    main()

