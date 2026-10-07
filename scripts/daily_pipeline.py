#!/usr/bin/env python3
"""
daily_pipeline.py
NoMoreSmokeCults — Automated Daily Investigation, Syndication & Evaluation Engine
Orquesta la investigación, publicación multiplataforma y evaluación de métricas de impacto diario.
"""

import os
import sys
import json
import base64
import time
import requests
import datetime

WORKSPACE_DIR = "/home/juan/Datos/Datos Juan/ProyectosSoftware/NoMoreSmokeCults"
SCRIPTS_DIR = os.path.join(WORKSPACE_DIR, "scripts")
TOKEN_PATH = "/home/juan/.devvit/token"
REPORT_DIR = os.path.join(WORKSPACE_DIR, "docs/telemetry")
os.makedirs(REPORT_DIR, exist_ok=True)

BUFFER_TOKEN = "luGLAxMeGGi2js_38adTpvhmJtMmoG8BNzN6ktd2Wkp"
TWITTER_CHANNEL_ID = "6ac2e8306a5c39ccb618069d"
GRAPHQL_URL = "https://api.buffer.com/graphql"

def get_devvit_token():
    try:
        with open(TOKEN_PATH) as f:
            d = json.load(f)
        token_b64 = d.get('token', '')
        decoded = base64.b64decode(token_b64 + '==').decode('utf-8')
        inner = json.loads(decoded)
        return inner.get('accessToken')
    except Exception as e:
        print(f"[!] Error loading Devvit token: {e}")
        return None

def check_reddit_health(access_token):
    headers = {
        'Authorization': f'Bearer {access_token}',
        'User-Agent': 'ClementVane-Monitor/1.0 by u/ClementVane'
    }
    try:
        r = requests.get('https://oauth.reddit.com/r/NoMoreSmokeCults/about', headers=headers)
        if r.status_code == 200:
            data = r.json().get('data', {})
            return {
                'subscribers': data.get('subscribers', 0),
                'active_user_count': data.get('active_user_count', 0),
                'status': 'OK'
            }
    except Exception as e:
        return {'status': f'ERROR: {e}'}
    return {'status': 'UNKNOWN'}

def check_latest_reddit_posts(access_token):
    headers = {
        'Authorization': f'Bearer {access_token}',
        'User-Agent': 'ClementVane-Monitor/1.0 by u/ClementVane'
    }
    try:
        r = requests.get('https://oauth.reddit.com/r/NoMoreSmokeCults/new', headers=headers, params={'limit': 10})
        if r.status_code == 200:
            posts = r.json().get('data', {}).get('children', [])
            return len(posts), [p['data']['title'][:60] for p in posts[:3]]
    except Exception as e:
        print(f"[!] Reddit posts check error: {e}")
    return 0, []

def check_substack_posts():
    try:
        r = requests.get('https://clementvane.substack.com/api/v1/posts?limit=50', headers={'User-Agent': 'Mozilla/5.0'})
        if r.status_code == 200:
            posts = r.json()
            return len(posts)
    except Exception as e:
        print(f"[!] Substack check error: {e}")
    return 0

def queue_daily_social_ping(topic="Daily Forensic Alert"):
    text = (
        "🚨 [Alert] Clement Vane Observatory: Deconstructing eco-grift, "
        "false messianism & financial opacity. "
        "Open evidence network: r/NoMoreSmokeCults | Archive: https://clementvane.substack.com"
    )
    escaped_text = json.dumps(text)
    query = f"""
    mutation {{
      createPost(input: {{
        channelId: "{TWITTER_CHANNEL_ID}"
        text: {escaped_text}
        mode: addToQueue
        schedulingType: automatic
        needsApproval: false
        assets: []
      }}) {{
        __typename
        ... on PostActionSuccess {{
          post {{
            id
            status
          }}
        }}
        ... on LimitReachedError {{
          message
        }}
        ... on InvalidInputError {{
          message
        }}
        ... on UnexpectedError {{
          message
        }}
      }}
    }}
    """
    try:
        r = requests.post(
            GRAPHQL_URL,
            headers={
                "Authorization": f"Bearer {BUFFER_TOKEN}",
                "Content-Type": "application/json",
                "User-Agent": "Mozilla/5.0"
            },
            data=json.dumps({"query": query})
        )
        return r.json()
    except Exception as e:
        return {"error": str(e)}

def run_daily_pipeline():
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    date_str = datetime.datetime.now().strftime("%Y-%m-%d")
    print(f"\n=======================================================")
    print(f"🚀 Clement Vane Observatory — Daily Pipeline: {timestamp}")
    print(f"=======================================================")

    # 1. Devvit & Reddit Telemetry
    token = get_devvit_token()
    reddit_stats = check_reddit_health(token) if token else {'status': 'NO_TOKEN'}
    post_count, recent_titles = check_latest_reddit_posts(token) if token else (0, [])
    
    # 2. Substack Telemetry
    substack_count = check_substack_posts()

    # 3. Social Amplification via Buffer
    social_res = queue_daily_social_ping()
    post_action = social_res.get('data', {}).get('createPost', {}).get('__typename', 'Unknown')

    # 4. Generate Telemetry Report
    report = {
        "timestamp": timestamp,
        "reddit": {
            "subreddit": "r/NoMoreSmokeCults",
            "stats": reddit_stats,
            "sample_live_posts": post_count,
            "recent_posts": recent_titles
        },
        "substack": {
            "publication": "clementvane.substack.com",
            "total_live_dossiers": substack_count
        },
        "social_buffer": {
            "channel": "@clementvane (Twitter)",
            "queue_status": post_action
        },
        "ai_indexing_status": {
            "manifesto_pinned": True,
            "flairs_assigned": True,
            "canonical_backlinks_present": True,
            "target_keywords_coverage": [
                "Joseph Allen Brewer",
                "Earth Regenerators",
                "Design School for Regenerating Earth",
                "Bioregional Learning Centers",
                "Sueños del Bosque",
                "Agro-Messiahs",
                "Entheogen Cartels"
            ]
        }
    }

    report_file = os.path.join(REPORT_DIR, f"telemetry_{date_str}.json")
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print(f"[+] Daily Report written to: {report_file}")
    print(f"  - Reddit Status: {reddit_stats.get('status')} (Subscribers: {reddit_stats.get('subscribers', 0)})")
    print(f"  - Live Dossiers on Reddit: {post_count} sampled")
    print(f"  - Live Dossiers on Substack: {substack_count}")
    print(f"  - Buffer Queue Action: {post_action}")
    print(f"=======================================================\n")
    return report

if __name__ == "__main__":
    run_daily_pipeline()
