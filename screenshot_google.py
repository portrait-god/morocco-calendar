from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from PIL import Image
import time
import os
import io
import urllib.parse
import json

options = Options()
options.add_argument('--headless=new')
options.add_argument('--window-size=1200,800')
driver = webdriver.Chrome(options=options)

def get_google_image(query, safe_name):
    print(f"Searching: {query}")
    try:
        url = f"https://www.google.com/search?tbm=isch&q={urllib.parse.quote(query + ' Morocco high quality free photography')}"
        driver.get(url)
        time.sleep(2) # Wait for images to load
        
        # Accept cookies if prompted (Google EU dialog)
        try:
            btn = driver.find_element(By.XPATH, "//button[.//div[text()='Accept all']]")
            btn.click()
            time.sleep(1)
        except:
            pass

        # Find the first image result thumbnail
        img_element = driver.find_element(By.CSS_SELECTOR, "img.YQ4gaf")
        
        # Download the base64 or src
        src = img_element.get_attribute('src')
        if src and src.startswith('data:image'):
            import base64
            head, data = src.split(',', 1)
            img_data = base64.b64decode(data)
            img = Image.open(io.BytesIO(img_data))
        else:
            # Fallback to screenshotting the element itself
            png = img_element.screenshot_as_png
            img = Image.open(io.BytesIO(png))

        # Crop to square
        w, h = img.size
        s = min(w, h)
        img = img.crop(((w-s)//2, (h-s)//2, (w+s)//2, (h+s)//2))
        img = img.resize((300, 300), Image.Resampling.LANCZOS)
        img = img.convert('RGB')
        
        path = f"static/images/events/{safe_name}.jpg"
        img.save(path, quality=85)
        print(f"Saved {path}")
        return f"/{path}"
    except Exception as e:
        print(f"Failed {safe_name}: {e}")
        return None

# Load events to find what's still missing/generic
with open('static/events_gallery.json', 'r') as f:
    events = json.load(f)

for ev in events['events']:
    img_path = ev.get('image', '')
    
    # Check if it was one of the failed unsplash downloads or still generic
    failed_unsplash = ["surf_bonfire.jpg", "artisan.jpg", "marathon.jpg", "horses.jpg"]
    is_failed = any(f in img_path for f in failed_unsplash)
    
    is_generic = img_path in [
        '/static/icons/icon-512.png', 
        '/static/images/events/tangier.jpg', 
        '/static/images/events/jazz.jpg', 
        '/static/images/events/biennale.jpg', 
        '/static/images/events/eid.jpg', 
        '/static/images/events/surf.jpg',
        '/static/images/events/rose.jpg',
        '/static/images/events/music.jpg' # The generic catch-all we just added
    ]
    
    # Don't touch our safe ones
    is_safe = "tap_in_soiree" in img_path or "fes" in img_path or "chefchaouen" in img_path or "eid" in ev['title'].lower() or "biennale" in ev['title'].lower() or "rose" in ev['title'].lower() or "mawazine" in ev['title'].lower() or "jazzablanca" in img_path or "kitesurf" in img_path or "skate" in img_path or "cherry" in img_path or "story" in img_path or "surf_jam" in img_path or "night_market" in img_path
    
    if (is_generic or is_failed) and not is_safe:
        res = get_google_image(ev['title'], ev['id'])
        if res:
            ev['image'] = res

with open('static/events_gallery.json', 'w') as f:
    json.dump(events, f, indent=2)

driver.quit()
print("Screenshot scraping complete!")
