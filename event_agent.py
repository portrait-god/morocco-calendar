#!/usr/bin/env python3
"""
event_agent.py — Morocco Calendar Daily Event Discovery Agent

Runs nightly via cron to find new events and flyer images from:
1. Web search (via requests + BeautifulSoup)
2. Instagram public hashtag posts (via instaloader)

NEVER overwrites existing events — only appends new ones.
After updating events_gallery.json, auto-deploys via ./deploy.sh

Cron setup (runs midnight every day):
  crontab -e
  0 0 * * * /usr/bin/python3 /Users/shanemccormick/Documents/personal-productivity-os/morocco-calendar/event_agent.py >> /tmp/event_agent.log 2>&1
"""

import json
import os
import sys
import time
import hashlib
import subprocess
from datetime import datetime, timezone
from pathlib import Path

# -------------------------------------------------------------------
# Configuration
# -------------------------------------------------------------------
BASE_DIR = Path(__file__).parent
GALLERY_PATH = BASE_DIR / "static" / "events_gallery.json"
FLYERS_DIR = BASE_DIR / "static" / "event_flyers"
FLYERS_DIR.mkdir(exist_ok=True)

TRIP_START = "2026-03-11"
TRIP_END   = "2026-06-08"
TODAY      = datetime.now(timezone.utc).isoformat()

CITIES = {
    "Tangier":      {"tags": ["tangier", "tanger", "tangermaroc"], "days": range(1, 15)},
    "Chefchaouen":  {"tags": ["chefchaouen", "bluecity", "chefchaouenmorocco"], "days": range(15, 18)},
    "Fez":          {"tags": ["fezmorocco", "fesmedina", "fez2026"], "days": range(18, 27)},
    "Rabat":        {"tags": ["rabatmorocco", "rabat2026", "rabatevents"], "days": range(27, 41)},
    "Essaouira":    {"tags": ["essaouira", "essaouiramorocco", "gnaoua"], "days": range(41, 56)},
    "Marrakech":    {"tags": ["marrakech", "marrakechevent", "marrakech2026"], "days": range(56, 91)},
}

FLYER_KEYWORDS = ["event", "soirée", "festival", "concert", "nuit", "entrée", "billet", "show", "live", "party", "فعالية", "حفل"]

# -------------------------------------------------------------------
# Load existing events (to avoid overwriting)
# -------------------------------------------------------------------
def load_gallery():
    if GALLERY_PATH.exists():
        with open(GALLERY_PATH) as f:
            return json.load(f)
    return {"events": []}


def save_gallery(data):
    with open(GALLERY_PATH, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"✅ Saved {len(data['events'])} events to events_gallery.json")


def existing_ids(data):
    return {ev["id"] for ev in data["events"]}


def make_id(title, date):
    slug = f"{title}-{date}".lower().replace(" ", "-").replace("'", "")
    return hashlib.md5(slug.encode()).hexdigest()[:10]


# -------------------------------------------------------------------
# Instagram hashtag scraper using instaloader
# -------------------------------------------------------------------
def scrape_instagram_hashtag(tag, city, existing, data):
    """Download flyer images from a public Instagram hashtag."""
    try:
        import instaloader
    except ImportError:
        print("⚠️  instaloader not installed. Run: pip3 install instaloader")
        return

    L = instaloader.Instaloader(
        download_pictures=True,
        download_video_thumbnails=False,
        download_videos=False,
        save_metadata=False,
        post_metadata_txt_pattern="",
        dirname_pattern=str(FLYERS_DIR / "{target}"),
        quiet=True
    )

    print(f"🔍 Searching Instagram #{tag} for {city} event flyers...")
    try:
        hashtag = instaloader.Hashtag.from_name(L.context, tag)
        count = 0
        for post in hashtag.get_posts():
            if count >= 5:
                break  # Max 5 posts per hashtag to stay within rate limits
            time.sleep(2)  # Throttle

            caption = (post.caption or "").lower()
            is_flyer = any(kw in caption for kw in FLYER_KEYWORDS)
            if not is_flyer:
                continue

            event_id = make_id(post.shortcode, str(post.date))
            if event_id in existing:
                continue

            # Download the image
            img_filename = f"{post.shortcode}.jpg"
            img_path = FLYERS_DIR / img_filename
            try:
                L.download_pic(str(img_path), post.url, post.date)
            except Exception:
                pass

            event = {
                "id": event_id,
                "title": caption[:80].strip().title() if caption else f"Event in {city}",
                "date": post.date.strftime("%Y-%m-%d"),
                "city": city,
                "description": (post.caption or "")[:200],
                "image": f"/static/event_flyers/{img_filename}" if img_path.exists() else None,
                "link": f"https://www.instagram.com/p/{post.shortcode}/",
                "source_account": post.owner_username,
                "timestamp_added": TODAY,
            }

            data["events"].append(event)
            existing.add(event_id)
            count += 1
            print(f"  ✅ Added flyer from @{post.owner_username}: {event['title'][:50]}")

    except Exception as e:
        print(f"  ⚠️  Error scanning #{tag}: {e}")

    time.sleep(60)  # 1 minute cool-down between hashtags


# -------------------------------------------------------------------
# Web search for named events
# -------------------------------------------------------------------
def search_web_events(city, existing, data):
    """Search the web for upcoming events in a city."""
    try:
        import requests
        from bs4 import BeautifulSoup
    except ImportError:
        print("⚠️  requests/bs4 not installed. Run: pip3 install requests beautifulsoup4")
        return

    queries = [
        f"{city} Morocco events 2026",
        f"{city} festival 2026",
        f"{city} soirée concert mars avril mai 2026",
    ]

    headers = {"User-Agent": "Mozilla/5.0 (compatible; MoroccoCalendarBot/1.0)"}

    for query in queries:
        try:
            url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
            resp = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(resp.text, "html.parser")

            # Pull any visible event snippets
            for result in soup.select(".g")[:3]:
                title_el = result.select_one("h3")
                link_el = result.select_one("a")
                desc_el = result.select_one(".VwiC3b")

                if not title_el:
                    continue

                title = title_el.get_text()
                link = link_el["href"] if link_el and link_el.get("href", "").startswith("http") else None
                desc = desc_el.get_text() if desc_el else ""

                event_id = make_id(title, city)
                if event_id in existing:
                    continue

                event = {
                    "id": event_id,
                    "title": title,
                    "date": TRIP_START,  # Approximate; agent uses start of trip as fallback
                    "city": city,
                    "description": desc[:200],
                    "image": None,
                    "link": link,
                    "source_account": None,
                    "timestamp_added": TODAY,
                }
                data["events"].append(event)
                existing.add(event_id)
                print(f"  🌐 Added web event for {city}: {title[:50]}")

        except Exception as e:
            print(f"  ⚠️  Web search error for '{query}': {e}")

        time.sleep(3)


# -------------------------------------------------------------------
# Main
# -------------------------------------------------------------------
def main():
    print(f"\n🌙 Morocco Event Agent starting at {TODAY}")
    print(f"📍 Trip: {TRIP_START} → {TRIP_END}\n")

    data = load_gallery()
    existing = existing_ids(data)
    print(f"📋 Loaded {len(data['events'])} existing events (will not be overwritten)\n")

    for city, config in CITIES.items():
        print(f"\n🏙️  Scanning {city}...")

        # 1. Web search
        search_web_events(city, existing, data)

        # 2. Instagram hashtag scraping (throttled)
        for tag in config["tags"][:2]:  # Max 2 tags per city
            scrape_instagram_hashtag(tag, city, existing, data)

    save_gallery(data)

    # Auto-deploy
    print("\n🚀 Auto-deploying changes...")
    deploy_script = BASE_DIR / "deploy.sh"
    if deploy_script.exists():
        result = subprocess.run(["bash", str(deploy_script)], capture_output=True, text=True)
        print(result.stdout)
        if result.returncode != 0:
            print(f"⚠️  Deploy error: {result.stderr}")
    else:
        print("⚠️  deploy.sh not found. Skipping auto-deploy.")

    print("\n✅ Event agent complete.")


if __name__ == "__main__":
    main()
