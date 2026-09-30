#!/usr/bin/env python3
"""
SEO Auto-Indexer for BioSavvy
Pings search engines to request indexing of all pages.
Runs automatically via GitHub Actions on every push.

Supported:
  - Google (via Indexing API or sitemap ping)
  - Bing (via sitemap submission)
  - IndexNow (instant indexing protocol, supported by Bing + Yandex)
"""

import os
import sys
import json
import requests
from datetime import datetime

SITE_URL = "https://biosavvy.github.io"
SITEMAP_URL = f"{SITE_URL}/sitemap.xml"
SITEMAP_PAGES_URL = f"{SITE_URL}/sitemap-pages.xml"


def ping_google():
    """Ping Google with sitemap URL."""
    print("\n[Google] Pinging sitemap...")
    try:
        url = f"https://www.google.com/ping?sitemap={SITEMAP_URL}"
        r = requests.get(url, timeout=30, headers={"User-Agent": "BioSavvyBot/1.0"})
        if r.status_code == 200:
            print(f"  ✓ Google sitemap pinged successfully")
            return True
        else:
            print(f"  ⚠ Google returned {r.status_code}")
            return False
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False


def ping_bing():
    """Ping Bing with sitemap URL."""
    print("\n[Bing] Pinging sitemap...")
    try:
        url = f"https://www.bing.com/ping?sitemap={SITEMAP_URL}"
        r = requests.get(url, timeout=30, headers={"User-Agent": "BioSavvyBot/1.0"})
        if r.status_code == 200:
            print(f"  ✓ Bing sitemap pinged successfully")
            return True
        else:
            print(f"  ⚠ Bing returned {r.status_code}")
            return False
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False


def submit_indexnow():
    """Submit URLs via IndexNow protocol (instant indexing for Bing + Yandex)."""
    print("\n[IndexNow] Submitting URLs for instant indexing...")

    # IndexNow requires an API key - generate and save
    indexnow_key_file = ".github/indexnow-key.txt"
    if os.path.exists(indexnow_key_file):
        with open(indexnow_key_file) as f:
            api_key = f.read().strip()
    else:
        # Generate a random key
        import hashlib
        api_key = hashlib.md5(f"biosavvy-{datetime.now().isoformat()}".encode()).hexdigest()
        os.makedirs(os.path.dirname(indexnow_key_file), exist_ok=True)
        with open(indexnow_key_file, "w") as f:
            f.write(api_key)
        # Also need to create the key file at root for verification
        with open("indexnow-key.txt", "w") as f:
            f.write(api_key)
        print(f"  Generated new IndexNow key: {api_key[:8]}...")

    # Collect all page URLs
    urls = [SITE_URL + "/"]
    for i in range(1, 24):
        article = f"{SITE_URL}/article{i}.html"
        urls.append(article)

    # Additional pages
    urls.extend([
        f"{SITE_URL}/blog.html",
    ])

    payload = {
        "host": "biosavvy.github.io",
        "key": api_key,
        "keyLocation": f"{SITE_URL}/{api_key}.txt",
        "urlList": urls
    }

    try:
        r = requests.post(
            "https://api.indexnow.org/indexnow",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        if r.status_code == 200:
            print(f"  ✓ IndexNow submitted {len(urls)} URLs")
            return True
        elif r.status_code == 201:
            print(f"  ✓ IndexNow submitted successfully (created)")
            return True
        else:
            print(f"  ⚠ IndexNow returned {r.status_code}: {r.text[:100]}")
            return False
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False


def submit_google_indexing_api():
    """Submit URLs to Google Indexing API (requires service account)."""
    # This requires a Google Cloud service account with JSON key
    # Only works if GOOGLE_INDEXING_CREDENTIALS secret is set
    credentials_json = os.environ.get("GOOGLE_INDEXING_CREDENTIALS", "")
    if not credentials_json:
        print("\n[Google Indexing API] Skipping — no service account configured")
        print("  (Optional: set GOOGLE_INDEXING_CREDENTIALS secret for direct indexing)")
        return False

    print("\n[Google Indexing API] Submitting URLs...")
    try:
        creds = json.loads(credentials_json)
        # Would need google-auth library for proper OAuth2
        print("  ℹ Google Indexing API requires google-auth library")
        print("  Use IndexNow instead for automatic submission")
        return False
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False


def main():
    print("=" * 60)
    print("BioSavvy SEO Auto-Indexer")
    print(f"Time: {datetime.now().isoformat()}")
    print(f"Site: {SITE_URL}")
    print("=" * 60)

    results = {}

    # Core submissions
    results["Google"] = ping_google()
    results["Bing"] = ping_bing()
    results["IndexNow"] = submit_indexnow()

    # Optional: Google Indexing API
    submit_google_indexing_api()

    # Summary
    print(f"\n{'='*60}")
    print("INDEXING SUMMARY")
    print(f"{'='*60}")
    for engine, success in results.items():
        status = "✓" if success else "✗"
        print(f"  {status} {engine}")
    print(f"{'='*60}")
    print("Done!")


if __name__ == "__main__":
    main()
