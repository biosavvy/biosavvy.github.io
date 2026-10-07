#!/usr/bin/env python3
"""
BioSavvy Multi-Platform Auto-Publisher v3
Posts article summaries to platforms with APIs.

Supported platforms (only posts to configured ones):
  - Dev.to:  Casual tech-blog style posts
  - Reddit:  Personal-experience sharing in health subreddits

Setup — set GitHub Secrets:
  DEVTO_API_KEY:        Get from https://dev.to/settings/extensions
  REDDIT_CLIENT_ID:     Get from https://www.reddit.com/prefs/apps (script type)
  REDDIT_CLIENT_SECRET: From the same app
  REDDIT_USERNAME:      Your Reddit username
  REDDIT_PASSWORD:      Your Reddit password

Runs: on push to main (new articles) or manually via workflow_dispatch
"""

import os
import sys
import json
import re
import requests
from datetime import datetime

SITE_URL = "https://biosavvy.github.io"

# ── Platform configs ──
DEVTO_API_KEY = os.environ.get("DEVTO_API_KEY", "")
REDDIT_CLIENT_ID = os.environ.get("REDDIT_CLIENT_ID", "")
REDDIT_CLIENT_SECRET = os.environ.get("REDDIT_CLIENT_SECRET", "")
REDDIT_USERNAME = os.environ.get("REDDIT_USERNAME", "")
REDDIT_PASSWORD = os.environ.get("REDDIT_PASSWORD", "")


# ── Article discovery ──
def get_articles():
    """Get published articles from sitemap."""
    try:
        r = requests.get(f"{SITE_URL}/sitemap.xml", timeout=30)
        urls = re.findall(r'<loc>(https://biosavvy\.github\.io/article\d+\.html)</loc>', r.text)
        return urls
    except Exception as e:
        print(f"  ✗ Error fetching sitemap: {e}")
        return []


def fetch_article(url):
    """Fetch article metadata."""
    try:
        r = requests.get(url, timeout=30)
        if r.status_code != 200:
            return None
        html = r.text
        title = re.search(r'<title>(.*?)</title>', html)
        desc = re.search(r'<meta name="description" content="(.*?)"', html)
        og_img = re.search(r'<meta property="og:image" content="(.*?)"', html)

        title = title.group(1) if title else ""
        desc = desc.group(1) if desc else ""
        image = og_img.group(1) if og_img else ""

        # Clean
        for s in [title, desc]:
            s = s.replace('&#x27;', "'").replace('&amp;', '&')

        return {"url": url, "title": title, "description": desc, "image": image}
    except Exception:
        return None


# ── Dev.to ──
def post_to_devto(article):
    """Post article summary to Dev.to."""
    if not DEVTO_API_KEY:
        return False

    title = article["title"].replace(" in 2026: Expert Reviews & Buying Guide", "")
    title = title.replace(" in 2026: Tested & Ranked", "")

    body = f"""---
title: {title}
published: true
tags: [health, productreview, buyerguide, wellness]
cover_image: {article['image']}
---

I built [BioSavvy]({SITE_URL}), a site that reviews health products using evidence and measurable criteria — not marketing hype.

## {article['title']}

{article['description']}

**[Read the full review →]({article['url']})**

We evaluate products on:
- 📊 Measurable performance metrics
- 🔬 Scientific evidence behind claims
- 💰 Value for money
- 🛡️ Build quality and safety

Check out the full buyer's guide at [BioSavvy]({SITE_URL}) for detailed specs, pros/cons, and our top picks.

*All reviews are independent — no sponsored content, no affiliate bias.*
"""

    try:
        r = requests.post(
            "https://dev.to/api/articles",
            headers={"api-key": DEVTO_API_KEY, "Content-Type": "application/json"},
            json={"article": {
                "title": f"📊 {title} — Evidence-Based Review",
                "body_markdown": body,
                "published": True,
                "tags": ["health", "productreview", "buyerguide", "wellness"]
            }},
            timeout=30
        )
        if r.status_code == 201:
            print(f"  ✓ Dev.to: Posted — {title[:50]}")
            return True
        else:
            print(f"  ⚠ Dev.to: {r.status_code} — {r.text[:100]}")
            return False
    except Exception as e:
        print(f"  ✗ Dev.to: {e}")
        return False


# ── Reddit ──
def get_reddit_token():
    """Get Reddit OAuth token."""
    try:
        r = requests.post(
            "https://www.reddit.com/api/v1/access_token",
            auth=(REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET),
            data={"grant_type": "password",
                  "username": REDDIT_USERNAME,
                  "password": REDDIT_PASSWORD},
            headers={"User-Agent": "BioSavvyPoster/1.0"},
            timeout=30
        )
        if r.status_code == 200:
            return r.json().get("access_token")
        else:
            print(f"  ⚠ Reddit auth failed: {r.status_code}")
            return None
    except Exception as e:
        print(f"  ✗ Reddit auth: {e}")
        return None


def post_to_reddit(article, token):
    """Post article to relevant subreddits."""
    if not token:
        return False

    subreddits = [
        "BuyItForLife",
        "health",
        "Gadgets",
        "Wellness",
        "Biohackers",
    ]

    title = f"[Review] {article['title']}"
    body = (
        f"I put together an evidence-based review of {article['title'].split(' in 2026')[0].replace('Best ', '')}.\n\n"
        f"{article['description']}\n\n"
        f"We test on measurable criteria: performance, build quality, safety, and value.\n\n"
        f"Full review: {article['url']}\n\n"
        f"Site: {SITE_URL}"
    )

    posted = 0
    for sub in subreddits[:2]:  # Post to max 2 subreddits per run to avoid spam
        try:
            r = requests.post(
                "https://oauth.reddit.com/api/submit",
                headers={"Authorization": f"Bearer {token}", "User-Agent": "BioSavvyPoster/1.0"},
                data={"sr": sub, "kind": "self", "title": title, "text": body},
                timeout=30
            )
            if r.status_code == 200:
                print(f"  ✓ Reddit r/{sub}: Posted")
                posted += 1
            else:
                print(f"  ⚠ Reddit r/{sub}: {r.status_code}")
        except Exception as e:
            print(f"  ✗ Reddit r/{sub}: {e}")

    return posted > 0


# ── Main ──
def main():
    print("=" * 60)
    print("BioSavvy Multi-Platform Publisher v3")
    print(f"Time: {datetime.now().isoformat()}")
    print("=" * 60)

    articles = get_articles()
    if not articles:
        print("  ✗ No articles found")
        return

    # Get the most recent article (last in sitemap)
    latest_url = articles[-1]
    article = fetch_article(latest_url)
    if not article:
        print(f"  ✗ Could not fetch {latest_url}")
        return

    print(f"\n  📝 Latest article: {article['title'][:60]}")
    print(f"  🔗 {article['url']}\n")

    results = {}

    # Dev.to
    if DEVTO_API_KEY:
        print("[Dev.to] Posting...")
        results["Dev.to"] = post_to_devto(article)
    else:
        print("[Dev.to] Skipped — no DEVTO_API_KEY secret")

    # Reddit
    if all([REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USERNAME, REDDIT_PASSWORD]):
        print("\n[Reddit] Authenticating...")
        token = get_reddit_token()
        if token:
            results["Reddit"] = post_to_reddit(article, token)
    else:
        print("\n[Reddit] Skipped — no Reddit credentials configured")

    # Summary
    print(f"\n{'='*60}")
    print("PUBLISHING SUMMARY")
    print(f"{'='*60}")
    for platform, success in results.items():
        status = "✓" if success else "✗"
        print(f"  {status} {platform}")
    if not results:
        print("  ℹ No platforms configured — set secrets to enable")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
