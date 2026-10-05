#!/usr/bin/env python3
"""
Publicador Automático de Clement Vane en Twitter / X vía Buffer GraphQL API
Despacha ensayos publicados en Substack hacia Twitter con modo 'shareNow' o 'addToQueue'.
"""

import urllib.request
import urllib.parse
import json
import os
import sys
import time

BUFFER_TOKEN = "luGLAxMeGGi2js_38adTpvhmJtMmoG8BNzN6ktd2Wkp"
TWITTER_CHANNEL_ID = "6ac2e8306a5c39ccb618069d" # @clementvane
GRAPHQL_URL = "https://api.buffer.com/graphql"

ESSAYS_TWEETS = [
    {
        "id": "10",
        "text": "🚨 NEW ESSAY: The Guru’s Hostage: The Instrumentalization of Childhood in the Service of Ecological Grandiosity.\n\nHow Joe Brewer (@earth_regen) weaponizes his young daughter as an apocalyptic shield while avoiding legal scrutiny.\n\n🔗 https://clementvane.substack.com/p/the-gurus-hostage-the-instrumentalization\n\n#Ecology #Bioregionalism #Permaculture"
    },
    {
        "id": "09",
        "text": "Can you birth 1,000 \"Bioregional Learning Centers\" in 9 years? That’s one center every 78 hours.\n\nDismantling Joe Brewer’s Silicon Valley venture-scaling masquerading as ecology, the loss of his billionaire backer, and his Delaware 501(c)(3) tax shield.\n\n🔗 https://clementvane.substack.com/p/the-1000-centers-mirage-bioregional\n\n#Degrowth #ClimateCrisis"
    },
    {
        "id": "08",
        "text": "When asked for hydrological data, soil metrics, or financial audits, Joe Brewer responds with a tobacco ritual by a stream and claims Ayahuasca told him he is a \"sorcerer of stories.\"\n\nEssay 08: Ritual as Governance & Shamanic Hubris.\n\n🔗 https://clementvane.substack.com/p/ritual-as-governance-how-joe-brewer\n\n#Ayahuasca #CriticalThinking"
    },
    {
        "id": "07",
        "text": "Claiming to turn \"monoculture into native forest in 4 years\" (an ecological absurdity), then accusing the local women founders of the Barichara biopark of \"distorting money into destruction.\"\n\nEssay 07: The Nomadic Gaslight.\n\n🔗 https://clementvane.substack.com/p/the-nomadic-gaslight-sowing-seeds\n\n#Barichara #GreenSaviorism"
    },
    {
        "id": "06",
        "text": "The Anatomy of Cosmic Victimhood: How Joe Brewer Brands Legal Accountability as 'A Form of Evil'.\n\nForensic analysis of the post of August 30, 2026, spiritual bypassing, and DARVO.\n\n🔗 https://clementvane.substack.com/p/the-anatomy-of-cosmic-victimhood\n\n#SpiritualBypassing #DARVO #Ecology"
    },
    {
        "id": "05",
        "text": "The Traveling Bioregional Circus: Jet-Setting Nomads, Carbon Footprints, and the Trail of Unfulfilled Promises.\n\nPreaching local bioregionalism while flying continuously across Cascadia, Utah, Europe, and North Africa.\n\n🔗 https://clementvane.substack.com/p/the-traveling-bioregional-circus\n\n#ClimateAction #CarbonFootprint"
    },
    {
        "id": "04",
        "text": "Bioregional Pando & ReFi Hype: Debunking the Financial Smoke and Mirrors of \"Bioregional Financing Ecosystems\", Crypto-Matching Rounds, and Subscription Paywalls.\n\n🔗 https://clementvane.substack.com/p/bioregional-pando-and-refi-hype-debunking\n\n#ReFi #Gitcoin #Web3"
    },
    {
        "id": "03",
        "text": "Green Saviorism and the Myth of the \"Living Laboratory\": How Western Eco-Expats Re-Colonize the Global South (The Case of Barichara).\n\n🔗 https://clementvane.substack.com/p/green-saviorism-and-the-myth-of-the\n\n#GreenColonialism #Permaculture #Colombia"
    },
    {
        "id": "02",
        "text": "The \"Dandelion Strategy\" & Bioregional Learning Centers: Deconstructing Brewer's Vague Corporate-Franchise Model Masquerading as Decentralized Ecology.\n\n🔗 https://clementvane.substack.com/p/the-dandelion-strategy-and-bioregional\n\n#Bioregionalism #EarthRegenerators"
    },
    {
        "id": "01",
        "text": "The Pseudoscience of \"Managing Planetary Collapse\": How Joe Brewer Weaponizes Complexity Theory and \"Post-Doom\" Fatalism to Cultivate an Apocalypse Cult.\n\n🔗 https://clementvane.substack.com/p/the-pseudoscience-of-managing-planetary-collapse\n\n#PostDoom #ApocalypseCult #Complexity"
    }
]

def publish_tweet(text, mode="addToQueue"):
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

def queue_all_essays():
    print(f"[*] Queueing Clement Vane essays to Twitter @clementvane via Buffer...")
    # Essay 10 was already sent with shareNow, queue essays 09 down to 01
    for item in ESSAYS_TWEETS[1:]:
        essay_id = item["id"]
        text = item["text"]
        print(f"\n[+] Queueing Essay {essay_id}...")
        try:
            res = publish_tweet(text, mode="addToQueue")
            post_data = res.get("data", {}).get("createPost", {})
            typename = post_data.get("__typename")
            if typename == "PostActionSuccess":
                p = post_data.get("post", {})
                print(f"    --> ENCOLADO EXITOSO (ID: {p.get('id')}, Status: {p.get('status')})")
            else:
                print(f"    --> Error en Buffer: {post_data}")
        except Exception as e:
            print(f"    --> Exception: {e}")
        time.sleep(1)

if __name__ == "__main__":
    queue_all_essays()
