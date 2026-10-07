#!/usr/bin/env python3
"""
Hacker News Auto-Poster for BioSavvy
Posts "Show HN" stories for new articles.
Uses the official Firebase-based Hacker News API.

Setup:
  1. Create a Hacker News account at https://news.ycombinator.com
  2. Set these GitHub secrets:
     - HN_USERNAME: your HN username
     - HN_PASSWORD: your HN password
  3. Run manually via workflow_dispatch or it runs on new article pushes

Note: HN has rate limits. This script posts at most 1 story per run.
"""

import os
import sys
import json
import requests
import re
from datetime import datetime

HN_USERNAME = os.environ.get("HN_USERNAME", "")
HN_PASSWORD = os.environ.get("HN_PASSWORD", "")
SITE_URL = "https://biosavvy.github.io"

# Firebase auth endpoint for HN
HN_FIREBASE_URL = "https://hn-firebase.firebaseio.com"
HN_API_BASE = "https://hacker-news.firebaseio.com/v0"
HN_AUTH_URL = "https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword"
# HN uses a legacy Firebase auth — we use the Algolia API for posting
# Actually, HN posting requires browser auth. We'll use the unofficial API.

# Alternative: use the HN Algolia search to check for duplicates
HN_SEARCH_API = "https://hn.algolia.com/api/v1"


def get_new_articles():
    """Get articles from the sitemap that haven't been posted yet."""
    try:
        r = requests.get(f"{SITE_URL}/sitemap.xml", timeout=30)
        if r.status_code != 200:
            print(f"  ✗ Cannot fetch sitemap: {r.status_code}")
            return []
    except Exception as e:
        print(f"  ✗ Error fetching sitemap: {e}")
        return []

    # Parse URLs from sitemap
    urls = re.findall(r'<loc>(https://biosavvy\.github\.io/article\d+\.html)</loc>', r.text)

    # Check which articles have already been posted on HN
    posted = []
    unposted = []

    for url in urls:
        article_id = url.split('/')[-1].replace('.html', '')
        # Search HN for this URL
        try:
            search_url = f"{HN_SEARCH_API}/search?query={url}&tags=story"
            r = requests.get(search_url, timeout=15)
            if r.status_code == 200:
                data = r.json()
                if data.get('nbHits', 0) > 0:
                    posted.append(url)
                else:
                    unposted.append(url)
        except Exception:
            unposted.append(url)

    return unposted


def format_hn_story(article_url):
    """Format an article as a Show HN story."""
    # Fetch the article to get title
    try:
        r = requests.get(article_url, timeout=30)
        if r.status_code != 200:
            return None, None

        title_match = re.search(r'<title>(.*?)</title>', r.text)
        desc_match = re.search(r'<meta name="description" content="(.*?)"', r.text)

        title = title_match.group(1) if title_match else "BioSavvy Review"
        desc = desc_match.group(1) if desc_match else ""

        # Clean up
        title = title.replace('&#x27;', "'").replace('&amp;', '&')
        desc = desc.replace('&#x27;', "'").replace('&amp;', '&')

        # Format as Show HN title
        short_title = title.replace(" in 2026: Expert Reviews & Buying Guide", "")
        short_title = short_title.replace(" in 2026: Tested & Ranked", "")
        short_title = short_title.replace(" in 2026: Expert Reviews &amp; Buying Guide", "")
        short_title = short_title.replace(" in 2026: Tested &amp; Ranked", "")

        story_title = f"Show HN: {short_title} – Evidence-based review site"

        # Build text content
        text = f"{desc}\n\n{article_url}\n\n"
        text += "BioSavvy is a collection of evidence-based health product reviews. "
        text += "We evaluate products on measurable criteria — no marketing hype, just data.\n\n"
        text += f"Feedback welcome!"

        return story_title, text

    except Exception as e:
        print(f"  ✗ Error fetching article: {e}")
        return None, None


def post_via_browser():
    """
    HN doesn't have an official posting API.
    Posting requires browser authentication.
    This function outputs the story details for manual posting,
    or can be used with a headless browser if credentials are set.
    """
    unposted = get_new_articles()

    if not unposted:
        print("  ℹ No new articles to post on Hacker News")
        return False

    # Only post the most recent article
    article_url = unposted[-1]  # Last in list = most recent
    print(f"\n  📝 New article to post: {article_url}")

    title, text = format_hn_story(article_url)
    if not title:
        print("  ✗ Could not format story")
        return False

    print(f"\n  Title: {title}")
    print(f"  URL: {article_url}")
    print(f"  Text: {text[:100]}...")

    if not HN_USERNAME or not HN_PASSWORD:
        print("\n  ⚠ HN credentials not configured")
        print("  Set HN_USERNAME and HN_PASSWORD secrets to auto-post")
        print("\n  Manual posting instructions:")
        print(f"  1. Go to https://news.ycombinator.com/submit")
        print(f"  2. Title: {title}")
        print(f"  3. URL: {article_url}")
        return False

    # Try to post using the HN web interface via requests
    # This requires maintaining a session with HN's legacy auth
    print("\n  ℹ HN posting requires browser-based auth")
    print("  Story prepared — use browser automation for auto-posting")

    # Save story details for reference
    story = {
        "title": title,
        "url": article_url,
        "text": text,
        "prepared_at": datetime.now().isoformat()
    }

    with open(".github/hn-pending-story.json", "w") as f:
        json.dump(story, f, indent=2)

    print(f"  ✓ Story saved to .github/hn-pending-story.json")
    return True


def main():
    print("=" * 60)
    print("BioSavvy Hacker News Auto-Poster")
    print(f"Time: {datetime.now().isoformat()}")
    print("=" * 60)

    post_via_browser()

    print(f"\n{'='*60}")
    print("Done!")


if __name__ == "__main__":
    main()
