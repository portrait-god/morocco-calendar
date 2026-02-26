# Morocco Content Calendar App: Phase 1 & 2 Development Summary

**Date:** February 2026
**Project Directory:** `/Users/shanemccormick/Documents/personal-productivity-os/morocco-calendar`

## Core Features Built in this Session
This log serves as a record of our conversation and all the features we built for the Morocco 2026 application.

### 1. The Core Application Architecture
- Initialised a Flask lightweight web-server (`app.py`).
- Built a JSON-driven database model (`calendar_data.json`) generated automatically from a Python script (`generate_calendar.py`), to allow easy editing without touching HTML.
- Implemented an `update_calendar()` API endpoint that lets the AI Agent dynamically update the JSON file in real-time when conversing with you.

### 2. The 90-Day Itinerary Engine
- Coded a generative Python loop to build a precise **90-day itinerary** from **March 11 to June 8, 2026**.
- Added an automatic "Schengen Reset" tracker that ticks down to the critical June 10th visa renewal date.
- Stored exact flight logic (LIS -> MAD -> TNG) and laid out day-by-day progression for 8 specific Moroccan cities: Tangier, Chefchaouen, Fez, Rabat, Casablanca, Taghazout, Essaouira, and Marrakech.
- Scripted an automatic **Golden Hour Calculator** that approximates sunset times based on the day of the year and Daylight Savings Time rules in Morocco, giving you tailored shooting times.

### 3. The Front-End UI Structure
- Built a sleek, dark-mode 7-column calendar grid CSS layout (`index.html`) similar to a native iOS calendar app.
- Implemented "Sticky Headers" so you always know what month you are scrolling through.
- Created expandable "Day Cards" that pop open smoothly to reveal your daily itinerary (Locations, Events, Hostels, and Social Media content plans).
- Added multi-category filter buttons (All Days, Locations, Map, Events, and Booked tabs).

### 4. Interactive Map Tab
- Integrated an interactive Leaflet.js open-source map into the "Map" tab.
- Drew a complete polyline route demonstrating your travel trajectory down the Moroccan coast and into the Atlas mountains.
- Placed interactive city markers that display the total number of days you'll spend in each hub.

### 5. Locations & Bookings (Dynamic State)
- Implemented a "Locations" checklist tab, scraping all your highly-curated off-the-beaten-path shoot targets and subculture scenes.
- Location names act as instant Google Maps search links.
- Implemented `localStorage` syncing, allowing you to check off locations in the Locations tab, and it permanently remembers your progress across sessions.
- Built a **"Booked"** tab that aggregates all of your confirmed hostel bookings from `bookings.json`.
- Wrote JavaScript to dynamically inject green "✅ Confirmed Bookings" badges directly into the specific Day Tiles on the calendar where the dates overlap. This allows you to easily see what days are covered.

### 6. Events Gallery & Image Scraping Automation
- Aggregated 36+ specific cultural events, festivals, and night markets happening precisely during your 90 days.
- Built an "Events" tab featuring a grid of clickable image cards.
- Implemented a "Click-to-Copy" (📋) interaction on the event titles for easy social media tagging.
- Automated a **Headless Chrome Web Scraper** in Python to bypass Google's 429 API limits and physically open Google Images to take massive 600x600 1:1 high-resolution screenshots of the 36 events, saving them directly into your `static/images/events/unique` folder.
- Configured day tiles so clicking an "Event" navigates to the Events tab and forcefully scrolls exactly to the matching event image card.

### 7. Deployment Readiness & Networking
- Converted the site into a Progressive Web App (PWA) with a `manifest.json`, icon rules, and an `sw.js` Service Worker so you can save it to your iPhone Home Screen and it acts like a native app.
- Updated the Flask server to broadcast on `host="0.0.0.0"` and automatically output your Local Wi-Fi IP address in the terminal, letting you open the dashboard on your phone while developing.
- Deployed the live instance to the cloud via GitHub and Render.

---

*This summary acts as a perfect reference point. Next time we spin up this project, you can provide this file to me to immediately restore all my contextual memory of how the app is engineered.*
