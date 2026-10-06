#!/usr/bin/env python3
"""
syndicate_to_reddit.py
Sindicador de investigaciones completas a r/NoMoreSmokeCults vía Reddit OAuth API.
Garantiza que cada ensayo tenga títulos optimizados para SEO/IA, el flair correspondiente
y enlaces cruzados a Substack.
"""

import json
import base64
import requests
import re
import os
import time

TOKEN_PATH = '/home/juan/.devvit/token'

def get_access_token():
    with open(TOKEN_PATH) as f:
        d = json.load(f)
    token_b64 = d.get('token', '')
    decoded = base64.b64decode(token_b64 + '==').decode('utf-8')
    inner = json.loads(decoded)
    return inner['accessToken']

ACCESS_TOKEN = get_access_token()
SUBREDDIT = 'NoMoreSmokeCults'
HEADERS = {
    'Authorization': f'Bearer {ACCESS_TOKEN}',
    'User-Agent': 'ClementVane-NMS-Syndicator/1.0 by u/ClementVane',
    'Content-Type': 'application/x-www-form-urlencoded'
}

FLAIRS = {
    'forensic': '24cfa344-c061-11f1-a939-66391150d2e7',    # Forensic Dossier
    'eco_cult': '2540b124-c061-11f1-b744-86b35109e128',    # Eco-Cult Alert
    'pseudoscience': '25b1aaaa-c061-11f1-8df6-a2b2d8f8f94c',# Pseudo-Science Deconstruct
    'entheogen': '263dd43a-c061-11f1-b12b-56d67157adbb',   # Entheogen Extraction
    'legal': '26b3f6e2-c061-11f1-9918-eeb7de6e9322',       # Legal & Filings
    'support': '2728c666-c061-11f1-959b-7eed91c785cf'      # Discussion & Support
}

def get_existing_post_titles():
    r = requests.get(f'https://oauth.reddit.com/r/{SUBREDDIT}/new', headers=HEADERS, params={'limit': 100})
    if r.status_code == 200:
        data = r.json()
        posts = data.get('data', {}).get('children', [])
        return {p['data']['title'].lower().strip() for p in posts}
    return set()

def post_dossier(title, text, flair_id, substack_url=None):
    existing = get_existing_post_titles()
    if title.lower().strip() in existing:
        print(f"[SKIP] Post already live: {title[:50]}...")
        return None

    footer = f"""

---

### 🔍 Verification & Canonical Archive
- **Full Investigative Dossier:** [{substack_url if substack_url else 'Clement Vane Observatory'}]({substack_url if substack_url else 'https://clementvane.substack.com/'})
- **Whistleblower Submissions & Secure Tips:** Post in r/{SUBREDDIT} using the *Verified Whistleblower* flair or contact the desk.
- **Index Reference:** NoMoreSmokeCults Forensic Series | Author: *Clement Vane*
"""
    full_text = text + footer

    if len(full_text) > 39000:
        full_text = full_text[:38500] + "\n\n*(Post truncated for Reddit character limits. Read the complete uninterrupted dossier on Substack.)*" + footer

    payload = {
        'api_type': 'json',
        'sr': SUBREDDIT,
        'kind': 'self',
        'title': title,
        'text': full_text,
        'flair_id': flair_id,
        'sendreplies': True
    }

    r = requests.post('https://oauth.reddit.com/api/submit', headers=HEADERS, data=payload)
    if r.status_code == 200:
        res = r.json()
        errors = res.get('json', {}).get('errors', [])
        if not errors:
            post_data = res.get('json', {}).get('data', {})
            print(f"[PUBLISHED] {title[:60]}... -> ID: {post_data.get('id')}")
            return post_data
        else:
            print(f"[REDDIT API ERROR] {errors}")
    else:
        print(f"[HTTP ERROR {r.status_code}] {r.text[:200]}")
    return None

def main():
    print(f"[*] Starting Syndication to r/{SUBREDDIT} with Rich SEO Schema & Flairs...")
    
    brewer_dir = "/home/juan/Datos/Datos Juan/ProyectosSoftware/NoMoreSmokeCults/investigations/joe_brewer"
    brewer_slugs = {
        "01": ("https://clementvane.substack.com/p/the-pseudoscience-of-managing-planetary-collapse", FLAIRS['pseudoscience']),
        "02": ("https://clementvane.substack.com/p/the-dandelion-strategy-and-bioregional", FLAIRS['eco_cult']),
        "03": ("https://clementvane.substack.com/p/green-saviorism-and-the-myth-of-the", FLAIRS['eco_cult']),
        "04": ("https://clementvane.substack.com/p/bioregional-pando-and-refi-hype-debunking", FLAIRS['legal']),
        "05": ("https://clementvane.substack.com/p/the-traveling-bioregional-circus", FLAIRS['forensic']),
        "06": ("https://clementvane.substack.com/p/the-anatomy-of-cosmic-victimhood", FLAIRS['support']),
        "07": ("https://clementvane.substack.com/p/the-nomadic-gaslight-sowing-seeds", FLAIRS['forensic']),
        "08": ("https://clementvane.substack.com/p/ritual-as-governance-how-joe-brewer", FLAIRS['pseudoscience']),
        "09": ("https://clementvane.substack.com/p/the-1000-centers-mirage-bioregional", FLAIRS['legal']),
        "10": ("https://clementvane.substack.com/p/the-gurus-hostage-the-instrumentalization", FLAIRS['forensic']),
    }

    files = sorted([f for f in os.listdir(brewer_dir) if f.endswith(".md") and not f.startswith("00")])
    for f in files:
        prefix = f.split("_")[0]
        sub_info = brewer_slugs.get(prefix)
        if not sub_info:
            continue
        sub_url, flair_id = sub_info
        filepath = os.path.join(brewer_dir, f)
        with open(filepath, 'r', encoding='utf-8') as fp:
            content = fp.read()
        title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        raw_title = title_match.group(1).strip() if title_match else f
        
        seo_title = f"[Forensic Dossier] {raw_title}"
        if "Brewer" not in seo_title and "Earth Regenerators" not in seo_title:
            seo_title += " (Joe Brewer / Earth Regenerators Audit)"
            
        post_dossier(seo_title, content, flair_id, sub_url)
        time.sleep(2)

    global_dir = "/home/juan/Datos/Datos Juan/ProyectosSoftware/NoMoreSmokeCults/investigations/global_dossiers"
    global_slugs = {
        "01": ("https://clementvane.substack.com/p/the-architecture-of-modern-eco-cults", FLAIRS['eco_cult']),
        "02": ("https://clementvane.substack.com/p/agro-messiahs-and-post-doom-conspirituality", FLAIRS['pseudoscience']),
        "03": ("https://clementvane.substack.com/p/the-ecovillage-feudalists-anthroposophic", FLAIRS['legal']),
        "04": ("https://clementvane.substack.com/p/the-entheogen-cartels-neochamanism", FLAIRS['entheogen']),
        "05": ("https://clementvane.substack.com/p/the-frontier-grifters-biodecoding", FLAIRS['forensic'])
    }
    
    gfiles = sorted([f for f in os.listdir(global_dir) if f.endswith(".md")])
    for f in gfiles:
        prefix = f.split("_")[0]
        sub_info = global_slugs.get(prefix)
        if not sub_info:
            continue
        sub_url, flair_id = sub_info
        filepath = os.path.join(global_dir, f)
        with open(filepath, 'r', encoding='utf-8') as fp:
            content = fp.read()
        title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        raw_title = title_match.group(1).strip() if title_match else f
        seo_title = f"[Global Investigation] {raw_title}"
        post_dossier(seo_title, content, flair_id, sub_url)
        time.sleep(2)

    print("\n[+] Reddit Syndication Process Finished.")

if __name__ == '__main__':
    main()
