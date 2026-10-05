import urllib.request
import urllib.parse
import json
import re
import os

PUB_ID = 11501196
USER_ID = 556516389

COOKIES = {
    'substack.sid': 's%3AfgvtSnIdm3_yMNrM6IjWOb7UT8u2weGs.YeXU0WROLYVmMtNTU9ONCjo81JtjA7nTCLSp3qIq%2F08',
    'substack.lli': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOjU1NjUxNjM4OSwiaWF0IjoxNzkxMTM1MDM0LCJleHAiOjE3OTM3MjcwMzQsImF1ZCI6Imxpa2VseS1sb2dnZWQtaW4ifQ.kXzSRKrodRsRVPLvyoOS1XNz175VSZ7WPn3BFBtiHBk'
}

COOKIE_HEADER = "; ".join([f"{k}={v}" for k, v in COOKIES.items()])

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Cookie': COOKIE_HEADER,
    'Content-Type': 'application/json',
    'Origin': 'https://clementvane.substack.com',
    'Referer': 'https://clementvane.substack.com/publish/post'
}

def parse_markdown_to_prosemirror(md_text):
    nodes = []
    lines = md_text.strip().split('\n')
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue
        
        # Heading 1
        if line.startswith('# '):
            nodes.append({
                "type": "heading",
                "attrs": {"level": 1},
                "content": [{"type": "text", "text": line[2:].strip()}]
            })
        # Heading 2
        elif line.startswith('## '):
            nodes.append({
                "type": "heading",
                "attrs": {"level": 2},
                "content": [{"type": "text", "text": line[3:].strip()}]
            })
        # Heading 3
        elif line.startswith('### '):
            nodes.append({
                "type": "heading",
                "attrs": {"level": 3},
                "content": [{"type": "text", "text": line[4:].strip()}]
            })
        # Blockquote
        elif line.startswith('> '):
            quote_text = line[2:].strip()
            if quote_text.startswith('*') and quote_text.endswith('*'):
                quote_text = quote_text[1:-1]
            nodes.append({
                "type": "blockquote",
                "content": [{
                    "type": "paragraph",
                    "content": [{"type": "text", "text": quote_text, "marks": [{"type": "italic"}]}]
                }]
            })
        # Horizontal rule
        elif line in ('---', '***', '___'):
            nodes.append({"type": "horizontal_rule"})
        # Normal paragraph
        else:
            clean_text = line
            nodes.append({
                "type": "paragraph",
                "content": [{"type": "text", "text": clean_text}]
            })
        i += 1
    return {"type": "doc", "content": nodes}

def publish_file(filepath):
    print(f"\nProcessing: {filepath}")
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract title
    title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    title = title_match.group(1).strip() if title_match else os.path.basename(filepath)

    # Extract subtitle or first paragraph
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
            slug = draft_res.get('slug')
            print(f"Created draft ID: {draft_id}, slug: {slug}")
    except urllib.error.HTTPError as e:
        print(f"HTTPError creating draft: {e.code} - {e.read().decode('utf-8')}")
        return

    # Publish draft
    pub_payload = {
        "send": False,
        "share_on_facebook": False
    }

    req_pub = urllib.request.Request(
        f'https://clementvane.substack.com/api/v1/drafts/{draft_id}/publish',
        data=json.dumps(pub_payload).encode('utf-8'),
        headers=HEADERS,
        method='POST'
    )

    try:
        with urllib.request.urlopen(req_pub) as resp:
            pub_res = json.loads(resp.read().decode('utf-8'))
            post_url = f"https://clementvane.substack.com/p/{pub_res.get('slug', slug)}"
            print(f"SUCCESS: Published live at {post_url}")
    except urllib.error.HTTPError as e:
        print(f"HTTPError publishing draft: {e.code} - {e.read().decode('utf-8')}")

if __name__ == '__main__':
    base_dir = '/home/juan/Datos/Datos Juan/Documentos/his former partner/Caso Joseph'
    files_to_publish = [
        os.path.join(base_dir, '06_The_Anatomy_of_Cosmic_Victimhood.md'),
        os.path.join(base_dir, '07_The_Nomadic_Gaslight_Sowing_Seeds_Burning_Bridges.md')
    ]
    for fp in files_to_publish:
        if os.path.exists(fp):
            publish_file(fp)
        else:
            print(f"File not found: {fp}")
