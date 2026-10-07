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
def get_devto_existing():
    """Get list of articles already posted on Dev.to to avoid duplicates."""
    if not DEVTO_API_KEY:
        return set()
    try:
        r = requests.get(
            "https://dev.to/api/articles/me/all",
            headers={"api-key": DEVTO_API_KEY},
            params={"per_page": 100},
            timeout=30
        )
        if r.status_code == 200:
            articles = r.json()
            # Build a set of normalized titles for matching
            existing = set()
            for a in articles:
                # Store both the article ID and normalized title
                title = a["title"].lower().replace("&amp;", "&").replace("&#39;", "'").strip()
                existing.add(title)
            return existing
        else:
            print(f"  ⚠ Could not fetch Dev.to articles: {r.status_code}")
            return set()
    except Exception as e:
        print(f"  ⚠ Dev.to dedup check failed: {e}")
        return set()


def post_to_devto(article, posted_titles):
    """Post article summary to Dev.to with a health-focused, caring tone."""
    if not DEVTO_API_KEY:
        return False

    # Clean title for Dev.to post
    title = article["title"]
    for suffix in [" in 2026: Expert Reviews & Buying Guide",
                    " in 2026: Expert Reviews &amp; Buying Guide",
                    " in 2026: Tested & Ranked",
                    " in 2026: Tested &amp; Ranked"]:
        title = title.replace(suffix, "")

    # Skip if already posted (check by title)
    if title.lower() in posted_titles:
        print(f"  ⏭ Dev.to: Already posted — {title[:50]}")
        return "skipped"

    desc = article["description"].replace('&#x27;', "'").replace('&amp;', '&')

    body = f"""---
title: {title}
published: true
tags: [health, wellness, buyerguide, evidencebased]
cover_image: {article['image']}
---

选择健康产品时，最让人头疼的问题往往是：**到底哪个真的有用？**

市面上产品五花八门，宣传天花乱坠，但真正经得起推敲的有多少？我们做这些评测，就是希望帮大家少走弯路，找到真正对自己健康有帮助的东西。

## {title}

{desc}

**[查看完整评测 →]({article['url']})**

我们的评测关注这些方面：
- 🌿 成分与原理 — 这个产品靠不靠谱？有科学依据吗？
- 📊 实际表现 — 用起来效果怎么样？
- 💰 性价比 — 花的钱值不值？
- 🛡️ 安全性 — 用着放心吗？

每一篇评测我们都认真对待，希望大家能从中找到适合自己的健康好物。

*所有评测均为独立撰写，不接受商业赞助。*
"""

    try:
        r = requests.post(
            "https://dev.to/api/articles",
            headers={"api-key": DEVTO_API_KEY, "Content-Type": "application/json"},
            json={"article": {
                "title": f"{title} — 健康评测推荐",
                "body_markdown": body,
                "published": True,
                "tags": ["health", "wellness", "buyerguide", "evidencebased"]
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

    # Fetch all articles
    all_articles = []
    for url in articles:
        a = fetch_article(url)
        if a:
            all_articles.append(a)

    if not all_articles:
        print("  ✗ Could not fetch any articles")
        return

    # Reverse so oldest first (matches Dev.to chronological display)
    all_articles.reverse()

    print(f"\n  📝 Found {len(all_articles)} articles")

    results = {}

    # Dev.to — post at most 1 article per run to avoid triggering spam detection
    if DEVTO_API_KEY:
        print("\n[Dev.to] Checking existing posts...")
        posted_titles = get_devto_existing()
        print(f"  Already posted: {len(posted_titles)} articles")

        posted = 0
        for article in all_articles:
            result = post_to_devto(article, posted_titles)
            if result is True:
                posted += 1
                break  # Only 1 article per run — safe for spam detection
            elif result == "skipped":
                continue  # Already posted, try next
            else:
                break  # Failed, stop

        if posted == 0:
            # Check if all are already posted
            all_posted = all(
                post_to_devto(a, posted_titles) == "skipped"
                for a in all_articles[:3]  # Quick check, don't loop all
            )
            if all_posted:
                results["Dev.to"] = "all articles already posted"
            else:
                results["Dev.to"] = "no new articles to post this run"
        else:
            results["Dev.to"] = f"{posted} posted (safe mode: 1 per run)"
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
    for platform, result in results.items():
        if isinstance(result, str):
            print(f"  ✓ {platform}: {result}")
        else:
            status = "✓" if result else "✗"
            print(f"  {status} {platform}")
    if not results:
        print("  ℹ No platforms configured — set secrets to enable")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
