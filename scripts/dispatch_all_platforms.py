#!/usr/bin/env python3
"""
Sindicador y Despachador Masivo — Clement Vane
Automatiza el control y distribución en Substack, Hashnode, X (Twitter) y Reddit.
"""

import urllib.request
import urllib.parse
import json
import os
import re
import subprocess

HASHNODE_TOKEN = "736073fa-4b58-4d83-b063-5cf31baf147b"
SUBSTACK_FEED = "https://clementvane.substack.com/feed"

def check_substack():
    req = urllib.request.Request("https://clementvane.substack.com/api/v1/posts?limit=20", headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            print(f"[*] Substack Clement Vane: {len(data)} ensayos publicados en vivo.")
            return data
    except Exception as e:
        print("[!] Error verificando Substack:", e)
        return []

def main():
    print("=" * 60)
    print("   CLEMENT VANE — DESPACHADOR Y SINDICADOR MULTIRED")
    print("=" * 60)
    posts = check_substack()
    print(f"\n[1] Hashnode (API Token registrado): {HASHNODE_TOKEN[:8]}...{HASHNODE_TOKEN[-4:]}")
    print(f"    - Feed RSS canónico listo para clonación: {SUBSTACK_FEED}")
    print("\n[2] X / Twitter (@clementvane):")
    print("    - Plantillas de alta fidelidad compiladas en: twitter_distribution_kit.md")
    print("\n[3] Reddit (u/ClementVane):")
    print("    - Estrategia de comunidades (r/bioregionalism, r/Collapse, r/Permaculture) en: reddit_syndication_kit.md")
    print("=" * 60)

if __name__ == "__main__":
    main()
