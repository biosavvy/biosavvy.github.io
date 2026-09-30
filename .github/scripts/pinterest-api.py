#!/usr/bin/env python3
"""
Pinterest API Automation Script
Uses Pinterest Business API v5 to create boards and pins.

Auth modes:
  1. PINTEREST_ACCESS_TOKEN set → direct use (short-lived, 30 days)
  2. PINTEREST_CLIENT_ID + CLIENT_SECRET + REFRESH_TOKEN set → auto-refresh (long-lived)

Mode 2 is recommended for automation — it auto-refreshes tokens.
"""

import os
import sys
import json
import requests
from time import sleep
from datetime import datetime

PINTEREST_API_BASE = "https://api.pinterest.com/v5"

# Auth configuration
ACCESS_TOKEN = os.environ.get("PINTEREST_ACCESS_TOKEN", "")
CLIENT_ID = os.environ.get("PINTEREST_CLIENT_ID", "")
CLIENT_SECRET = os.environ.get("PINTEREST_CLIENT_SECRET", "")
REFRESH_TOKEN = os.environ.get("PINTEREST_REFRESH_TOKEN", "")
ACTION = os.environ.get("ACTION", "boards-and-pins")


BOARDS = [
    {
        "name": "Pain Relief & Recovery",
        "description": "Science-backed pain relief devices: back stretchers, TENS units, red light therapy, posture correctors & more"
    },
    {
        "name": "Better Sleep",
        "description": "Sleep aid devices, therapy mattresses & tools for deeper, more restful sleep"
    },
    {
        "name": "Oral Care & Dental Health",
        "description": "Water flossers, oral irrigators & dental wellness essentials"
    },
    {
        "name": "Home Health & Wellness",
        "description": "Air quality monitors, wellness products & healthy home essentials"
    },
    {
        "name": "Healthy Kitchen",
        "description": "Portable blenders, juicers & nutrition tools for healthy living"
    },
]

PINS = [
    {
        "board_name": "Pain Relief & Recovery",
        "title": "5 Best Back Stretchers of 2026 — Expert Tested & Ranked",
        "description": "Struggling with back pain? We tested the top back stretchers so you don't have to. From budget-friendly options to premium lumbar support devices — find the perfect back stretcher for your needs. 🔗 Read the full review →",
        "link": "https://biosavvy.github.io/article18.html",
        "image_url": "https://biosavvy.github.io/images/article18_1.jpg",
        "dominant_color": "#C85A17"
    },
    {
        "board_name": "Pain Relief & Recovery",
        "title": "Best TENS & EMS Muscle Stimulators 2026 — Pain Relief That Actually Works",
        "description": "TENS and EMS therapy for muscle pain, recovery & relaxation. We reviewed the top 5 devices with real testing data. Compare features, prices & effectiveness. 🔗 Full guide →",
        "link": "https://biosavvy.github.io/article19.html",
        "image_url": "https://biosavvy.github.io/images/article19_1.jpg",
        "dominant_color": "#3D5A80"
    },
    {
        "board_name": "Better Sleep",
        "title": "5 Best Sleep Aid Devices of 2026 — Fall Asleep Faster, Sleep Deeper",
        "description": "Can't sleep? These science-backed sleep aid devices actually work. From white noise machines to smart sleep trackers — we tested them all. 🔗 Read more →",
        "link": "https://biosavvy.github.io/article20.html",
        "image_url": "https://biosavvy.github.io/images/article20_1.jpg",
        "dominant_color": "#4A4E69"
    },
    {
        "board_name": "Pain Relief & Recovery",
        "title": "Best Foot Acupressure Mats 2026 — Reflexology Relief at Home",
        "description": "Ancient reflexology meets modern design. These foot acupressure mats relieve pain, reduce stress & improve circulation. 🔗 Full review →",
        "link": "https://biosavvy.github.io/article21.html",
        "image_url": "https://biosavvy.github.io/images/article21_1.jpg",
        "dominant_color": "#9B2226"
    },
    {
        "board_name": "Healthy Kitchen",
        "title": "5 Best Portable Juicers of 2026 — Fresh Juice Anywhere",
        "description": "Healthy smoothies & fresh juice on the go! We tested the top portable juicers for power, battery life & ease of cleaning. 🔗 See all picks →",
        "link": "https://biosavvy.github.io/article22.html",
        "image_url": "https://biosavvy.github.io/images/article22_1.jpg",
        "dominant_color": "#588157"
    },
    {
        "board_name": "Home Health & Wellness",
        "title": "Best Air Quality Detectors 2026 — Know What You're Breathing",
        "description": "Your home's air quality affects your health every day. These smart air quality monitors track PM2.5, CO2, VOCs & more in real-time. 🔗 Full guide →",
        "link": "https://biosavvy.github.io/article23.html",
        "image_url": "https://biosavvy.github.io/images/article23_1.jpg",
        "dominant_color": "#023047"
    },
    {
        "board_name": "Oral Care & Dental Health",
        "title": "5 Best Oral Irrigators of 2026 — Dentist-Recommended Water Flossers",
        "description": "Upgrade your oral care routine! These water flossers remove 99.9% of plaque between teeth. We tested the top models. 🔗 Read the review →",
        "link": "https://biosavvy.github.io/article16.html",
        "image_url": "https://biosavvy.github.io/images/article16_1.jpg",
        "dominant_color": "#219EBC"
    },
    {
        "board_name": "Better Sleep",
        "title": "Best Infrared Therapy Mattresses 2026 — Sleep & Heal at the Same Time",
        "description": "Infrared therapy mattresses combine deep sleep with healing infrared heat. Reduce pain, improve circulation & wake up refreshed. 🔗 Full comparison →",
        "link": "https://biosavvy.github.io/article17.html",
        "image_url": "https://biosavvy.github.io/images/article17_1.jpg",
        "dominant_color": "#9B2226"
    },
    {
        "board_name": "Pain Relief & Recovery",
        "title": "Back Stretcher Showdown: Which One Is Worth Your Money?",
        "description": "We compared 5 popular back stretchers side by side — price, comfort, durability & effectiveness. See which one came out on top. 🔗 Full comparison →",
        "link": "https://biosavvy.github.io/article18.html",
        "image_url": "https://biosavvy.github.io/images/article18_3.jpg",
        "dominant_color": "#BB3E03"
    },
    {
        "board_name": "Pain Relief & Recovery",
        "title": "Best Red Light Therapy Devices 2026 — Science-Backed Pain Relief",
        "description": "Red light therapy for pain, skin & recovery — does it work? We tested the top devices with real data. 🔗 Read more →",
        "link": "https://biosavvy.github.io/article12.html",
        "image_url": "https://biosavvy.github.io/images/article12_1.jpg",
        "dominant_color": "#E63946"
    },
    {
        "board_name": "Pain Relief & Recovery",
        "title": "5 Best Eye Massagers of 2026 — Relieve Eye Strain & Headaches",
        "description": "Screen time giving you eye strain? These eye massagers use heat, pressure & vibration to relieve tension. 🔗 Full review →",
        "link": "https://biosavvy.github.io/article13.html",
        "image_url": "https://biosavvy.github.io/images/article13_1.jpg",
        "dominant_color": "#457B9D"
    },
    {
        "board_name": "Pain Relief & Recovery",
        "title": "Best Infrared Sauna Blankets 2026 — Detox & Relax at Home",
        "description": "Get the benefits of an infrared sauna without leaving home. These sauna blankets promote detox, relaxation & pain relief. 🔗 See all picks →",
        "link": "https://biosavvy.github.io/article14.html",
        "image_url": "https://biosavvy.github.io/images/article14_1.jpg",
        "dominant_color": "#BC4749"
    },
    {
        "board_name": "Pain Relief & Recovery",
        "title": "Best Smart Posture Correctors 2026 — Fix Your Posture with Technology",
        "description": "Bad posture causing back & neck pain? Smart posture correctors use sensors & gentle reminders to train better habits. 🔗 Full guide →",
        "link": "https://biosavvy.github.io/article15.html",
        "image_url": "https://biosavvy.github.io/images/article15_1.jpg",
        "dominant_color": "#2A9D8F"
    },
]


def refresh_access_token():
    """Refresh the access token using the refresh token."""
    if not CLIENT_ID or not CLIENT_SECRET or not REFRESH_TOKEN:
        print("Cannot refresh token: missing CLIENT_ID, CLIENT_SECRET, or REFRESH_TOKEN")
        return None

    print("Refreshing access token...")
    try:
        response = requests.post(
            "https://api.pinterest.com/v5/oauth/token",
            data={
                "grant_type": "refresh_token",
                "refresh_token": REFRESH_TOKEN,
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=30
        )
        response.raise_for_status()
        data = response.json()
        new_token = data.get("access_token")
        new_refresh = data.get("refresh_token", REFRESH_TOKEN)
        expires_in = data.get("expires_in", "N/A")
        print(f"✓ Token refreshed! Expires in: {expires_in}s")
        # NOTE: The new tokens should be saved to GitHub secrets for next run
        print(f"NEW_ACCESS_TOKEN={new_token}")
        print(f"NEW_REFRESH_TOKEN={new_refresh}")
        return new_token
    except requests.exceptions.HTTPError as e:
        print(f"Token refresh failed: {e}")
        print(f"Response: {response.text[:500]}")
        return None
    except Exception as e:
        print(f"Token refresh error: {e}")
        return None


def api_request(method, endpoint, data=None, params=None, token=None):
    """Make API request to Pinterest."""
    use_token = token or ACCESS_TOKEN
    headers = {
        "Authorization": f"Bearer {use_token}",
        "Content-Type": "application/json",
    }
    url = f"{PINTEREST_API_BASE}{endpoint}"

    try:
        if method == "GET":
            response = requests.get(url, headers=headers, params=params, timeout=30)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=data, timeout=30)
        elif method == "PUT":
            response = requests.put(url, headers=headers, json=data, timeout=30)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers, timeout=30)
        else:
            raise ValueError(f"Unknown method: {method}")

        if response.status_code == 401:
            print(f"  ⚠ 401 Unauthorized on {method} {endpoint}")
            return {"_auth_error": True}

        response.raise_for_status()
        return response.json() if response.text else {}

    except requests.exceptions.HTTPError as e:
        print(f"  HTTP Error: {e}")
        print(f"  Response: {response.text[:500]}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"  Request Error: {e}")
        return None


def get_user_profile():
    """Get current user profile."""
    print("Getting user profile...")
    result = api_request("GET", "/user_account")
    if result and not result.get("_auth_error"):
        print(f"  Username: {result.get('username', 'N/A')}")
        print(f"  Account type: {result.get('account_type', 'N/A')}")
    return result


def list_boards():
    """List all boards."""
    print("\nListing boards...")
    result = api_request("GET", "/boards", params={"page_size": 100})
    if result and "items" in result:
        boards = result["items"]
        print(f"  Found {len(boards)} boards:")
        for board in boards:
            print(f"    - {board.get('name', 'N/A')} (id: {board.get('id', 'N/A')})")
        return boards
    return []


def create_board(name, description):
    """Create a new board."""
    print(f"\n  Creating board: '{name}'")
    data = {
        "name": name,
        "description": description,
    }
    result = api_request("POST", "/boards", data=data)
    if result and not result.get("_auth_error"):
        print(f"  ✓ Board created: {result.get('name')} (id: {result.get('id')})")
    return result


def create_pin(board_id, title, description, link, image_url, dominant_color="#C85A17"):
    """Create a new pin."""
    print(f"\n  Creating pin: '{title[:50]}...'")

    # Pinterest API: POST /pins with media_source
    pin_data = {
        "board_id": board_id,
        "title": title,
        "description": description,
        "link": link,
        "dominant_color": dominant_color,
        "media_source": {
            "source_type": "image_url",
            "url": image_url
        }
    }

    result = api_request("POST", "/pins", data=pin_data)
    if result and not result.get("_auth_error"):
        pin_id = result.get("id", "N/A")
        print(f"  ✓ Pin created: {pin_id}")
    return result


def test_token():
    """Test if the access token is valid."""
    print("\n--- Testing Access Token ---")
    profile = get_user_profile()
    if profile and not profile.get("_auth_error"):
        print(f"\n✓ Token is valid! Connected as: {profile.get('username')}")
        return True
    else:
        print("\n✗ Token is invalid or expired.")
        print("\nOptions to fix:")
        print("1. If you have refresh tokens, the script will try auto-refresh")
        print("2. Generate a new access token at developers.pinterest.com")
        print("3. Update PINTEREST_ACCESS_TOKEN in GitHub Secrets")
        return False


def create_boards():
    """Create all boards, skipping existing ones."""
    print("\n--- Creating Boards ---")
    existing_boards = list_boards()
    existing_names = {b.get("name", "").lower(): b for b in existing_boards}

    board_map = {}
    for board in BOARDS:
        name_lower = board["name"].lower()
        if name_lower in existing_names:
            print(f"  ✓ Already exists: {board['name']}")
            board_map[board["name"]] = existing_names[name_lower]["id"]
        else:
            result = create_board(board["name"], board["description"])
            if result and not result.get("_auth_error"):
                board_map[board["name"]] = result.get("id")
            elif result and result.get("_auth_error"):
                print("  ✗ Auth error - token may need refresh")
                return None
            sleep(1)

    print(f"\n  Boards ready: {len(board_map)}/{len(BOARDS)}")
    return board_map


def create_pins(board_map):
    """Create all pins on their respective boards."""
    print("\n--- Creating Pins ---")
    created = 0
    failed = 0

    for pin in PINS:
        board_name = pin["board_name"]
        if board_name not in board_map:
            print(f"\n  ⚠ Board not found: {board_name}")
            failed += 1
            continue

        board_id = board_map[board_name]
        result = create_pin(
            board_id=board_id,
            title=pin["title"],
            description=pin["description"],
            link=pin["link"],
            image_url=pin["image_url"],
            dominant_color=pin.get("dominant_color", "#C85A17")
        )

        if result and not result.get("_auth_error"):
            created += 1
        elif result and result.get("_auth_error"):
            print("  ✗ Auth error during pin creation")
            break
        else:
            failed += 1

        sleep(2)  # Rate limiting

    return created, failed


def main():
    """Main automation flow."""
    print("=" * 60)
    print("Pinterest API Automation")
    print(f"Time: {datetime.now().isoformat()}")
    print(f"Action: {ACTION}")
    print("=" * 60)

    # Auth setup
    if not ACCESS_TOKEN and REFRESH_TOKEN:
        print("\nAccess token not set, attempting refresh...")
        new_token = refresh_access_token()
        if new_token:
            global ACCESS_TOKEN
            ACCESS_TOKEN = new_token
        else:
            print("✗ Token refresh failed.")
            sys.exit(1)

    if not ACCESS_TOKEN:
        print("\n✗ ERROR: PINTEREST_ACCESS_TOKEN not set!")
        print("\n--- One-Time Setup Required ---")
        print("1. Go to https://developers.pinterest.com/apps/")
        print("2. Create a new app (name: BioSavvy)")
        print("3. In app settings, add scopes: boards:read, boards:write, pins:read, pins:write")
        print("4. In OAuth Settings, add redirect URI: https://localhost/callback")
        print("5. Note your App ID (Client ID) and App Secret (Client Secret)")
        print("6. Visit this URL in browser (replace YOUR_APP_ID):")
        print("   https://www.pinterest.com/oauth/?client_id=YOUR_APP_ID&redirect_uri=https://localhost/callback&response_type=code&scope=boards:read+boards:write+pins:read+pins:write")
        print("7. After authorization, copy the 'code' from the redirect URL")
        print("8. Exchange code for token (see SETUP_GUIDE.md)")
        print("9. Add to GitHub Secrets:")
        print("   PINTEREST_ACCESS_TOKEN = your access token")
        print("   PINTEREST_CLIENT_ID = your app ID")
        print("   PINTEREST_CLIENT_SECRET = your app secret")
        print("   PINTEREST_REFRESH_TOKEN = your refresh token")
        sys.exit(1)

    # Action routing
    if ACTION == "test-token":
        success = test_token()
        sys.exit(0 if success else 1)

    # Verify auth
    profile = get_user_profile()
    if not profile or profile.get("_auth_error"):
        print("\n✗ Authentication failed!")
        # Try token refresh if available
        if REFRESH_TOKEN and CLIENT_ID and CLIENT_SECRET:
            print("Attempting token refresh...")
            new_token = refresh_access_token()
            if new_token:
                ACCESS_TOKEN = new_token
                profile = get_user_profile()
                if not profile or profile.get("_auth_error"):
                    print("✗ Auth still failed after refresh")
                    sys.exit(1)
            else:
                sys.exit(1)
        else:
            sys.exit(1)

    # Create boards
    if ACTION in ("boards-only", "boards-and-pins"):
        board_map = create_boards()
        if not board_map:
            print("\n✗ Board creation failed")
            sys.exit(1)

        # Create pins
        if ACTION == "boards-and-pins":
            created, failed = create_pins(board_map)
            print(f"\n{'=' * 60}")
            print(f"Summary: {created} pins created, {failed} failed, {len(PINS)} total")
            print(f"{'=' * 60}")

    elif ACTION == "pins-only":
        # Get existing boards and map
        board_map = {}
        existing_boards = list_boards()
        board_lookup = {b.get("name", "").lower(): b for b in existing_boards}
        for board in BOARDS:
            name_lower = board["name"].lower()
            if name_lower in board_lookup:
                board_map[board["name"]] = board_lookup[name_lower]["id"]
            else:
                print(f"  ⚠ Board not found: {board['name']}")

        if not board_map:
            print("✗ No boards found. Run boards-only first.")
            sys.exit(1)

        created, failed = create_pins(board_map)
        print(f"\n{'=' * 60}")
        print(f"Summary: {created} pins created, {failed} failed, {len(PINS)} total")
        print(f"{'=' * 60}")

    print("\nDone!")


if __name__ == "__main__":
    main()
