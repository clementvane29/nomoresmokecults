#!/usr/bin/env python3
import urllib.request
import urllib.parse
import json
import re
import os
import sys

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

def get_live_posts():
    req = urllib.request.Request('https://clementvane.substack.com/api/v1/posts?limit=50', headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            return [p.get('title', '').strip().lower() for p in data]
    except Exception as e:
        print("Error fetching live posts:", e)
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
        else:
            nodes.append({"type": "paragraph", "content": [{"type": "text", "text": line}]})
        i += 1
    return {"type": "doc", "content": nodes}

def publish_file(filepath, live_titles):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    title = title_match.group(1).strip() if title_match else os.path.basename(filepath)

    # Check if already published
    normalized_title = title.lower()
    for lt in live_titles:
        if normalized_title in lt or lt in normalized_title:
            print(f"[SKIP] Already published: {title}")
            return

    print(f"\n[PUBLISHING] {title} ({os.path.basename(filepath)})")

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
    except Exception as e:
        print(f"Error creating draft: {e}")
        return

    req_pub = urllib.request.Request(
        f'https://clementvane.substack.com/api/v1/drafts/{draft_id}/publish',
        data=json.dumps({"send": False, "share_on_facebook": False}).encode('utf-8'),
        headers=HEADERS,
        method='POST'
    )

    try:
        with urllib.request.urlopen(req_pub) as resp:
            pub_res = json.loads(resp.read().decode('utf-8'))
            print(f"--> LIVE: https://clementvane.substack.com/p/{pub_res.get('slug')}")
    except Exception as e:
        print(f"Error publishing: {e}")

if __name__ == '__main__':
    base_dir = '/home/juan/Datos/Datos Juan/Documentos/his former partner/Caso Joseph'
    live_titles = get_live_posts()
    print(f"Currently live posts count: {len(live_titles)}")

    all_files = sorted([f for f in os.listdir(base_dir) if re.match(r'^\d{2}_.*\.md$', f) and not f.startswith('00_')])
    for filename in all_files:
        fp = os.path.join(base_dir, filename)
        publish_file(fp, live_titles)
